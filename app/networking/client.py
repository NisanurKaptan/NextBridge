import socket
from app.networking.protocol import create_packet

class P2PClient:
    def __init__(self):
        self.client_sock = None
        self.my_port = None

    def connect_to_peer(self, host, target_port, my_port):
        self.my_port = my_port
        try:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((host, target_port))
            print(f"[Client] {target_port} connection succeeded.")
            return True
        except Exception as e:
            print(f"[Client error] No connection: {e}")
            return False

    def send_chat_message(self, message):
        if self.client_sock:
            try:
                packet = create_packet(msg_type="CHAT", content=message, sender=f"Peer-{self.my_port}")
                self.client_sock.send(packet)
            except Exception as e:
                print(f"[Client error] Message couldn't send: {e}")
        else:
            print("[Client error] No connection")

    def disconnect(self):
        if self.client_sock:
            self.client_sock.close()

    def send_file(self, file_path):
        if not self.client_sock:
            print("[Client error] No active connection!")
            return

        import os
        if not os.path.exists(file_path):
            print("[Client error] No file!")
            return

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        try:
            header = f"FILE_START:{file_name}:{file_size}".encode('utf-8')
            self.client_sock.send(header)
            
            import time
            time.sleep(0.1)

            print(f"[Client] '{file_name}' sending ({file_size} byte)...")
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(4096) 
                    if not chunk:
                        break
                    self.client_sock.sendall(chunk) 
            
            time.sleep(0.1)
            self.client_sock.send("FILE_END".encode('utf-8'))
            print("[Client] File submission completed!")

        except Exception as e:
            print(f"[Client error] Error occurred while sending the file.: {e}")