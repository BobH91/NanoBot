#!/usr/bin/env python3
"""
tcp_server.py — Nanobot TCP command server (RPi 5)
Listens on 0.0.0.0:9000 for JSON drive commands from the Orin Nano.

Protocol (newline-delimited JSON, one object per line):
  Drive:   {"cmd": "drive", "throttle": 0.5, "steering": 0.0}
  Stop:    {"cmd": "stop"}
  E-Stop:  {"cmd": "estop"}
  Ping:    {"cmd": "ping"}
  Quit:    {"cmd": "quit"}

Response (always one JSON line back):
  {"status": "ok"}
  {"status": "error", "msg": "..."}
  {"status": "pong"}
"""

import json
import logging
import signal
import socket
import sys
import threading
import time

from drive import get_driver, shutdown_driver

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
HOST          = "0.0.0.0"
PORT          = 9000
BACKLOG       = 1           # only one client (the Nano) expected
RECV_BUF      = 4096
WATCHDOG_SEC  = 1.0         # stop motors if no valid command within this window
LOG_LEVEL     = logging.INFO

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/home/pi/nanobot/logs/tcp_server.log"),
    ],
)
log = logging.getLogger("tcp_server")

# ──────────────────────────────────────────────
# Watchdog — stops motors if client goes silent
# ──────────────────────────────────────────────
class Watchdog:
    def __init__(self, timeout: float):
        self._timeout  = timeout
        self._last_pet = time.monotonic()
        self._lock     = threading.Lock()
        self._running  = True
        self._thread   = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def pet(self):
        with self._lock:
            self._last_pet = time.monotonic()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            time.sleep(0.1)
            with self._lock:
                age = time.monotonic() - self._last_pet
            if age > self._timeout:
                drv = get_driver()
                drv.stop()   # ramp to zero (not hard estop)


# ──────────────────────────────────────────────
# Command dispatcher
# ──────────────────────────────────────────────
def dispatch(obj: dict) -> dict:
    cmd = obj.get("cmd", "").lower()
    drv = get_driver()

    if cmd == "drive":
        throttle = float(obj.get("throttle", 0.0))
        steering = float(obj.get("steering", 0.0))
        log.info("DRIVE: throttle=%.3f steering=%.3f", throttle, steering)
        drv.set(throttle=throttle, steering=steering)
        return {"status": "ok"}

    elif cmd == "stop":
        drv.stop()
        return {"status": "ok"}

    elif cmd == "estop":
        drv.estop()
        log.warning("E-STOP received")
        return {"status": "ok"}

    elif cmd == "ping":
        return {"status": "pong"}

    elif cmd == "quit":
        drv.stop()
        return {"status": "ok", "msg": "bye"}

    else:
        return {"status": "error", "msg": f"unknown cmd: {cmd!r}"}


# ──────────────────────────────────────────────
# Client handler (one thread per connection)
# ──────────────────────────────────────────────
def handle_client(conn: socket.socket, addr: tuple, watchdog: Watchdog):
    log.info("Client connected: %s:%d", *addr)
    buf = ""
    try:
        conn.settimeout(2.0)
        while True:
            try:
                chunk = conn.recv(RECV_BUF)
            except socket.timeout:
                # No data — watchdog will handle stale connection
                continue

            if not chunk:
                log.info("Client disconnected: %s:%d", *addr)
                break

            buf += chunk.decode("utf-8", errors="replace")

            # Process all complete newline-delimited messages
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    log.warning("Bad JSON from %s: %s", addr, exc)
                    resp = {"status": "error", "msg": "invalid JSON"}
                    conn.sendall((json.dumps(resp) + "\n").encode())
                    continue

                watchdog.pet()

                try:
                    resp = dispatch(obj)
                except Exception as exc:
                    log.error("Dispatch error: %s", exc)
                    resp = {"status": "error", "msg": str(exc)}

                conn.sendall((json.dumps(resp) + "\n").encode())

                if obj.get("cmd") == "quit":
                    return

    except Exception as exc:
        log.error("Client handler exception: %s", exc)
    finally:
        conn.close()
        get_driver().stop()
        log.info("Client handler closed for %s:%d", *addr)


# ──────────────────────────────────────────────
# Main server loop
# ──────────────────────────────────────────────
def run_server():
    watchdog = Watchdog(WATCHDOG_SEC)

    # Pre-init the driver so first command has no startup lag
    log.info("Initialising motor driver …")
    get_driver()
    log.info("Motor driver ready.")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(BACKLOG)
    log.info("Listening on %s:%d", HOST, PORT)

    # Graceful shutdown on SIGINT / SIGTERM
    def _shutdown(sig, _frame):
        log.info("Signal %d — shutting down.", sig)
        watchdog.stop()
        shutdown_driver()
        server.close()
        sys.exit(0)

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        try:
            conn, addr = server.accept()
        except OSError:
            break   # server socket closed by signal handler

        t = threading.Thread(
            target=handle_client,
            args=(conn, addr, watchdog),
            daemon=True,
        )
        t.start()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    run_server()
