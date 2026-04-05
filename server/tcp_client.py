from concurrent.futures import ThreadPoolExecutor
from ..game.hangman import set_word, add_to_queue, start_game, is_game_started
from ..lobby.lobby import enter_lobby, leave_lobby, broadcast_lobby, notify_host, players
import socket
import json

def handle_connection(conn, addr):
    
    buffer = b""
    message = []
    
    player_id = None
    
    while True:
        try:
            data = conn.recv(1024)
        except (ConnectionResetError, BrokenPipeError):
            if player_id:
                leave_lobby(player_id=player_id)
                broadcast_lobby()
            break
            
        if not data:
            conn.close()
            break
        buffer += data
        before, sep, after = buffer.partition(b"\n")
        
        if sep:
            before_as_dict = json.loads(before)
            print(before_as_dict)
            
            if before_as_dict["acao"] == "entrar":
                
                player_ip, _ = addr
                
                player_id = enter_lobby(
                    name=before_as_dict["nome"], 
                    ip=player_ip,
                    conn=conn
                )
                
                broadcast_lobby()
                
                add_to_queue(player_id=player_id)
                
                if len(players) >= 2 and not is_game_started():
                    host_id = start_game()
                    notify_host(host_id)
                
            if before_as_dict["acao"] == "palavra":
                set_word(before_as_dict["palavra"])
                
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
        thread.submit(handle_connection, conn, addr)