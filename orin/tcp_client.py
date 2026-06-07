
"""
tcp_client.py — Nanobot TCP drive command client (Orin Nano)
Connects to tcp_server.py on the RPi (192.168.4.153:9000) and sends
newline-delimited JSON drive commands.

Used by webrtc_server.py — import and call:
    client = get_client()
    client.drive(throttle=0.5, steering=0.0)
    client.stop()
    client.estop()
"""

import json
import logging
import socket
import sys
import threading
import time

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
RPI_HOST        = "192.168.4.153"
RPI_PORT        = 9000
CONNECT_TIMEOUT = 3.0       # seconds to wait for TCP connect
RECV_TIMEOUT    = 2.0       # seconds to wait for response
RECONNECT_DELAY = 1.0       # seconds between reconnect attempts
SEND_INTERVAL   = 0.05      # minimum seconds between drive commands (20 Hz cap)
LOG_LEVEL       = logging.INFO

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("tcp_client")


# ──────────────────────────────────────────────
# Client
# ──────────────────────────────────────────────
class DriveClient:
    """
    Persistent TCP client that sends drive commands to the RPi.

    Automatically reconnects if the connection drops.
    Commands are rate-limited to SEND_INTERVAL to avoid flooding.
    A background keepalive thread sends pings when idle.
    """

    def __init__(self, host: str = RPI_HOST, port: int = RPI_PORT):
        self._host      = host
        self._port      = port
        self._sock: socket.socket | None = None
        self._lock      = threading.Lock()
        self._connected = False

        # Rate limiting
        self._last_send = 0.0

        # Keepalive
        self._running        = True
        self._last_activity  = time.monotonic()
        self._keepalive_thread = threading.Thread(
            target=self._keepalive_loop, daemon=True
        )
        self._keepalive_thread.start()

        # Connect immediately
        self._connect()

    # ── Public API ──────────────────────────────

    def drive(self, throttle: float, steering: float) -> bool:
        """
        Send a drive command.
        throttle : -1.0 … +1.0  (+1 = forward)
        steering : -1.0 … +1.0  (+1 = right)
        Returns True on success.
        """
        # Rate limit
        now = time.monotonic()
        if now - self._last_send < SEND_INTERVAL:
            return True
        self._last_send = now

        return self._send({"cmd": "drive",
                           "throttle": round(throttle, 4),
                           "steering": round(steering, 4)})

    def stop(self) -> bool:
        """Ramp motors to zero."""
        return self._send({"cmd": "stop"})

    def estop(self) -> bool:
        """Immediate hardware stop — bypasses ramp."""
        return self._send({"cmd": "estop"})

    def ping(self) -> bool:
        """Returns True if RPi responds with pong."""
        resp = self._send_recv({"cmd": "ping"})
        return resp is not None and resp.get("status") == "pong"

    def is_connected(self) -> bool:
        return self._connected

    def close(self) -> None:
        self._running = False
        self._keepalive_thread.join(timeout=2.0)
        with self._lock:
            self._disconnect()

    # ── Internal ────────────────────────────────

    def _connect(self) -> bool:
        with self._lock:
            if self._connected:
                return True
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(CONNECT_TIMEOUT)
                sock.connect((self._host, self._port))
                sock.settimeout(RECV_TIMEOUT)
                self._sock      = sock
                self._connected = True
                log.info("Connected to RPi %s:%d", self._host, self._port)
                return True
            except OSError as exc:
                log.warning("Connect failed: %s — retrying in %.1fs",
                            exc, RECONNECT_DELAY)
                self._connected = False
                return False

    def _disconnect(self) -> None:
        """Must be called with self._lock held."""
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self._connected = False

    def _send(self, obj: dict) -> bool:
        """Fire-and-forget send; reads and discards the response."""
        self._send_recv(obj)
        return self._connected

    def _send_recv(self, obj: dict) -> dict | None:
        """Send a command and return the parsed response, or None on error."""
        if not self._connected:
            self._connect()

        payload = (json.dumps(obj) + "\n").encode()

        with self._lock:
            if not self._connected:
                return None
            try:
                self._sock.sendall(payload)
                raw = self._sock.recv(4096)
                if not raw:
                    raise ConnectionResetError("Server closed connection")
                resp = json.loads(raw.decode().strip())
                self._last_activity = time.monotonic()
                return resp
            except (OSError, json.JSONDecodeError, ConnectionResetError) as exc:
                log.warning("Send/recv error: %s — reconnecting …", exc)
                self._disconnect()
                return None

    def _keepalive_loop(self) -> None:
        """Ping the RPi when idle; reconnect if disconnected."""
        while self._running:
            time.sleep(0.5)
            if not self._connected:
                self._connect()
                continue
            # Ping if no activity for 2 seconds
            if time.monotonic() - self._last_activity > 2.0:
                ok = self.ping()
                if not ok:
                    log.warning("Keepalive ping failed.")

    # ── Context manager ──────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ──────────────────────────────────────────────
# Singleton (used by webrtc_server.py)
# ──────────────────────────────────────────────
_client: DriveClient | None = None
_client_lock = threading.Lock()


def get_client() -> DriveClient:
    global _client
    with _client_lock:
        if _client is None:
            _client = DriveClient()
    return _client


def shutdown_client() -> None:
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None


# ──────────────────────────────────────────────
# CLI smoke test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Nanobot tcp_client.py — smoke test → {RPI_HOST}:{RPI_PORT}")

    with DriveClient() as client:

        print("  Ping …")
        if client.ping():
            print("  ✓ pong received")
        else:
            print("  ✗ no response — is tcp_server.py running on the RPi?")
            sys.exit(1)

        print("  Sending forward 30% for 2 s …")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            client.drive(throttle=0.3, steering=0.0)
            time.sleep(SEND_INTERVAL)

        print("  Stop …")
        client.stop()
        time.sleep(0.5)

        print("  E-STOP …")
        client.estop()
        time.sleep(0.3)

    print("Done.")
    sys.exit(0)
