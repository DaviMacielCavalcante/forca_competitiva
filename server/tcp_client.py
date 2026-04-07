from concurrent.futures import ThreadPoolExecutor
from game.hangman import set_word, add_to_queue, start_game, is_game_started, guess_letter, calculate_score, is_round_over, rotate_host, reset_round
from lobby.lobby import enter_lobby, leave_lobby, broadcast_lobby, notify_host, players, broadcast_game_state
from server.udp_client import start_timer
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
                    start_timer()
                
            if before_as_dict["acao"] == "palavra":
                set_word(before_as_dict["palavra"])
                
            if before_as_dict["acao"] == "letra":
                
                guess = guess_letter(before_as_dict["letra"])
                
                if guess["correct"]:
                    
                    score = calculate_score(100)
                    
                    players[player_id].score += score
                    guess["score"] = score
                    
                broadcast_game_state(guess)
                    
                is_over, msg = is_round_over(players_quantity= len(players))
                
                    
                if is_over:
                    guess["acao"] = msg["acao"]
                    broadcast_game_state(guess)
                    new_host_id = rotate_host()                   
                    notify_host(new_host_id)                    
                    reset_round()              
                    start_timer()                        
                
            message.append(before)
            
            ack = {
            "status": "ok"
            }
        
            ack_bytes = json.dumps(ack)+"\n"
            
            ack_data = ack_bytes.encode()
            
            conn.sendall(ack_data)
                
            buffer = after

if __name__ == "__main__":
    import os
    port = int(os.environ.get("TCP_PORT", 32348))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen()

    with ThreadPoolExecutor(max_workers=10) as thread:
        while True:
            conn, addr = server.accept()
            thread.submit(handle_connection, conn, addr)