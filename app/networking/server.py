import socket
import threading
from app.networking.protocol import parse_packet

class P2PServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_running = True

    def start(self):
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(5)
        print(f"[Server] {self.port} Started")
        
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def _accept_connections(self):
        while self.is_running:
            try:
                conn, addr = self.server_sock.accept()
                print(f"\n[Server] {addr} A new peer has connected from this address!")
                threading.Thread(target=self._listen_peer, args=(conn,), daemon=True).start()
            except Exception:
                break

    def _listen_peer(self, conn):
        while self.is_running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                
                packet = parse_packet(data)
                
                if packet["type"] == "CHAT":
                    print(f"\n[{packet['sender']}]: {packet['content']}")
                    print("> ", end="")
            except Exception:
                break
        conn.close()

    def stop(self):
        self.is_running = False
        self.server_sock.close()