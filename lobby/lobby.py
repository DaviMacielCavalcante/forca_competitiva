from dataclasses import dataclass
from threading import Lock
from uuid import uuid4
import socket
import json

@dataclass
class Player:
    name: str
    ip: str
    socket: socket.socket
     
     
players: dict[str, Player] = {}

players_lock = Lock()

def enter_lobby(name: str, ip: str, conn: socket):
    
    player_id = str(uuid4())
    
    with players_lock:
        players[player_id] = Player(name=name, ip=ip, socket=conn)        
        
    return player_id

def leave_lobby(player_id: str):
    
    with players_lock:
        players.pop(player_id, None)
        
def broadcast_lobby():
    
    players_in_lobby = [
        {
            "id": player_id,
            "nome": players[player_id].name
        } 
        for player_id in players]
    
    players_in_lobby_json = json.dumps(players_in_lobby)+"\n"
    
    players_in_lobby_bytes = players_in_lobby_json.encode()
    
    for player in players_in_lobby:
        
        players[player["id"]].socket.sendall(players_in_lobby_bytes)
        
def notify_host(player_id: str):
    
    notification = {
        "acao": "voce_e_o_host"
    }
    
    notification_json = json.dumps(notification)+"\n"
    
    notification_data = notification_json.encode()
    
    players[player_id].socket.sendall(notification_data)