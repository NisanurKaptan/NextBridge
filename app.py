import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.networking.server import P2PServer
from app.networking.client import P2PClient

def main():
    print("--- NEXTBRIDGE ---")
    try:
        my_port = int(input("Enter your own listening port: "))
    except ValueError:
        print("Invalid port!")
        return

    server = P2PServer('127.0.0.1', my_port)
    server.start()
    
    time.sleep(0.5)

    client = P2PClient()

    choice = input("\nDo you want to connect to a peer? (y/n): ").strip().lower()
    
    if choice == 'y':
        try:
            target_port = int(input("Peer port to connect to: "))
            client.connect_to_peer('127.0.0.1', target_port, my_port)
        except ValueError:
            print("Invalid port.")

    print("\n[System] Ready! Type a message and press Enter. To exit, type 'exit'.\n")
    print("[System] To send a file, type: /file FILE_PATH")
    while True:
        try:
            msg = input("> ").strip()
            if msg.lower() == 'exit':
                break
            
            if msg.startswith("/file "):
                file_path = msg.replace("/file ", "").strip()
                client.send_file(file_path)
            elif msg:
                client.send_chat_message(msg)
                
        except KeyboardInterrupt:
            break
    while True:
        try:
            msg = input("> ")
            if msg.lower() == 'exit':
                break
            if msg.strip():
                client.send_chat_message(msg)
        except KeyboardInterrupt:
            break

    print("\n[System] closing down...")
    server.stop()
    client.disconnect()

if __name__ == "__main__":
    main()