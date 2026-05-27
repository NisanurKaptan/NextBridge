import socket
import threading
import os
from app.networking.protocol import parse_packet

class P2PServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_running = True

    def start(self):
        self.server_sock.bind(('0.0.0.0', self.port))
        self.server_sock.listen(5)
        print(f"[Server] {self.port} Open to connections...")
        
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def _accept_connections(self):
        while self.is_running:
            try:
                conn, addr = self.server_sock.accept()
                print(f"\n[Server] {addr} A new peer has connected from this address.!")
                threading.Thread(target=self._listen_peer, args=(conn,), daemon=True).start()
            except Exception:
                break

    def _listen_peer(self, conn):
        save_dir = "received_files"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        while self.is_running:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                
                if data.startswith(b"FILE_START:"):
                    header_parts = data.decode('utf-8').split(":")
                    file_name = header_parts[1]
                    file_size = int(header_parts[2])
                    
                    file_path = os.path.join(save_dir, file_name)
                    print(f"\n[Server] File import begins: {file_name} ({file_size} byte)...")
                    
                    with open(file_path, "wb") as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = conn.recv(4096)
                            if b"FILE_END" in chunk:
                                chunk = chunk.replace(b"FILE_END", b'')
                                f.write(chunk)
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                            
                    print(f"[Server] The file was successfully retrieved and saved here: {file_path}")
                    print("> ", end="")
                    continue

                packet = parse_packet(data)
                if packet["type"] == "CHAT":
                    print(f"\n[{packet['sender']}]: {packet['content']}")
                    print("> ", end="")
            except Exception as e:
                print(f"\n[Server error] Listening stopped: {e}")
                break
        conn.close()

    def stop(self):
        self.is_running = False
        self.server_sock.close()