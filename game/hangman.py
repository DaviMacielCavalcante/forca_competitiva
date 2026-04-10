from collections import deque
from threading import Lock

host_deque = deque()
host_lock = Lock()
word_lock = Lock()
guess_lock = Lock()
current_word: str = ""
game_started: bool = False
revealed_letters: list = []
used_letters: set = set()
remaining_attemps: int = 6
remaining_time: int = 60
players_who_guessed: int = 0

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
    
    global revealed_letters
    
    revealed_letters = ["_"] * len(word)
    
    with word_lock:
        current_word = word

def start_game():
    
    global game_started
    
    game_started = True
    
    host_id = rotate_host()
    
    return host_id

def is_game_started():
    
    return game_started

def guess_letter(letter: str):
    
    with guess_lock:
    
        global remaining_attemps
        global revealed_letters
        global players_who_guessed
        
        is_guess_correct = False
        
        
        if letter in used_letters:
            return {
            "revealed_letters": revealed_letters,
            "correct": False,
            "remaining_attempts": remaining_attemps
        }
        
        used_letters.add(letter)
        
        if letter in current_word:
            players_who_guessed += 1
            for i, char in enumerate(current_word):
                if letter == char:
                    revealed_letters[i] = letter
                    is_guess_correct = True
                    
                    
        else :
            remaining_attemps -= 1
            
        return {
            "revealed_letters": revealed_letters,
            "correct": is_guess_correct,
            "remaining_attempts": remaining_attemps
        }
        
def calculate_score(score: int):
    
    global remaining_time
    global players_who_guessed
    
    time_factor = remaining_time / 60
    
    score -= (players_who_guessed * time_factor)
    
    return score

def is_game_over() -> tuple[bool, dict]:
    if revealed_letters and "_" not in revealed_letters:
        return True, {"acao": "game_over_word_guessed"}
    if remaining_attemps == 0:
        return True, {"acao": "game_over_attempts_exhausted"}
    return False, {}

def reset_time():
    global remaining_time
    remaining_time = 60

def is_word_set() -> bool:
    return bool(current_word)

def reset_round():

    global remaining_attemps
    global remaining_time
    global players_who_guessed
    global game_started
    global current_word
    global revealed_letters

    remaining_attemps = 6
    remaining_time = 60
    players_who_guessed = 0
    game_started = False
    current_word = ""
    revealed_letters = []
    used_letters.clear()
    
def get_remaining_time():
    
    global remaining_time
    
    return remaining_time

def decrement_time():
    
    global remaining_time
    
    remaining_time -=1;