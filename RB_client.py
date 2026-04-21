import socket
import json
from datetime import datetime
import time
import base64
import os

serverIP = '10.245.30.236'
serverPort = 5002
buffersize = 1024

client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)


messages=["Hello!", "This is a Test", "Howdy server, its Alice"]
seq_num = 1

try:
    client.connect((serverIP, serverPort))
    print(f"Connected to {serverIP}:{serverPort}")
    
    
    for msg in messages:
        for i in range(100):
            payload={
                "seq": seq_num,
                "content": "NORMAL",
                "message": msg,
                "sent_at": datetime.now().isoformat()
            }
        
    
            client.sendto(json.dumps(payload).encode(), (serverIP, serverPort))
            seq_num += 1 
            print(f"Sent text packet {i+1}: {msg}")
            time.sleep(0.1)


            
    #image_path = "/home/raspalice/Documents/raspberry_logo.png"
    #ext = os.path.splitext(image_path)[1]
    
    #with open(image_path, "rb") as f:
     #   image_bytes = f.read()
        
    #img_b64 = base64.b64encode(image_bytes).decode()
    
    #chunk_size = 2000
    #total_chunks = (len(img_b64) // chunk_size)+1
    
    #print(f"Sending B64 image in {total_chunks} chunks...")
    
    #for chunk_id in range(total_chunks):
     #   chunk = img_b64[chunk_id * chunk_size : (chunk_id + 1)*chunk_size]
    
      #  payload = {
       #     "seq": seq_num, 
        #    "content": "IMAGE_B64",
         #   "ext": ext,
          #  "chunk_id": chunk_id,
           # "total_chunks": total_chunks,
           # "data": chunk,
           # "sent_at": datetime.now().isoformat()
        #}
    
        #client.sendto(json.dumps(payload).encode(), (serverIP, serverPort))
        #seq_num += 1
        #print(f"Sent chunk {chunk_id+1}/{total_chunks}")
        #time.sleep(0.1)
    


except Exception as e:
    print(f"Error when sedning: {e}")
    
finally:
    
    done_payload = {
        "seq": seq_num - 1,
        "content": "DONE",
        "message": "end",
        "sent_at": datetime.now().isoformat()
    }

    client.sendto(json.dumps(done_payload).encode(), (serverIP, serverPort))
    print(f"All packets sent. Last packet was {seq_num - 1}")
    client.close()
    print("Client closing...")
    
    
    
    