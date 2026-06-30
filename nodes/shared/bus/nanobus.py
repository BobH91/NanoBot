import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5050

clients = []

def handle(conn, addr):
    print(f"[NanoBus] connected: {addr}")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            msg = json.loads(data)
            print("[EVENT]", msg)

            # broadcast
            for c in clients:
                if c != conn:
                    c.sendall(json.dumps(msg).encode())

        except:
            break

    conn.close()

def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(10)

    print(f"[NanoBus] running on {PORT}")

    while True:
        conn, addr = s.accept()
        clients.append(conn)
        threading.Thread(target=handle, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
