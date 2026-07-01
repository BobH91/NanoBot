import socket
import threading
import json
import time
import uuid

from shared.protocol.v83_protocol import (
    create_command,
    is_ack,
    is_result
)

PORT = 5050

clients = []

pending = {}
lock = threading.Lock()

ACK_TIMEOUT = 5


# -----------------------
# SERVER
# -----------------------

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(10)

    print("[v8.3 Controller] TCP running on 5050")

    while True:
        conn, addr = s.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


# -----------------------
# CLIENT HANDLER
# -----------------------

def handle_client(conn):
    buffer = ""

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                raw, buffer = buffer.split("\n", 1)
                msg = json.loads(raw)
                route(msg)

        except Exception as e:
            print("[ERROR]", e)
            break


# -----------------------
# ROUTER
# -----------------------

def route(msg):
    if is_ack(msg):
        cid = msg["command_id"]
        with lock:
            if cid in pending:
                pending[cid]["ack"] = True
                pending[cid]["ack_time"] = time.time()
        print("[ACK]", cid)
        return

    if is_result(msg):
        cid = msg["command_id"]
        with lock:
            if cid in pending:
                pending[cid]["done"] = True
                pending[cid]["result"] = msg
        print("[RESULT]", cid)
        return

    if msg.get("type") == "heartbeat":
        print("[HEARTBEAT]", msg)
        return

    print("[MSG]", msg)


# -----------------------
# SEND COMMAND
# -----------------------

def send(conn, action, payload):
    cmd = create_command(action, payload, True)
    cid = cmd["command_id"]

    with lock:
        pending[cid] = {
            "sent": time.time(),
            "ack": False,
            "done": False
        }

    conn.send((json.dumps(cmd) + "\n").encode())
    print("[SEND]", action, cid)


# -----------------------
# WATCHDOG
# -----------------------

def watchdog():
    while True:
        time.sleep(1)
        now = time.time()

        with lock:
            for cid in list(pending.keys()):
                p = pending[cid]

                if not p["ack"] and now - p["sent"] > ACK_TIMEOUT:
                    print("[TIMEOUT]", cid)

                if p.get("done"):
                    print("[COMPLETE]", cid)
                    del pending[cid]


# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()

    while True:
        time.sleep(10)
        if clients:
            send(clients[0], "move", {"direction": "forward", "speed": 0.5})
