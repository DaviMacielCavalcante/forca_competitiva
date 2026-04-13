from concurrent.futures import ThreadPoolExecutor
from game.hangman import set_word, add_to_queue, start_game, is_game_started, handle_guess, is_game_over, is_word_set, get_host_id, get_revealed_letters
from lobby.lobby import enter_lobby, leave_lobby, broadcast_lobby, notify_host, players, broadcast_game_state, notify_game_started
from server.udp_server import start_timer
from server.round import end_round
from loguru import logger
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
            logger.debug("mensagem recebida: {}", before_as_dict)

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
                    try:
                        host_id = start_game()
                        logger.debug("jogo iniciado: host_id={}, players={}", host_id, list(players.keys()))
                        notify_host(host_id)
                        notify_game_started(host_id)
                        logger.debug("notificação de host enviada para {}", host_id)
                    except Exception:
                        logger.exception("falha ao iniciar jogo")

            if before_as_dict["acao"] == "palavra":
                set_word(before_as_dict["palavra"])
                start_timer()
                broadcast_game_state({"revealed_letters": get_revealed_letters()})
                logger.debug("palavra definida, timer iniciado")

            if before_as_dict["acao"] == "letra" and is_word_set():

                guess = handle_guess(before_as_dict["letra"], player=players.get(player_id), host=players[get_host_id()])

                if guess["correct"] and guess.get("score"):
                    players[player_id].score += guess["score"]

                broadcast_game_state(guess)

                game_over, reason = is_game_over(players=players.values())

                if game_over:
                    end_round(reason)
                    

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
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen()

    with ThreadPoolExecutor(max_workers=10) as thread:
        while True:
            conn, addr = server.accept()
            thread.submit(handle_connection, conn, addr)