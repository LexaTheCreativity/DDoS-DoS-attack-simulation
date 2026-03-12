##PC1 as server

import socket
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table


console = Console()

table = Table(title="Incoming Packets", border_style="white")
table.add_column("ID", style="dim", width=4)
table.add_column("Client IP", style="magenta", width=20)
table.add_column("Content", style="white", width=25)
table.add_column("Timestamp Sent", style="yellow", width=26)
table.add_column("Timestamp Received", style="green", width=26)
table.add_column("Packet Size (bytes)", style="green", justify="center")
table.add_column("Latency (ms)", justify="right", width=13)

serverPort = 5002
serverIP = '10.245.30.27'
bufferSize = 10000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((serverIP, serverPort))
server.settimeout(5)

console.print("[bold yellow]PC server is up and listening...[/bold yellow]")

packet_id = 1

while True:
    try:
        data, address = server.recvfrom(bufferSize)
        server_received_at = datetime.now()

        #loads data from json 
        message = json.loads(data.decode('utf-8'))

        #Calc the packet size
        payload_size = len(data)
        total_packet_size = payload_size + 28

        #get the timestamp sent from the client 
        client_sent = datetime.fromisoformat(message['sent_at'])
        latency_ms = abs((server_received_at - client_sent).total_seconds() * 1000)


        if latency_ms > 200:
            latency_color = "red"
        elif latency_ms > 150:
            latency_color = "yellow"
        else:
            latency_color = "green"

        #add rows to the table
        table.add_row(
            str(packet_id),
            f"{address[0]}:{address[1]}",
            message["content"],
            message["sent_at"],
            server_received_at.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            f"{total_packet_size}",
            f"{latency_ms:.2f}"
        )

        console.clear()
        console.print(table)

        packet_id += 1

    except socket.timeout:
        console.print("[red]No incoming packets. Closing...[/red]")
        break
    except KeyboardInterrupt:
        console.print("[red]Interrupted. Closing...[/red]")
        break

    #test 1 2

server.close()