import socket
import json
import threading
import time

DISCOVERY_PORT = 50000
CONTROLLER_PORT = 5050

ROLE = "unknown"

# -----------------------------
# BROADCAST CONTROLLER (LENOVO ONLY)
# -----------------------------
def broadcast_controller():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    msg = json.dumps({
        "type": "controller_announce",
        "host": get_local_ip(),
        "port": CONTROLLER_PORT
    }).encode()

    while True:
        s.sendto(msg, ("255.255.255.255", DISCOVERY_PORT))
        time.sleep(2)

# -----------------------------
# LISTEN FOR CONTROLLER (PI / ORIN)
# -----------------------------
def listen_for_controller(callback):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", DISCOVERY_PORT))

    while True:
        data, _ = s.recvfrom(1024)
        msg = json.loads(data.decode())

        if msg.get("type") == "controller_announce":
            callback(msg)

# -----------------------------
# GET LOCAL IP
# -----------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
