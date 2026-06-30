from shared.discovery.discovery import broadcast_controller
import threading
import socket
import json

PORT = 5050

clients = []

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(10)

    print("[Controller] TCP server running on 5050")

    while True:
        conn, addr = s.accept()
        data = conn.recv(4096).decode()

        try:
            msg = json.loads(data)
            handle_message(msg)
        except Exception as e:
            print("[ERROR]", e)

        conn.close()

def handle_message(msg):
    print("[BUS EVENT]", msg)

    # ROUTING LOGIC
    if msg.get("type") == "heartbeat":
        return

    if msg.get("type") == "event":
        print("[EVENT]", msg)

    if msg.get("type") == "command_ack":
        print("[ACK FROM NODE]", msg)

def command(node, cmd, data=None):
    message = {
        "from": "controller",
        "to": node,
        "type": "command",
        "cmd": cmd,
        "data": data or {}
    }

    print("[SEND]", message)

    # For now: direct connect (simple v8.2 version)
    import socket
    s = socket.socket()
    s.connect(("127.0.0.1", 5050))
    s.send(json.dumps(message).encode())
    s.close()

def main():
    print("Controller starting...")

    threading.Thread(target=broadcast_controller, daemon=True).start()
    threading.Thread(target=tcp_server, daemon=True).start()

    # TEST COMMAND LOOP
    import time
    while True:
        time.sleep(10)
        command("pi", "move", {"direction": "forward", "speed": 0.3})

if __name__ == "__main__":
    main()
