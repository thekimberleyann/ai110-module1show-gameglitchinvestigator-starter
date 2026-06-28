"""Pure game logic for the Glitch Investigator guessing game.

This module is the "functional core": it contains all game rules and
state transitions and has no dependency on Streamlit or any UI. app.py is
the thin "imperative shell" that reads widgets, calls into here, and renders.
"""

import random


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive (low, high) number range for a difficulty level.

    Parameters:
        difficulty (str): The difficulty name ("Easy", "Normal", or "Hard").

    Returns:
        tuple[int, int]: A (low, high) pair. "Easy" gives (1, 20),
        "Normal" gives (1, 50), "Hard" gives (1, 100), and any
        unrecognized value defaults to (1, 100).
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def get_attempt_limit(difficulty: str):
    """Return the number of guesses allowed for a difficulty level.

    Parameters:
        difficulty (str): The difficulty name ("Easy", "Normal", or "Hard").

    Returns:
        int: Allowed attempts. "Easy" gives 6, "Normal" gives 7,
        "Hard" gives 8; any unrecognized value defaults to 7. The limits
        scale with the number range so harder difficulties (wider ranges)
        allow more guesses while staying tighter relative to the range.
    """
    limits = {
        "Easy": 6,
        "Normal": 7,
        "Hard": 8,
    }
    return limits.get(difficulty, 7)


def parse_guess(raw: str):
    """Parse a raw guess string into an integer.

    Parameters:
        raw (str): The raw user input. May be None or empty.

    Returns:
        tuple[bool, int | None, str | None]: A (ok, value, error) triple.
        On success returns (True, int_value, None). If the input is None
        or empty returns (False, None, "Enter a guess."). Only whole
        numbers are accepted: anything that is not a plain integer
        (decimals like "3.7" or "3.0", scientific notation like "1e2",
        or non-numeric text like "abc") returns
        (False, None, "Please enter a whole number."). Surrounding
        whitespace is ignored. This function is range-agnostic; bounds
        are enforced by the caller (see apply_guess).
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    # Parsing with int() directly rejects "3.7", "3.0", "1e2", and "abc"
    # while still accepting whitespace-padded whole numbers and negatives.
    try:
        value = int(raw.strip())
    except Exception:
        return False, None, "Please enter a whole number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret and report the outcome.

    Parameters:
        guess (int): The player's guessed number.
        secret (int): The secret number to compare against.

    Returns:
        tuple[str, str]: An (outcome, message) pair. Outcome is "Win",
        "Too High", or "Too Low", each with a matching display message.
    """
    if guess == secret:
        return "Win", "Correct!"

    if guess > secret:
        # Guess is above the secret, so the player must go lower.
        return "Too High", "Go LOWER!"

    # Guess is below the secret, so the player must go higher.
    return "Too Low", "Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Compute the new score after a guess based on its outcome.

    Parameters:
        current_score (int): The player's score before this guess.
        outcome (str): The result of the guess ("Win", "Too High",
            "Too Low", or anything else).
        attempt_number (int): The current attempt count.

    Returns:
        int: The updated score. A "Win" adds 100 - 10 * attempt_number,
        floored at a minimum of 10 points. "Too High" and "Too Low" each
        subtract 5. Any other outcome leaves the score unchanged.
    """
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def new_game_state(difficulty: str) -> dict:
    """Create a fresh game-state dict for the given difficulty.

    Parameters:
        difficulty (str): The difficulty name ("Easy", "Normal", or "Hard").

    Returns:
        dict: A new game state with keys:
            secret (int): the number to guess, drawn from the difficulty
                range,
            attempts (int): guesses used so far (starts at 0),
            score (int): current score (starts at 0),
            status (str): "playing", "won", or "lost" (starts "playing"),
            history (list[int]): valid guesses made so far (starts empty).
    """
    low, high = get_range_for_difficulty(difficulty)
    return {
        "secret": random.randint(low, high),
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
    }


def apply_guess(state: dict, raw_guess: str, difficulty: str):
    """Resolve a single guess against the current game state.

    This is a pure transition: it does not mutate the input state,
    returning a new state instead. It validates the input, enforces the
    difficulty's number range, advances attempts/score/history, determines
    the higher/lower hint, and sets the win/lost status.

    Parameters:
        state (dict): The current game state (see new_game_state).
        raw_guess (str): The raw text the player entered.
        difficulty (str): The active difficulty (used for the number
            range and the attempt limit).

    Returns:
        tuple[dict, dict]: (new_state, result) where result has keys:
            valid (bool): whether the input parsed as a number, fell
                within the difficulty's [low, high] range, AND was not
                already guessed,
            error (str | None): the validation error message if invalid,
            outcome (str | None): "Win", "Too High", or "Too Low" if
                valid,
            message (str | None): the matching hint message if valid.
        On invalid input (failed parse, out of range, or duplicate) the
        state is returned unchanged: no attempt consumed, nothing added
        to history, score and status untouched.
    """
    new_state = dict(state)

    ok, guess_int, err = parse_guess(raw_guess)
    if not ok:
        return new_state, {
            "valid": False,
            "error": err,
            "outcome": None,
            "message": None,
        }

    # Out-of-range guesses are treated as invalid input: the state is
    # returned unchanged so no attempt is consumed. parse_guess is kept
    # range-agnostic; the range check lives here.
    low, high = get_range_for_difficulty(difficulty)
    if guess_int < low or guess_int > high:
        return new_state, {
            "valid": False,
            "error": f"Your guess must be between {low} and {high}.",
            "outcome": None,
            "message": None,
        }

    # Reject a number the player has already guessed so duplicates do
    # not waste an attempt or produce a redundant hint.
    if guess_int in new_state["history"]:
        return new_state, {
            "valid": False,
            "error": (
                f"You already guessed {guess_int}. "
                "Try a different number."
            ),
            "outcome": None,
            "message": None,
        }

    new_state["attempts"] = new_state["attempts"] + 1
    new_state["history"] = new_state["history"] + [guess_int]

    outcome, message = check_guess(guess_int, new_state["secret"])
    new_state["score"] = update_score(
        new_state["score"], outcome, new_state["attempts"]
    )

    if outcome == "Win":
        new_state["status"] = "won"
    elif new_state["attempts"] >= get_attempt_limit(difficulty):
        new_state["status"] = "lost"

    return new_state, {
        "valid": True,
        "error": None,
        "outcome": outcome,
        "message": message,
    }
