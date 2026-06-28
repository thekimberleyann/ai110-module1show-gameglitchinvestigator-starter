# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Game purpose:** A number-guessing game where the player tries to identify a secret number within a set number of attempts. The difficulty setting controls the range (Easy: 1–20, Normal: 1–50, Hard: 1–100) and how many guesses are allowed.

**Bugs found:**
1. **Secret reset on every click:** Streamlit reruns the whole script on every interaction. The secret was generated with a bare `random.randint()` call, so it changed every time the player submitted a guess, making the game unwinnable.
2. **Inverted hints:** The `check_guess` function had the "Too High" and "Too Low" messages swapped. A guess above the secret told the player to go *higher*, and a guess below told them to go *lower*.
3. **Score calculation broken:** `update_score` gave a *bonus* of +5 on even-numbered wrong "Too High" guesses instead of subtracting 5. The win-score formula also had a stray `+ 1` that double-penalized late guesses.

**Fixes applied:**
1. Wrapped game state in `st.session_state` so the secret and attempt count survive across Streamlit reruns.
2. Swapped the return messages in `check_guess` so `guess > secret` returns "Go LOWER!" and `guess < secret` returns "Go HIGHER!".
3. Removed the even/odd branch in `update_score` so "Too High" always subtracts 5; removed the extra `+ 1` from the win-points formula.
4. Replaced `int(float(raw))` in `parse_guess` with `int(raw.strip())` so decimal inputs like `"3.7"` are rejected instead of silently truncated.
5. Added a range check in `apply_guess` so out-of-range guesses (e.g., `-5` on Easy) do not consume an attempt.

## 📸 Demo Walkthrough

1. Player opens the app and selects Normal difficulty (range 1-50, 8 attempts allowed).
2. The sidebar confirms the range and attempt limit; the secret is generated once and stored in session state and does not change between guesses.
3. Player enters 40 and submits. Secret is 33. Game returns "Go LOWER!" and the score drops by 5.
4. Player enters 20. Game returns "Go HIGHER!" and the score drops by 5 again.
5. Player enters 30. Game returns "Go HIGHER!" and the window narrows to 30-39.
6. Player enters 35. Game returns "Go LOWER!" and the window narrows to 30-34.
7. Player enters 33 Game returns "Correct!" with a balloon animation. Final score is calculated as `0 - 5 - 5 - 5 - 5 + (100 - 10x5) = -20 + 50 = 30` and displayed.
8. The "New Game" button resets the secret, score, attempts, and history to start fresh.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ pytest tests/ -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
collected 63 items

tests/test_game_logic.py::test_winning_guess_ported PASSED               [  1%]
tests/test_game_logic.py::test_guess_too_high_ported PASSED              [  3%]
tests/test_game_logic.py::test_guess_too_low_ported PASSED               [  4%]
tests/test_game_logic.py::test_bug1_attempts_init_is_zero[Easy] PASSED   [  6%]
tests/test_game_logic.py::test_bug1_attempts_init_is_zero[Normal] PASSED [  7%]
tests/test_game_logic.py::test_bug1_attempts_init_is_zero[Hard] PASSED   [  9%]
tests/test_game_logic.py::test_bug2_numeric_comparison_basic_outcomes PASSED [ 11%]
tests/test_game_logic.py::test_bug2_hints_stay_correct_across_sequence PASSED [ 12%]
tests/test_game_logic.py::test_bug3_secret_within_difficulty_range[Easy-1-20] PASSED [ 14%]
tests/test_game_logic.py::test_bug3_secret_within_difficulty_range[Hard-1-100] PASSED [ 15%]
tests/test_game_logic.py::test_bug3_secret_within_difficulty_range[Normal-1-50] PASSED [ 17%]
tests/test_game_logic.py::test_bug4_full_reset[Easy] PASSED              [ 19%]
tests/test_game_logic.py::test_bug4_full_reset[Normal] PASSED            [ 20%]
tests/test_game_logic.py::test_bug4_full_reset[Hard] PASSED              [ 22%]
tests/test_game_logic.py::test_bug5_get_range_for_difficulty[Easy-expected0] PASSED [ 23%]
tests/test_game_logic.py::test_bug5_get_range_for_difficulty[Normal-expected1] PASSED [ 25%]
tests/test_game_logic.py::test_bug5_get_range_for_difficulty[Hard-expected2] PASSED [ 26%]
tests/test_game_logic.py::test_bug5_get_range_default PASSED             [ 28%]
tests/test_game_logic.py::test_bug6_first_guess_win_score PASSED         [ 30%]
tests/test_game_logic.py::test_bug6_win_score_floor PASSED               [ 31%]
tests/test_game_logic.py::test_bug6_win_score_progression[1-90] PASSED   [ 33%]
tests/test_game_logic.py::test_bug6_win_score_progression[2-80] PASSED   [ 34%]
tests/test_game_logic.py::test_bug6_win_score_progression[5-50] PASSED   [ 36%]
tests/test_game_logic.py::test_bug6_win_score_progression[9-10] PASSED   [ 38%]
tests/test_game_logic.py::test_bug6_win_score_progression[10-10] PASSED  [ 39%]
tests/test_game_logic.py::test_bug6_win_score_progression[50-10] PASSED  [ 41%]
tests/test_game_logic.py::test_bug7_too_high_consistent_penalty_even_and_odd PASSED [ 42%]
tests/test_game_logic.py::test_bug7_too_low_penalty PASSED               [ 44%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[1] PASSED [ 46%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[2] PASSED [ 47%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[3] PASSED [ 49%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[4] PASSED [ 50%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[5] PASSED [ 52%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[6] PASSED [ 53%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[7] PASSED [ 55%]
tests/test_game_logic.py::test_bug7_too_high_penalty_every_attempt[8] PASSED [ 57%]
tests/test_game_logic.py::test_bug8_invalid_input_does_not_consume_attempt[abc] PASSED [ 58%]
tests/test_game_logic.py::test_bug8_invalid_input_does_not_consume_attempt[] PASSED [ 60%]
tests/test_game_logic.py::test_bug8_invalid_input_does_not_consume_attempt[None] PASSED [ 61%]
tests/test_game_logic.py::test_bug9_invalid_input_not_logged_to_history[abc] PASSED [ 65%]
tests/test_game_logic.py::test_bug9_invalid_input_not_logged_to_history[] PASSED [ 65%]
tests/test_game_logic.py::test_bug9_invalid_input_not_logged_to_history[None] PASSED [ 66%]
tests/test_game_logic.py::test_bug10_too_high_says_lower PASSED          [ 68%]
tests/test_game_logic.py::test_bug10_too_low_says_higher PASSED          [ 69%]
tests/test_game_logic.py::test_bug11_loss_exactly_after_full_limit_hard PASSED [ 71%]
tests/test_game_logic.py::test_bug12_win_detection_sets_won_status PASSED [ 73%]
tests/test_game_logic.py::test_bug12_apply_guess_does_not_mutate_input_state PASSED [ 74%]
tests/test_game_logic.py::test_bugA_parse_guess_rejects_non_integers[3.7] PASSED [ 76%]
tests/test_game_logic.py::test_bugA_parse_guess_rejects_non_integers[3.0] PASSED [ 77%]
tests/test_game_logic.py::test_bugA_parse_guess_rejects_non_integers[-2.5] PASSED [ 79%]
tests/test_game_logic.py::test_bugA_parse_guess_rejects_non_integers[1e2] PASSED [ 80%]
tests/test_game_logic.py::test_bugA_parse_guess_rejects_non_integers[abc] PASSED [ 82%]
tests/test_game_logic.py::test_bugA_parse_guess_accepts_whole_numbers[5-5] PASSED [ 84%]
tests/test_game_logic.py::test_bugA_parse_guess_accepts_whole_numbers[20-20] PASSED [ 85%]
tests/test_game_logic.py::test_bugA_parse_guess_accepts_whole_numbers[ 7 -7] PASSED [ 87%]
tests/test_game_logic.py::test_bugA_parse_guess_accepts_whole_numbers[-3--3] PASSED [ 88%]
tests/test_game_logic.py::test_bugB_negative_guess_rejected_out_of_range PASSED [ 90%]
tests/test_game_logic.py::test_bugB_too_large_guess_rejected_out_of_range PASSED [ 92%]
tests/test_game_logic.py::test_bugB_decimal_guess_rejected_invalid PASSED [ 93%]
tests/test_game_logic.py::test_bugB_in_range_integer_accepted_and_consumes_attempt PASSED [ 95%]
tests/test_game_logic.py::test_duplicate_guess_rejected PASSED           [ 96%]
tests/test_game_logic.py::test_duplicate_guess_does_not_block_new_numbers PASSED [ 98%]
tests/test_game_logic.py::test_duplicate_winning_guess_after_wrong_repeat PASSED [100%]

============================== 63 passed in 0.37s ==============================
```

## Stretch Features

**Challenge 3: Professional Documentation and Style**

- Added professional docstrings to every function in `logic_utils.py`, each with a one-line summary, a Parameters block (types + descriptions), and a Returns block covering every possible return value.
- Ran `flake8` on `logic_utils.py` and `app.py`; resolved all 11 E501 line-length violations by wrapping long comments and docstring lines at natural phrase boundaries.
- Prompts used and full before/after linting output are recorded in `ai_interactions.md`.
