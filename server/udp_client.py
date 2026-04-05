from threading import Thread
from ..game.hangman import get_remaining_time, decrement_time
from ..lobby.lobby import players
import time
import socket
import json
    
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("0.0.0.0", 32349))

def timer():
    while get_remaining_time():
        decrement_time()
        
        for player_id, player in players.items():
            
            data = json.dumps({"tempo": get_remaining_time()}).encode() + b"\n"
            server.sendto(data, (player.ip, 32350))
            
        time.sleep(1)
        
def start_timer():            
    t = Thread(target=timer)
    t.start()


    
    