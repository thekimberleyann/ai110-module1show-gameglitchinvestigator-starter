import streamlit as st

# This file is the thin "imperative shell": it only reads widgets, calls into
# logic_utils for all game rules/state transitions, and renders the result.
# All game logic now lives in logic_utils.py — Claude (agent mode).
from logic_utils import (
    get_range_for_difficulty,
    get_attempt_limit,
    new_game_state,
    apply_guess,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

low, high = get_range_for_difficulty(difficulty)
attempt_limit = get_attempt_limit(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# Single source of truth: the whole game state lives in one dict built by
# logic_utils.new_game_state (secret, attempts, score, status, history).
if "game" not in st.session_state:
    st.session_state.game = new_game_state(difficulty)

game = st.session_state.game

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - game['attempts']}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", game["secret"])
    st.write("Attempts:", game["attempts"])
    st.write("Score:", game["score"])
    st.write("Difficulty:", difficulty)
    st.write("History:", game["history"])

# Form so pressing Enter submits the guess (not just the Submit button).
with st.form(key=f"guess_form_{difficulty}", clear_on_submit=True):
    raw_guess = st.text_input("Enter your guess:")
    submit = st.form_submit_button("Submit Guess 🚀")

col2, col3 = st.columns(2)
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.game = new_game_state(difficulty)
    st.success("New game started.")
    st.rerun()

if game["status"] != "playing":
    if game["status"] == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    # All turn resolution (validation, scoring, win/lose) is in logic_utils.
    game, result = apply_guess(game, raw_guess, difficulty)
    st.session_state.game = game

    if not result["valid"]:
        st.error(result["error"])
    else:
        if show_hint:
            st.warning(result["message"])

        if result["outcome"] == "Win":
            st.balloons()
            st.success(
                f"You won! The secret was {game['secret']}. "
                f"Final score: {game['score']}"
            )
        elif game["status"] == "lost":
            st.error(
                f"Out of attempts! "
                f"The secret was {game['secret']}. "
                f"Score: {game['score']}"
            )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
