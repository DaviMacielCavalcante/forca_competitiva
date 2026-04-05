from collections import deque
from threading import Lock

host_deque = deque()
host_lock = Lock()
word_lock = Lock()
current_word: str = ""
game_started: bool = False

def add_to_queue(player_id: str):
    
    with host_lock:    
        host_deque.append(player_id)
    
def rotate_host():
    
    with host_lock:
        player_id = host_deque.popleft()
        
        host_deque.append(player_id)
        
    return player_id

def set_word(word: str):
    
    global current_word
    
    with word_lock:
        current_word = word

def start_game():
    
    global game_started
    
    game_started = True
    
    host_id = rotate_host()
    
    return host_id

def is_game_started():
    
    return game_started