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
remaining_time: int = 60
players_who_guessed: int = 0
host_id: str

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
        
def get_host_id():
    return host_id

def start_game():
    
    global host_id    
    global game_started
    
    game_started = True
    
    host_id = rotate_host()
    
    return host_id

def is_game_started():
    
    return game_started

def handle_guess(guess_str: str, player: object, host: object) -> dict:
    """
    Substitui a antiga guess_letter.
    Recebe a string e identifica internamente se é tentativa de LETRA ou PALAVRA.
    Retorna um dicionário com o status de acerto e a pontuação ganha.
    """
    global current_word, revealed_letters, used_letters
    
    with guess_lock:
        guess_str = guess_str.strip().upper()
        earned_points = 0
        
        # ==========================================
        # 1. TENTATIVA DE PALAVRA COMPLETA (Chute)
        # ==========================================
        if len(guess_str) > 1:
            if guess_str == current_word:
                # O jogador acertou a palavra:
                earned_points = calculate_score()
                return {"correct": True, "score": earned_points}
            
            else:
                # Errou o chute da palavra: perde uma tentativa
                player.remaining_attempts -= 1
                return {"correct": False, "score": 0}
                
        # ==========================================
        # 2. TENTATIVA DE LETRA ÚNICA
        # ==========================================
        else:
            # Evita punir se a letra já foi tentada
            if guess_str in used_letters:
                return {"correct": False, "score": 0} 
                
            used_letters.add(guess_str)
            
            if guess_str in current_word:
                # Acertou a letra: atualiza a lista de reveladas
                for i, char in enumerate(current_word):
                    if char == guess_str:
                        revealed_letters[i] = guess_str
                        
                # Verifica se ESSA letra foi a última necessária para preencher a palavra
                if "_" not in revealed_letters:
                    earned_points = calculate_score() 
                    return {"correct": True, "score": earned_points}
                
                # Acertou uma letra qualquer no meio do jogo
                return {"correct": True, "score": 0}
            else:
                # Errou a letra
                player.remaining_attempts -= 1
                return {"correct": False, "score": 0}
        
def calculate_score() -> int:
    """
    Calcula a pontuação da rodada usando base de 1000 pontos.
    Fatores de redução: tempo restante e caracteres revelados.
    """
    global remaining_time, revealed_letters, current_word
    
    base_score = 1000
    
    # Se respondeu em menos de 15s (remaining_time >= 45), o time_factor é 1.0 (100%).
    # Se demorou mais, cai proporcionalmente. Ex: 30s restantes = 30 / 45 = 0.66
    time_factor = min(1.0, remaining_time / 45.0)
    
    # Conta quantos espaços já foram descobertos (diferentes de '_')
    revealed_count = len([char for char in revealed_letters if char != "_"])
    
    if revealed_count <= 1:
        # Margem de tolerância: 0 ou 1 caractere revelado não altera o multiplicador
        reveal_factor = 1.0
    else:
        # A partir de 2 caracteres, o fator diminui progressivamente.
        # Usa o tamanho total da palavra para ser proporcional.
        total_chars = len(current_word)
        safe_length = max(2, total_chars) # Evita divisão por zero (além da checagem do front)
        
        # Exemplo: Palavra de 6 letras. 3 reveladas.
        # (3 - 1) / (6 - 1) = 2 / 5 = 0.4. Multiplicador será 1.0 - 0.4 = 0.6 (60%)
        # Limitamos com o max(0.1, ...) para garantir que nunca zere completamente ou fique negativo.
        reveal_factor = max(0.1, 1.0 - ((revealed_count - 1) / (safe_length - 1)))
        
    final_score = int(base_score * time_factor * reveal_factor)
    return final_score

def is_game_over(players: list) -> tuple[bool, dict]:
    
    players_defeated: bool = all(
        p.remaining_attempts == 0 for p in players
    )
    
    if revealed_letters and "_" not in revealed_letters:
        return True, {"acao": "game_over_word_guessed"}
    if players_defeated:
        return True, {"acao": "game_over_attempts_exhausted"}
    return False, {}

def reset_time():
    global remaining_time
    remaining_time = 60

def is_word_set() -> bool:
    return bool(current_word)

def reset_round(players: dict):

    global remaining_time
    global players_who_guessed
    global game_started
    global current_word
    global revealed_letters

    remaining_time = 60
    players_who_guessed = 0
    game_started = False
    current_word = ""
    revealed_letters = []
    used_letters.clear()
    
    for player in players.values():
        player.remaining_attempts = 3
    
def get_remaining_time():
    
    global remaining_time
    
    return remaining_time

def decrement_time():
    
    global remaining_time
    
    remaining_time -=1;