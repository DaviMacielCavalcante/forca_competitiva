from concurrent.futures import ThreadPoolExecutor
import socket
import json

def handle_connection(conn):
    
    buffer = b""
    message = []
    while True:
        data = conn.recv(1024)
        if not data:
            conn.close()
            break
        buffer += data
        before, sep, after = buffer.partition(b"\n")
        

        
        if sep:
            before_as_dict = json.loads(before)
            print(before_as_dict)
            
            message.append(before)
            
            ack = {
            "status": "ok"
            }
        
            ack_bytes = json.dumps(ack)+"\n"
            
            ack_data = ack_bytes.encode()
            
            conn.sendall(ack_data)
                
            buffer = after

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("0.0.0.0", 32348))
server.listen()
            
with ThreadPoolExecutor(max_workers=10) as thread:
    while True:
        conn, addr = server.accept()
        thread.submit(handle_connection, conn)