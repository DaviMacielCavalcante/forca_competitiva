from lobby.lobby import broadcast_game_state, notify_host, players
from loguru import logger
from game.hangman import rotate_host, reset_round, is_word_set
from server.udp_server import stop_timer
from threading import Lock

_round_lock = Lock()

def end_round(reason: dict):
    
    with _round_lock:
        if not is_word_set():
            return
        stop_timer()
        broadcast_game_state({"acao": reason["acao"]})
        new_host_id = rotate_host()
        notify_host(new_host_id)
        reset_round(players=players)
        logger.debug("jogo encerrado ({}), novo host: {}", reason["acao"], new_host_id)
    