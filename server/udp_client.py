from threading import Thread, Event
from game.hangman import get_remaining_time, decrement_time
from lobby.lobby import players
import time
import socket
import json

_stop_event: Event | None = None

def timer(server, stop_event: Event):
    while get_remaining_time() and not stop_event.is_set():
        decrement_time()

        for player_id, player in list(players.items()):
            data = json.dumps({"tempo": get_remaining_time()}).encode() + b"\n"
            server.sendto(data, (player.ip, 32350))

        time.sleep(1)

def stop_timer():
    global _stop_event
    if _stop_event is not None:
        _stop_event.set()

def start_timer():
    global _stop_event

    stop_timer()
    _stop_event = Event()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t = Thread(target=timer, args=(server, _stop_event), daemon=True)
    t.start()
