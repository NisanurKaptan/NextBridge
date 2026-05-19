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