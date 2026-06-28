"""Regression tests for the Glitch Investigator number-guessing game.

Each test guards a specific bug that was recently fixed in logic_utils.py so
it can never silently regress. Test names and docstrings reference the bug.

All logic lives in the parent folder's logic_utils.py (no Streamlit needed).
"""

import os
import sys

import pytest

# Make `import logic_utils` work when pytest is run from the project folder:
# logic_utils.py lives in the parent directory of this tests/ folder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logic_utils
from logic_utils import (
    apply_guess,
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    new_game_state,
    parse_guess,
    update_score,
)


def fresh_state(secret, difficulty_low_high=None):
    """Build a known game state literally so we don't depend on randomness."""
    return {
        "secret": secret,
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
    }


# ---------------------------------------------------------------------------
# Ported from the original test file (corrected: check_guess returns a tuple).
# Bug #2 / #10 sanity checks on the basic outcomes.
# ---------------------------------------------------------------------------

def test_winning_guess_ported():
    """Ported: guess == secret (50 == 50) -> outcome 'Win'."""
    outcome, _message = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high_ported():
    """Ported: guess (60) > secret (50) -> outcome 'Too High'."""
    outcome, _message = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low_ported():
    """Ported: guess (40) < secret (50) -> outcome 'Too Low'."""
    outcome, _message = check_guess(40, 50)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# Bug #1: Off-by-one attempts init — attempts must start at 0, not 1.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_bug1_attempts_init_is_zero(difficulty):
    """Bug #1: new_game_state(...)['attempts'] must be 0 (not 1) per difficulty."""
    state = new_game_state(difficulty)
    assert state["attempts"] == 0


# ---------------------------------------------------------------------------
# Bug #2: Secret never stringified / numeric comparison stays correct.
# ---------------------------------------------------------------------------

def test_bug2_numeric_comparison_basic_outcomes():
    """Bug #2: integer comparisons give correct outcomes, no stringification."""
    assert check_guess(60, 50)[0] == "Too High"
    assert check_guess(40, 50)[0] == "Too Low"
    assert check_guess(50, 50)[0] == "Win"


def test_bug2_hints_stay_correct_across_sequence():
    """Bug #2: the old glitch broke on alternating attempts; drive several
    guesses through apply_guess and assert hints stay numerically correct
    on every turn (even and odd attempts alike)."""
    state = fresh_state(secret=25)
    # Normal difficulty -> range 1-50, limit 8; these in-range guesses
    # won't trigger a loss and stay within bounds.
    sequence = [
        (40, "Too High"),  # attempt 1 (odd)
        (10, "Too Low"),   # attempt 2 (even)
        (45, "Too High"),  # attempt 3 (odd)
        (15, "Too Low"),   # attempt 4 (even)
        (35, "Too High"),  # attempt 5 (odd)
        (20, "Too Low"),   # attempt 6 (even)
    ]
    for guess, expected in sequence:
        state, result = apply_guess(state, str(guess), "Normal")
        assert result["outcome"] == expected, (
            f"guess {guess} at attempt {state['attempts']} gave "
            f"{result['outcome']}, expected {expected}"
        )


# ---------------------------------------------------------------------------
# Bug #3: New Game range respects difficulty.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, low, high",
    [("Easy", 1, 20), ("Hard", 1, 100), ("Normal", 1, 50)],
)
def test_bug3_secret_within_difficulty_range(difficulty, low, high):
    """Bug #3: new_game_state secret must fall inside the difficulty range.
    Loop many times since the secret is random."""
    for _ in range(200):
        state = new_game_state(difficulty)
        assert low <= state["secret"] <= high


# ---------------------------------------------------------------------------
# Bug #4: New Game full reset.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_bug4_full_reset(difficulty):
    """Bug #4: new_game_state resets status='playing', score=0, attempts=0,
    history=[]."""
    state = new_game_state(difficulty)
    assert state["status"] == "playing"
    assert state["score"] == 0
    assert state["attempts"] == 0
    assert state["history"] == []


# ---------------------------------------------------------------------------
# Bug #5: Prompt range (logic-level) get_range_for_difficulty.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, expected",
    [("Easy", (1, 20)), ("Normal", (1, 50)), ("Hard", (1, 100))],
)
def test_bug5_get_range_for_difficulty(difficulty, expected):
    """Bug #5: get_range_for_difficulty returns the correct (low, high)."""
    assert get_range_for_difficulty(difficulty) == expected


def test_bug5_get_range_default():
    """Bug #5: an unknown difficulty defaults to (1, 100)."""
    assert get_range_for_difficulty("Bogus") == (1, 100)


# ---------------------------------------------------------------------------
# Bug #6: Win-score has no extra +1, and minimum floor of 10 holds.
# ---------------------------------------------------------------------------

def test_bug6_first_guess_win_score():
    """Bug #6: a first-guess win scores exactly 90 (no stray +1)."""
    assert update_score(0, "Win", 1) == 90


def test_bug6_win_score_floor():
    """Bug #6: win points are floored at 10 for large attempt numbers."""
    assert update_score(0, "Win", 20) == 10


@pytest.mark.parametrize(
    "attempt, expected_points",
    [(1, 90), (2, 80), (5, 50), (9, 10), (10, 10), (50, 10)],
)
def test_bug6_win_score_progression(attempt, expected_points):
    """Bug #6: win = 100 - 10*attempt, floored at 10, no extra penalty."""
    assert update_score(0, "Win", attempt) == expected_points


# ---------------------------------------------------------------------------
# Bug #7: "Too High" is a consistent -5 penalty (was +5 on even attempts);
#          "Too Low" is also -5.
# ---------------------------------------------------------------------------

def test_bug7_too_high_consistent_penalty_even_and_odd():
    """Bug #7: 'Too High' subtracts 5 on both even and odd attempts
    (old bug gave +5 on even attempts)."""
    assert update_score(100, "Too High", 2) == 95  # even
    assert update_score(100, "Too High", 3) == 95  # odd


def test_bug7_too_low_penalty():
    """Bug #7: 'Too Low' subtracts 5."""
    assert update_score(100, "Too Low", 2) == 95
    assert update_score(100, "Too Low", 3) == 95


@pytest.mark.parametrize("attempt", [1, 2, 3, 4, 5, 6, 7, 8])
def test_bug7_too_high_penalty_every_attempt(attempt):
    """Bug #7: 'Too High' is -5 regardless of attempt parity."""
    assert update_score(100, "Too High", attempt) == 95


# ---------------------------------------------------------------------------
# Bug #8 & #9: Invalid input does not consume an attempt and is not logged.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_input", ["abc", "", None])
def test_bug8_invalid_input_does_not_consume_attempt(bad_input):
    """Bug #8: invalid input returns valid=False and does not advance attempts."""
    state = fresh_state(secret=42)
    new_state, result = apply_guess(state, bad_input, "Normal")
    assert result["valid"] is False
    assert new_state["attempts"] == 0


@pytest.mark.parametrize("bad_input", ["abc", "", None])
def test_bug9_invalid_input_not_logged_to_history(bad_input):
    """Bug #9: invalid input is never appended to history."""
    state = fresh_state(secret=42)
    new_state, result = apply_guess(state, bad_input, "Normal")
    assert result["valid"] is False
    assert new_state["history"] == []


# ---------------------------------------------------------------------------
# Bug #10: Inverted hint messages fixed.
# Too High -> go LOWER; Too Low -> go HIGHER.
# ---------------------------------------------------------------------------

def test_bug10_too_high_says_lower():
    """Bug #10: a too-high guess (60 vs 50) tells the player to go LOWER."""
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_bug10_too_low_says_higher():
    """Bug #10: a too-low guess (40 vs 50) tells the player to go HIGHER."""
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# ---------------------------------------------------------------------------
# Bug #11: Loss detection / attempt limit — player gets the FULL allowed
# number of guesses, status flips to "lost" exactly after the last one.
# ---------------------------------------------------------------------------

def test_bug11_loss_exactly_after_full_limit_hard():
    """Bug #11: on Hard (limit 8) with a fixed secret, 8 wrong guesses must
    NOT flip 'lost' until exactly the 8th — the player gets all 8 guesses,
    not one fewer."""
    secret = 25
    state = fresh_state(secret=secret)
    limit = get_attempt_limit("Hard")
    assert limit == 8

    # Distinct wrong guesses each turn (all > secret -> "Too High", never a win,
    # and never repeated so the duplicate guard doesn't reject them).
    for attempt in range(1, limit + 1):
        wrong_guess = str(secret + attempt)  # 26..33 — all in 1-100
        state, result = apply_guess(state, wrong_guess, "Hard")
        assert result["outcome"] != "Win"
        if attempt < limit:
            assert state["status"] == "playing", (
                f"lost too early at attempt {attempt}"
            )
        else:
            assert state["status"] == "lost", (
                f"should be lost at the final attempt {attempt}"
            )
    assert state["attempts"] == limit


# ---------------------------------------------------------------------------
# Bug #12: Win detection and state immutability.
# ---------------------------------------------------------------------------

def test_bug12_win_detection_sets_won_status():
    """Bug #12: a correct guess yields outcome 'Win' and status 'won'."""
    state = fresh_state(secret=37)
    new_state, result = apply_guess(state, "37", "Normal")
    assert result["outcome"] == "Win"
    assert new_state["status"] == "won"


def test_bug12_apply_guess_does_not_mutate_input_state():
    """Bug #12: apply_guess is pure — it must not mutate the input state dict
    (attempts, history, score, status all unchanged on the original)."""
    state = {
        "secret": 37,
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
    }
    original_copy = {
        "secret": 37,
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
    }
    new_state, _result = apply_guess(state, "37", "Normal")

    # Original untouched.
    assert state == original_copy
    assert state["attempts"] == 0
    assert state["history"] == []
    assert state["status"] == "playing"
    assert state["score"] == 0
    # And the returned state genuinely advanced (sanity that it did something).
    assert new_state is not state
    assert new_state["attempts"] == 1


# ---------------------------------------------------------------------------
# Bug A: Decimals (and other non-integer numeric-looking input) are rejected.
# parse_guess must only accept whole numbers; it stays range-agnostic so it
# still parses negatives as ints (range is enforced in apply_guess).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_input", ["3.7", "3.0", "-2.5", "1e2", "abc"])
def test_bugA_parse_guess_rejects_non_integers(bad_input):
    """Bug A: decimals and non-integer numeric-looking input are invalid."""
    ok, value, err = parse_guess(bad_input)
    assert ok is False
    assert value is None
    assert err is not None


@pytest.mark.parametrize(
    "good_input, expected",
    [("5", 5), ("20", 20), (" 7 ", 7), ("-3", -3)],
)
def test_bugA_parse_guess_accepts_whole_numbers(good_input, expected):
    """Bug A: whole numbers (incl. whitespace-padded and negatives) parse as
    ints; range is enforced elsewhere so '-3' parses fine here."""
    ok, value, err = parse_guess(good_input)
    assert ok is True
    assert value == expected
    assert err is None


# ---------------------------------------------------------------------------
# Bug B: Negative / out-of-range guesses are rejected by apply_guess without
# consuming an attempt or logging to history.
# ---------------------------------------------------------------------------

def test_bugB_negative_guess_rejected_out_of_range():
    """Bug B: a negative guess ('-5' on Easy, range 1-20) is out of range;
    state stays unchanged (attempts 0, history [])."""
    state = fresh_state(secret=10)
    new_state, result = apply_guess(state, "-5", "Easy")
    assert result["valid"] is False
    assert new_state["attempts"] == 0
    assert new_state["history"] == []


def test_bugB_too_large_guess_rejected_out_of_range():
    """Bug B: a too-large guess ('25' on Easy, range 1-20) is out of range;
    state stays unchanged (attempts 0, history [])."""
    state = fresh_state(secret=10)
    new_state, result = apply_guess(state, "25", "Easy")
    assert result["valid"] is False
    assert new_state["attempts"] == 0
    assert new_state["history"] == []


def test_bugB_decimal_guess_rejected_invalid():
    """Bug B/A: a decimal guess ('3.7') is invalid; attempts unchanged."""
    state = fresh_state(secret=10)
    new_state, result = apply_guess(state, "3.7", "Easy")
    assert result["valid"] is False
    assert new_state["attempts"] == 0
    assert new_state["history"] == []


def test_bugB_in_range_integer_accepted_and_consumes_attempt():
    """Bug B: an in-range integer ('10' on Easy) is valid and consumes an
    attempt (and is logged to history)."""
    state = fresh_state(secret=15)
    new_state, result = apply_guess(state, "10", "Easy")
    assert result["valid"] is True
    assert new_state["attempts"] == 1
    assert new_state["history"] == [10]


# ---------------------------------------------------------------------------
# Duplicate guards: a number already in history is rejected without consuming
# an attempt, logging it again, or changing the score/status.
# ---------------------------------------------------------------------------

def test_duplicate_guess_rejected():
    """A repeated guess is invalid: state unchanged, no extra attempt, no
    duplicate in history, score/status untouched."""
    state = fresh_state(secret=15)
    # First guess (10) is valid and recorded.
    state, first = apply_guess(state, "10", "Easy")
    assert first["valid"] is True
    assert state["attempts"] == 1
    assert state["history"] == [10]

    score_before = state["score"]
    # Guessing 10 again must be rejected.
    new_state, result = apply_guess(state, "10", "Easy")
    assert result["valid"] is False
    assert "already guessed" in result["error"].lower()
    assert new_state["attempts"] == 1            # no attempt consumed
    assert new_state["history"] == [10]          # not logged twice
    assert new_state["score"] == score_before    # score untouched
    assert new_state["status"] == "playing"


def test_duplicate_guess_does_not_block_new_numbers():
    """After a rejected duplicate, a fresh in-range number is still accepted."""
    state = fresh_state(secret=15)
    state, _ = apply_guess(state, "10", "Easy")
    state, dup = apply_guess(state, "10", "Easy")   # rejected
    assert dup["valid"] is False

    state, fresh = apply_guess(state, "12", "Easy")  # new number, accepted
    assert fresh["valid"] is True
    assert state["attempts"] == 2
    assert state["history"] == [10, 12]


def test_duplicate_winning_guess_after_wrong_repeat():
    """A repeated wrong guess is rejected, but guessing the (new) secret wins."""
    state = fresh_state(secret=15)
    state, _ = apply_guess(state, "10", "Easy")     # wrong, recorded
    state, dup = apply_guess(state, "10", "Easy")   # duplicate, rejected
    assert dup["valid"] is False
    state, win = apply_guess(state, "15", "Easy")   # correct
    assert win["valid"] is True
    assert win["outcome"] == "Win"
    assert state["status"] == "won"
