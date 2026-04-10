import subprocess
import socket
import json
import time
import sys
import os
import pytest

SERVER_HOST = "127.0.0.1"


def find_free_port() -> int:
    """Ask the OS for a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# --- helpers ---

def send(conn: socket.socket, data: dict):
    msg = json.dumps(data) + "\n"
    conn.sendall(msg.encode())


def recv_all(conn: socket.socket, timeout: float = 1.5) -> list[dict]:
    """Collect all newline-delimited JSON messages within the timeout window."""
    conn.settimeout(timeout)
    buffer = b""
    messages = []
    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if line.strip():
                    messages.append(json.loads(line))
    except socket.timeout:
        pass
    return messages


def connect(port: int) -> socket.socket:
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((SERVER_HOST, port))
    return conn


# --- fixtures ---

@pytest.fixture(scope="function")
def server():
    """Start a fresh TCP server on a free port for each test."""
    port = find_free_port()
    env = {**os.environ, "TCP_PORT": str(port)}
    proc = subprocess.Popen(
        [sys.executable, "-m", "server.tcp_server"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=env,
    )
    time.sleep(0.8)  # give it time to bind
    yield proc, port
    proc.terminate()
    proc.wait()


# --- tests ---

class TestLobby:

    def test_player_can_join(self, server):
        """A player joining should receive a lobby list containing their name."""
        _, port = server
        conn = connect(port)
        send(conn, {"acao": "entrar", "nome": "Alice"})
        messages = recv_all(conn)
        conn.close()

        lobby_msgs = [m for m in messages if isinstance(m, list)]
        assert len(lobby_msgs) == 1
        names = [p["nome"] for p in lobby_msgs[0]]
        assert "Alice" in names

    def test_two_players_see_each_other_in_lobby(self, server):
        """Both players should appear in the lobby list after both join."""
        _, port = server
        alice = connect(port)
        bob = connect(port)

        send(alice, {"acao": "entrar", "nome": "Alice2"})
        time.sleep(0.1)
        send(bob, {"acao": "entrar", "nome": "Bob2"})
        time.sleep(0.1)

        messages = recv_all(alice)

        lobby_msgs = [m for m in messages if isinstance(m, list)]
        last_lobby = lobby_msgs[-1]
        names = [p["nome"] for p in last_lobby]

        alice.close()
        bob.close()

        assert "Alice2" in names
        assert "Bob2" in names


class TestGameFlow:

    def test_first_player_becomes_host(self, server):
        """When 2 players join, the first player should receive the host notification."""
        _, port = server
        alice = connect(port)
        bob = connect(port)

        send(alice, {"acao": "entrar", "nome": "Host"})
        time.sleep(0.1)
        send(bob, {"acao": "entrar", "nome": "Guest"})
        time.sleep(0.1)

        alice_messages = recv_all(alice)
        bob.close()
        alice.close()

        acoes = [m.get("acao") for m in alice_messages if isinstance(m, dict)]
        assert "voce_e_o_host" in acoes

    def test_server_acks_every_message(self, server):
        """Server should send {"status": "ok"} after every message."""
        _, port = server
        conn = connect(port)
        send(conn, {"acao": "entrar", "nome": "AckTester"})
        messages = recv_all(conn)
        conn.close()

        acks = [m for m in messages if isinstance(m, dict) and m.get("status") == "ok"]
        assert len(acks) >= 1

    def test_correct_letter_guess_is_revealed(self, server):
        """A correct letter guess should appear in revealed_letters."""
        _, port = server
        alice = connect(port)
        bob = connect(port)

        send(alice, {"acao": "entrar", "nome": "AliceG"})
        time.sleep(0.1)
        send(bob, {"acao": "entrar", "nome": "BobG"})
        time.sleep(0.1)

        recv_all(alice, timeout=0.5)

        send(alice, {"acao": "palavra", "palavra": "gato"})
        recv_all(alice, timeout=0.5)

        send(bob, {"acao": "letra", "letra": "a"})
        messages = recv_all(bob)

        alice.close()
        bob.close()

        game_states = [m for m in messages if isinstance(m, dict) and "revealed_letters" in m]
        assert len(game_states) >= 1
        assert "a" in game_states[0]["revealed_letters"]
        assert game_states[0]["correct"] is True

    def test_wrong_letter_decrements_attempts(self, server):
        """A wrong letter guess should decrement remaining_attempts."""
        _, port = server
        alice = connect(port)
        bob = connect(port)

        send(alice, {"acao": "entrar", "nome": "AliceW"})
        time.sleep(0.1)
        send(bob, {"acao": "entrar", "nome": "BobW"})
        time.sleep(0.1)

        recv_all(alice, timeout=0.5)

        send(alice, {"acao": "palavra", "palavra": "gato"})
        recv_all(alice, timeout=0.5)

        send(bob, {"acao": "letra", "letra": "z"})
        messages = recv_all(bob)

        alice.close()
        bob.close()

        game_states = [m for m in messages if isinstance(m, dict) and "revealed_letters" in m]
        assert len(game_states) >= 1
        assert game_states[0]["correct"] is False
        assert game_states[0]["remaining_attempts"] == 2

    def test_duplicate_letter_does_not_decrement_attempts(self, server):
        """Sending the same letter twice should not reduce attempts on the second send."""
        _, port = server
        alice = connect(port)
        bob = connect(port)

        send(alice, {"acao": "entrar", "nome": "AliceD"})
        time.sleep(0.1)
        send(bob, {"acao": "entrar", "nome": "BobD"})
        time.sleep(0.1)

        recv_all(alice, timeout=0.5)

        send(alice, {"acao": "palavra", "palavra": "gato"})
        recv_all(alice, timeout=0.5)

        send(bob, {"acao": "letra", "letra": "z"})
        recv_all(bob, timeout=0.5)

        send(bob, {"acao": "letra", "letra": "z"})
        messages = recv_all(bob)

        alice.close()
        bob.close()

        game_states = [m for m in messages if isinstance(m, dict) and "revealed_letters" in m]
        assert len(game_states) >= 1
        assert game_states[0]["remaining_attempts"] == 2
