# deniyorum
import json

def create_packet(msg_type, content, sender="Peer"):
    packet = {
        "type": msg_type,      
        "content": content,    
        "sender": sender       
    }
    return json.dumps(packet).encode('utf-8')

def parse_packet(raw_bytes):
    try:
        json_str = raw_bytes.decode('utf-8')
        return json.loads(json_str)
    except Exception:
        return {"type": "ERROR", "content": "Invalid format ", "sender": "System"}