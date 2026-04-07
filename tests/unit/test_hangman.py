import pytest
from collections import deque
from game import hangman


@pytest.fixture(autouse=True)
def reset_game_state():
    """Reset all module-level globals before each test."""
    hangman.host_deque = deque()
    hangman.current_word = ""
    hangman.game_started = False
    hangman.revealed_letters = []
    hangman.used_letters = set()
    hangman.remaining_attemps = 6
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
        result = hangman.guess_letter("a")
        assert result["revealed_letters"] == ["_", "a", "_", "_"]
        assert result["correct"] is True

    def test_correct_guess_does_not_decrement_attempts(self):
        """A correct guess should not reduce remaining attempts."""
        hangman.set_word("gato")
        hangman.guess_letter("a")
        assert hangman.remaining_attemps == 6

    def test_wrong_guess_decrements_attempts(self):
        """A wrong guess should decrement remaining_attemps by 1."""
        hangman.set_word("gato")
        result = hangman.guess_letter("z")
        assert result["correct"] is False
        assert result["remaining_attempts"] == 5

    def test_duplicate_letter_returns_current_state(self):
        """A duplicate guess should return the current state without changing anything."""
        hangman.set_word("gato")
        hangman.guess_letter("a")
        attempts_before = hangman.remaining_attemps
        result = hangman.guess_letter("a")
        assert result["correct"] is False
        assert result["remaining_attempts"] == attempts_before

    def test_duplicate_letter_does_not_decrement_attempts(self):
        """A duplicate guess should not decrement attempts."""
        hangman.set_word("gato")
        hangman.guess_letter("z")
        attempts_after_first = hangman.remaining_attemps
        hangman.guess_letter("z")
        assert hangman.remaining_attemps == attempts_after_first

    def test_correct_guess_increments_players_who_guessed(self):
        """A correct guess should increment players_who_guessed."""
        hangman.set_word("gato")
        hangman.guess_letter("a")
        assert hangman.players_who_guessed == 1

    def test_letter_appearing_multiple_times_is_fully_revealed(self):
        """A correct guess should reveal all occurrences of the letter."""
        hangman.set_word("banana")
        result = hangman.guess_letter("a")
        assert result["revealed_letters"] == ["_", "a", "_", "a", "_", "a"]


# --- is_round_over ---

class TestIsRoundOver:

    def test_not_over_at_start(self):
        """Round should not be over at game start."""
        is_over, _ = hangman.is_round_over(players_quantity=2)
        assert is_over is False

    def test_over_when_all_players_guessed(self):
        """Round should end when all players have guessed correctly."""
        hangman.players_who_guessed = 2
        is_over, msg = hangman.is_round_over(players_quantity=2)
        assert is_over is True
        assert "all" in msg["acao"]

    def test_over_when_attempts_exhausted(self):
        """Round should end when remaining attempts reach zero."""
        hangman.remaining_attemps = 0
        is_over, msg = hangman.is_round_over(players_quantity=2)
        assert is_over is True
        assert "failed" in msg["acao"]

    def test_over_when_time_runs_out(self):
        """Round should end when remaining time reaches zero."""
        hangman.remaining_time = 0
        is_over, msg = hangman.is_round_over(players_quantity=2)
        assert is_over is True
        assert "failed" in msg["acao"]


# --- reset_round ---

class TestResetRound:

    def test_resets_attempts(self):
        """reset_round() should restore remaining_attemps to 6."""
        hangman.remaining_attemps = 0
        hangman.reset_round()
        assert hangman.remaining_attemps == 6

    def test_resets_time(self):
        """reset_round() should restore remaining_time to 60."""
        hangman.remaining_time = 0
        hangman.reset_round()
        assert hangman.remaining_time == 60

    def test_resets_players_who_guessed(self):
        """reset_round() should reset players_who_guessed to 0."""
        hangman.players_who_guessed = 3
        hangman.reset_round()
        assert hangman.players_who_guessed == 0


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
