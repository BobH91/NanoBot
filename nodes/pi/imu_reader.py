#!/usr/bin/env python3
"""
NanoBot Pi IMU reader.

Reads SparkFun 9DoF D21 YPR records over USB serial.
Reports the latest valid reading as JSON once per second.

This process is read-only with respect to robot control:
it does not issue motor commands or communicate with the motor driver.
"""

import argparse
import json
import math
import signal
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone

import serial


DEFAULT_PORT = "/dev/serial/by-id/usb-SparkFun_SFE_9DOF-D21-if00"
DEFAULT_BAUD = 115200
DEFAULT_STALE_AFTER = 0.5
DEFAULT_REPORT_INTERVAL = 1.0
SERIAL_TIMEOUT = 0.25
RECONNECT_DELAY = 2.0

running = True


def stop_handler(_signum, _frame):
    global running
    running = False


def parse_ypr(line):
    """Return (yaw, pitch, roll), or None for an invalid record."""
    if not line.startswith("#YPR="):
        return None

    try:
        values = [float(value) for value in line[5:].split(",")]
    except ValueError:
        return None

    if len(values) != 3 or not all(math.isfinite(v) for v in values):
        return None

    return tuple(values)


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def make_report(latest, stale_after):
    """Build a health-aware JSON snapshot."""
    now = time.monotonic()

    if latest is None:
        return {
            "timestamp_utc": utc_timestamp(),
            "healthy": False,
            "reason": "no_valid_reading",
            "yaw": None,
            "pitch": None,
            "roll": None,
            "age_ms": None,
        }

    yaw, pitch, roll, received_at, timestamp = latest
    age = now - received_at
    healthy = age <= stale_after

    return {
        "timestamp_utc": timestamp,
        "healthy": healthy,
        "reason": "ok" if healthy else "stale_data",
        "yaw": yaw,
        "pitch": pitch,
        "roll": roll,
        "age_ms": round(age * 1000, 1),
    }


def report(latest, stale_after):
    print(json.dumps(make_report(latest, stale_after)), flush=True)


class IMURequestHandler(BaseHTTPRequestHandler):
    latest_state = None
    latest_lock = None
    stale_after = DEFAULT_STALE_AFTER
    allowed_origin = "http://192.168.4.90:8080"
    allowed_client = "192.168.4.90"

    def log_message(self, _format, *_args):
        pass

    def _send_json(self, status, payload, origin=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/imu":
            self._send_json(404, {"error": "not_found"})
            return

        if self.client_address[0] != self.allowed_client:
            self._send_json(403, {"error": "client_not_allowed"})
            return

        origin = self.headers.get("Origin")
        if origin and origin != self.allowed_origin:
            self._send_json(403, {"error": "origin_not_allowed"})
            return

        with self.latest_lock:
            latest = self.latest_state["latest"]

        self._send_json(
            200,
            make_report(latest, self.stale_after),
            origin=origin,
        )

    def do_OPTIONS(self):
        origin = self.headers.get("Origin")
        if origin != self.allowed_origin:
            self._send_json(403, {"error": "origin_not_allowed"})
            return

        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Vary", "Origin")
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="NanoBot SparkFun IMU reader")
    parser.add_argument("--port", default=DEFAULT_PORT)
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--stale-after", type=float, default=DEFAULT_STALE_AFTER)
    parser.add_argument("--report-interval", type=float, default=DEFAULT_REPORT_INTERVAL)
    parser.add_argument("--http", action="store_true", help="Enable read-only HTTP endpoint")
    parser.add_argument("--http-host", default="0.0.0.0")
    parser.add_argument("--http-port", type=int, default=9001)
    parser.add_argument("--allowed-origin", default="http://192.168.4.90:8080")
    parser.add_argument("--allowed-client", default="192.168.4.90")
    args = parser.parse_args()

    if args.stale_after <= 0 or args.report_interval <= 0:
        parser.error("--stale-after and --report-interval must be positive")

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    latest = None
    latest_state = {"latest": None}
    latest_lock = threading.Lock()
    http_server = None

    if args.http:
        IMURequestHandler.latest_state = latest_state
        IMURequestHandler.latest_lock = latest_lock
        IMURequestHandler.stale_after = args.stale_after
        IMURequestHandler.allowed_origin = args.allowed_origin
        IMURequestHandler.allowed_client = args.allowed_client

        http_server = ThreadingHTTPServer(
            (args.http_host, args.http_port),
            IMURequestHandler,
        )
        http_thread = threading.Thread(
            target=http_server.serve_forever,
            daemon=True,
        )
        http_thread.start()
        print(
            f"IMU HTTP endpoint listening on {args.http_host}:{args.http_port}/imu",
            file=sys.stderr,
            flush=True,
        )

    next_report = time.monotonic()

    print(
        f"IMU reader starting: port={args.port}, baud={args.baud}",
        file=sys.stderr,
        flush=True,
    )

    while running:
        try:
            with serial.Serial(
                args.port,
                args.baud,
                timeout=SERIAL_TIMEOUT,
            ) as imu:
                print("IMU serial connection opened.", file=sys.stderr, flush=True)

                while running:
                    raw = imu.readline()

                    if raw:
                        line = raw.decode("utf-8", errors="replace").strip()
                        values = parse_ypr(line)

                        if values is not None:
                            latest = (
                                *values,
                                time.monotonic(),
                                utc_timestamp(),
                            )
                            with latest_lock:
                                latest_state["latest"] = latest

                    now = time.monotonic()
                    if now >= next_report:
                        report(latest, args.stale_after)
                        next_report = now + args.report_interval

        except (serial.SerialException, OSError) as exc:
            print(
                f"IMU serial error: {exc}; retrying in {RECONNECT_DELAY}s.",
                file=sys.stderr,
                flush=True,
            )
            if running:
                time.sleep(RECONNECT_DELAY)

    if http_server is not None:
        http_server.shutdown()
        http_server.server_close()

    print("IMU reader stopped.", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
