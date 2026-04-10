import pytest
from collections import deque
from dataclasses import dataclass
from game import hangman


@dataclass
class FakePlayer:
    """Minimal Player stand-in for unit tests."""
    remaining_attempts: int = 3
    score: int = 0


@pytest.fixture(autouse=True)
def reset_game_state():
    """Reset all module-level globals before each test."""
    hangman.host_deque = deque()
    hangman.current_word = ""
    hangman.game_started = False
    hangman.revealed_letters = []
    hangman.used_letters = set()
    hangman.remaining_time = 60
    hangman.players_who_guessed = 0


# --- set_word ---

class TestSetWord:

    def test_stores_word(self):
        """set_word() should store the word in current_word."""
        hangman.set_word("gato")
        assert hangman.current_word == "gato"

    def test_initializes_revealed_letters(self):
        """set_word() should initialize revealed_letters with underscores."""
        hangman.set_word("gato")
        assert hangman.revealed_letters == ["_", "_", "_", "_"]

    def test_revealed_letters_length_matches_word(self):
        """revealed_letters should have the same length as the word."""
        hangman.set_word("python")
        assert len(hangman.revealed_letters) == len("python")


# --- guess_letter ---

class TestGuessLetter:

    def test_correct_guess_reveals_letter(self):
        """A correct guess should reveal the letter in the right positions."""
        hangman.set_word("gato")
        player = FakePlayer()
        host = FakePlayer()
        result = hangman.guess_letter("a", player, host)
        assert result["revealed_letters"] == ["_", "a", "_", "_"]
        assert result["correct"] is True

    def test_correct_guess_does_not_decrement_attempts(self):
        """A correct guess should not reduce remaining attempts."""
        hangman.set_word("gato")
        player = FakePlayer()
        host = FakePlayer()
        hangman.guess_letter("a", player, host)
        assert player.remaining_attempts == 3

    def test_wrong_guess_decrements_attempts(self):
        """A wrong guess should decrement the player's remaining_attempts by 1."""
        hangman.set_word("gato")
        player = FakePlayer()
        host = FakePlayer()
        result = hangman.guess_letter("z", player, host)
        assert result["correct"] is False
        assert result["remaining_attempts"] == 2

    def test_duplicate_letter_returns_current_state(self):
        """A duplicate guess should return the current state without changing anything."""
        hangman.set_word("gato")
        player = FakePlayer()
        host = FakePlayer()
        hangman.guess_letter("a", player, host)
        attempts_before = player.remaining_attempts
        result = hangman.guess_letter("a", player, host)
        assert result["correct"] is False
        assert result["remaining_attempts"] == attempts_before

    def test_duplicate_letter_does_not_decrement_attempts(self):
        """A duplicate guess should not decrement attempts."""
        hangman.set_word("gato")
        player = FakePlayer()
        host = FakePlayer()
        hangman.guess_letter("z", player, host)
        attempts_after_first = player.remaining_attempts
        hangman.guess_letter("z", player, host)
        assert player.remaining_attempts == attempts_after_first

    def test_correct_guess_increments_players_who_guessed(self):
        """A correct guess should increment players_who_guessed."""
        hangman.set_word("gato")
        player = FakePlayer()
        host = FakePlayer()
        hangman.guess_letter("a", player, host)
        assert hangman.players_who_guessed == 1

    def test_letter_appearing_multiple_times_is_fully_revealed(self):
        """A correct guess should reveal all occurrences of the letter."""
        hangman.set_word("banana")
        player = FakePlayer()
        host = FakePlayer()
        result = hangman.guess_letter("a", player, host)
        assert result["revealed_letters"] == ["_", "a", "_", "a", "_", "a"]


# --- host scoring on player elimination ---

class TestHostScoring:

    def test_host_gains_points_when_player_exhausts_attempts(self):
        """Host should gain points when a player's remaining_attempts reaches 0."""
        hangman.set_word("gato")
        player = FakePlayer(remaining_attempts=1)
        host = FakePlayer()
        hangman.remaining_time = 30
        hangman.guess_letter("z", player, host)
        expected_score = 100 * (60 - 30) / 60  # 50.0
        assert host.score == expected_score

    def test_host_gains_no_points_when_player_still_has_attempts(self):
        """Host should not gain points if the player still has attempts left."""
        hangman.set_word("gato")
        player = FakePlayer(remaining_attempts=3)
        host = FakePlayer()
        hangman.guess_letter("z", player, host)
        assert host.score == 0

    def test_host_gains_max_points_when_player_fails_at_end_of_round(self):
        """Host should gain ~100 points if the player fails at the very end of the timer."""
        hangman.set_word("gato")
        player = FakePlayer(remaining_attempts=1)
        host = FakePlayer()
        hangman.remaining_time = 1
        hangman.guess_letter("z", player, host)
        expected_score = 100 * (60 - 1) / 60
        assert host.score == pytest.approx(expected_score)

    def test_host_gains_zero_points_when_player_fails_instantly(self):
        """Host should gain 0 points if the player fails immediately (full time remaining)."""
        hangman.set_word("gato")
        player = FakePlayer(remaining_attempts=1)
        host = FakePlayer()
        hangman.remaining_time = 60
        hangman.guess_letter("z", player, host)
        assert host.score == 0.0


# --- is_game_over ---

class TestIsGameOver:

    def test_not_over_at_start(self):
        """Game should not be over at start."""
        players = [FakePlayer(), FakePlayer()]
        is_over, _ = hangman.is_game_over(players)
        assert is_over is False

    def test_over_when_word_fully_revealed(self):
        """Game should end when the word is fully guessed."""
        hangman.set_word("ab")
        player = FakePlayer()
        host = FakePlayer()
        hangman.guess_letter("a", player, host)
        hangman.guess_letter("b", player, host)
        is_over, msg = hangman.is_game_over([player])
        assert is_over is True
        assert msg["acao"] == "game_over_word_guessed"

    def test_over_when_all_players_exhausted(self):
        """Game should end when all players have 0 remaining attempts."""
        players = [FakePlayer(remaining_attempts=0), FakePlayer(remaining_attempts=0)]
        is_over, msg = hangman.is_game_over(players)
        assert is_over is True
        assert msg["acao"] == "game_over_attempts_exhausted"

    def test_not_over_when_some_players_have_attempts(self):
        """Game should not end if at least one player still has attempts."""
        players = [FakePlayer(remaining_attempts=0), FakePlayer(remaining_attempts=2)]
        is_over, _ = hangman.is_game_over(players)
        assert is_over is False


# --- reset_round ---

class TestResetRound:

    def test_resets_player_attempts(self):
        """reset_round() should restore each player's remaining_attempts to 3."""
        players = [FakePlayer(remaining_attempts=0), FakePlayer(remaining_attempts=1)]
        hangman.reset_round(players)
        for p in players:
            assert p.remaining_attempts == 3

    def test_resets_time(self):
        """reset_round() should restore remaining_time to 60."""
        hangman.remaining_time = 0
        hangman.reset_round([])
        assert hangman.remaining_time == 60

    def test_resets_players_who_guessed(self):
        """reset_round() should reset players_who_guessed to 0."""
        hangman.players_who_guessed = 3
        hangman.reset_round([])
        assert hangman.players_who_guessed == 0


# --- get_host_id ---

class TestGetHostId:

    def test_returns_host_id_after_start(self):
        """get_host_id() should return the current host's ID after start_game()."""
        hangman.add_to_queue("player-1")
        hangman.add_to_queue("player-2")
        hangman.start_game()
        assert hangman.get_host_id() == "player-1"


# --- calculate_score ---

class TestCalculateScore:

    def test_score_decreases_with_players_who_guessed(self):
        """Score should decrease proportionally to players_who_guessed and time_factor."""
        hangman.remaining_time = 60
        hangman.players_who_guessed = 1
        result = hangman.calculate_score(100)
        assert result == 99.0  # 100 - 1 * (60/60)

    def test_score_with_no_guessers(self):
        """Score should not change when no players have guessed."""
        hangman.players_who_guessed = 0
        result = hangman.calculate_score(100)
        assert result == 100


# --- decrement_time ---

class TestDecrementTime:

    def test_decrements_by_one(self):
        """decrement_time() should reduce remaining_time by 1."""
        hangman.remaining_time = 30
        hangman.decrement_time()
        assert hangman.remaining_time == 29


# --- host queue ---

class TestHostQueue:

    def test_add_to_queue(self):
        """add_to_queue() should add the player to the deque."""
        hangman.add_to_queue("player-1")
        assert "player-1" in hangman.host_deque

    def test_rotate_host_moves_first_to_last(self):
        """rotate_host() should pop the front and append to the back."""
        hangman.add_to_queue("player-1")
        hangman.add_to_queue("player-2")
        rotated = hangman.rotate_host()
        assert rotated == "player-1"
        assert list(hangman.host_deque) == ["player-2", "player-1"]
