##PC1 as server

import socket
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt
import base64
import time



# -----------------------------
# Defining variables
# -----------------------------

SET_Loop_time_limit = 10
BUFFER_SIZE = 4096
IP_ADDRESS = '10.245.30.236'
PORT_NUM = 5002
TOTAL_PACKETS_SENT = 300

packet_id = 1
results = []

last_seq_num = 0
seq_lost = 0
seq_received = 0
total_sent_by_client = None
attacker_packet_count = 0      

b64_chunks = {}
expected_chunks = None
image_ext = ".png"

total_bytes = 0
normal_bytes = 0
start_time_troughput = None

start_time = datetime.now()
t_end_loop = time.time() + SET_Loop_time_limit


console = Console()

# -----------------------------
# Table logic
# -----------------------------

table = Table(title="Incoming Packets", border_style="white")
table.add_column("ID", style="dim", width=4)
table.add_column("Client IP", style="magenta", width=20)
table.add_column("Content", style="white", width=25)
table.add_column("Timestamp Sent", style="yellow", width=26)
table.add_column("Timestamp Received", style="green", width=26)
table.add_column("Packet Size (bytes)", style="green", justify="center", width=13)
table.add_column("Latency (ms)", justify="right", width=13)


# -----------------------------
# Network connection setup
# -----------------------------

serverPort = PORT_NUM
serverIP = IP_ADDRESS
bufferSize = BUFFER_SIZE

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((serverIP, serverPort))
server.settimeout(5)

console.print("[bold yellow]PC server is up and listening...[/bold yellow]")



while time.time() < t_end_loop:
    try:    
        data, address = server.recvfrom(bufferSize)
        server_received_at = datetime.now()

        if start_time_troughput is None:
            start_time_troughput = time.time()


        #loads data from json 
        message = json.loads(data.decode('utf-8'))
        content_type = message["content"]


        # -----------------------------
        # Handle Packet Loss
        # -----------------------------
        #packet size
        payload_size = len(data)
        total_packet_size = payload_size + 28
        #total_bytes += total_packet_size


        if content_type == "DONE":
            total_sent_by_client = int(message["seq"])
            print("[bold cyan]Received DONE signal from client.[/bold cyan]")
        
        
        if content_type == 'NORMAL':
            curr_seq = int(message['seq'])

            if seq_received == 0:
                seq_lost += curr_seq  
            elif curr_seq > last_seq_num + 1:
                seq_lost += (curr_seq - last_seq_num - 1)

            last_seq_num = curr_seq
            seq_received += 1

            normal_bytes += total_packet_size


        # -----------------------------
        # Handle attacker packets
        # -----------------------------
        if content_type == "ATTACK":
            attacker_packet_count += 1



        # -----------------------------
        # Handle image data
        # -----------------------------
        if content_type == "IMAGE_B64":
            chunk_id = message["chunk_id"]
            total_chunks = message["total_chunks"]
            image_ext = message["ext"]
            b64_chunks[chunk_id] = message["data"]
            expected_chunks = total_chunks

            if len(b64_chunks) == expected_chunks:
                 print("[green]All Base64 chunks received. Reassembling...[/green]")
                 print(f"Expected chunks = {expected_chunks}")
                 full_b64 = "".join(b64_chunks[i] for i in range(expected_chunks))
                 img_bytes = base64.b64decode(full_b64)
                 filename = f"received_image{image_ext}"
                 with open(filename, "wb") as f:
                     f.write(img_bytes)
                     print(f"[bold green]Image saved as {filename}[/bold green]")
                     b64_chunks = {}
        expected_chunks = None


        # -----------------------------
        # DoS rate, throughput, other calculation 
        # -----------------------------

        #---------------
        #Lattency
        client_sent = datetime.fromisoformat(message['sent_at'])
        latency_ms = abs((server_received_at - client_sent).total_seconds() * 1000)

        #---------------
        #Thorughput

        time_elapsed_total = time.time() - start_time_troughput
        if time_elapsed_total <= 0:
            time_elapsed_total = 1e-6 

        #bits per sec
        throughput_bps = (normal_bytes * 8) / time_elapsed_total
        #mega bits per sec     
        throughput_mbps = throughput_bps / 1_000_000                   
        #packet per sec
        throughput_pps = seq_received / time_elapsed_total 

        #---------------
        # DoS rate
        dos_rate = attacker_packet_count / time_elapsed_total 


        # -----------------------------
        # Create content for table rows
        # -----------------------------
        table.add_row(
            str(packet_id),
            f"{address[0]}:{address[1]}",
            message["content"],
            message["sent_at"],
            server_received_at.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            f"{total_packet_size}",
            f"{latency_ms:.2f}"
        )

        # -----------------------------
        # Add the result to a json file 
        # -----------------------------
        results.append({
            "dos_rate": dos_rate,
            "throughput_mbps": throughput_mbps,
            "throughput_pps": throughput_pps,
            "seq_received": seq_received 
        })

        console.clear()
        console.print(table)

        print(f"Throughput: {throughput_mbps:.4f} Mbps ({throughput_pps:.2f} pps), {throughput_bps:.4f} bps") 
        
        print(f"DoS Rate: {dos_rate:.2f} Mbps")


        packet_id += 1

    except socket.timeout:
        console.print("[red]No incoming packets. Closing...[/red]")
        break
    except KeyboardInterrupt:
        console.print("[red]Interrupted. Closing...[/red]")
        break

server.close()


# -----------------------------
# Report summary packet loss
# -----------------------------

total_seq_sent = TOTAL_PACKETS_SENT

seq_lost = total_seq_sent - seq_received

if total_seq_sent > 0:
    lost_seq_percent = (seq_lost / total_seq_sent) * 100
else:
    lost_seq_percent = 0

summary_dos_rate = attacker_packet_count / SET_Loop_time_limit
summary_throughput_pps = seq_received / SET_Loop_time_limit

print("\n--- SUMMARY OF PACKET LOSS ---")
print(f"Expected (sent): {total_seq_sent}")
print(f"Received:        {seq_received}")
print(f"Lost:            {seq_lost}")
print(f"Loss %:          {lost_seq_percent:.2f}%")
print(f"Attacker packets:    {attacker_packet_count}")
print(f"Attacker rate:       {summary_dos_rate:.2f} packets/sec")
print(f"Avg throughput:      {summary_throughput_pps:.2f} pps")
print("--- END OF SUMMARY ---")


 
# -----------------------------
# Get the output of result.json
# -----------------------------

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
console.print("[bold green]Results saved to results.json[/bold green]")

dos_rates = [r["dos_rate"] for r in results]
throughputs = [r["throughput_mbps"] for r in results]
seq_received_over_time = [r["seq_received"] for r in results]


# -----------------------------
# Plot - subplots
# -----------------------------

# Define nessary figure parameters
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
 
# Plot 1 - DoS rate vs Throughput
ax1.plot(dos_rates, throughputs, color='steelblue')
ax1.set_title("Throughput vs DoS Rate")
ax1.set_xlabel("DoS Rate (packets/sec)")
ax1.set_ylabel("Throughput (Mbps)")
ax1.grid(True, linestyle='--', alpha=0.5)
 
# Plot 2 - Received packets over time vs DoS rate
ax2.bar(dos_rates, seq_received_over_time, color='tomato', width=0.8)
ax2.set_title("Received Packets vs Attacker Rate")
ax2.set_xlabel("Attacker Rate")
ax2.set_ylabel("Received Packets")
ax2.grid(True, linestyle='--', alpha=0.5, axis='y')
 
# FIX: tight_layout BEFORE savefig
plt.tight_layout()
fig.savefig("Plot.png")
plt.show()
 
console.print("[bold green]Plot saved as Plot.png[/bold green]")