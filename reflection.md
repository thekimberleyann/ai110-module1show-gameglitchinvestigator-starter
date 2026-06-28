# Reflection: Game Glitch Investigator

## 1. What was broken when you started?

When I first ran the game, three things were immediately wrong. The secret number kept changing every single time I clicked "Submit"; I could watch it flip around in the Developer Debug Info panel, so it was impossible to ever guess the right number. On top of that, the hints were completely backwards: when my guess was too high the game told me to go higher, and when my guess was too low it told me to go lower. The score was also misbehaving: on even-numbered attempts a wrong "Too High" guess would actually add points instead of subtracting them, which made no sense.

**Bug Reproduction Log**

| Input Used | Expected Behavior | Actual Behavior | Console Output / Error |
|------------|-------------------|-----------------|------------------------|
| Any guess (e.g., 40 on Normal) | Secret stays fixed for the whole game so the player can eventually win | Secret re-randomized on every Streamlit rerun; "Developer Debug Info" shows a new secret after each click | No error shown -- it just silently reset every time I clicked |
| Guess of 60 when secret is 50 (Too High) | Hint reads "Go LOWER!" | Hint read "Go HIGHER!", pointing me in the completely wrong direction | No error shown |
| Guess of "3.7" (decimal input) | Error message saying decimals are not allowed | It just used 3 instead of what I typed without telling me -- I didn't even notice at first | No error shown |

---

## 2. How did you use AI as a teammate?

I used Claude (via Claude Code in VS Code) as my primary AI assistant throughout the project. I attached both `app.py` and `logic_utils.py` to give it full context before asking questions or requesting changes.

**Correct AI suggestion: inverted hints fix**

I described the hint bug and asked Claude to explain the logic in `check_guess`. It identified that the return values for "Too High" and "Too Low" had their messages swapped: the `"Too High"` branch returned `"Go HIGHER!"` and the `"Too Low"` branch returned `"Go LOWER!"`, which is the exact opposite of what a number-guessing game needs. Claude suggested swapping the message strings so that `guess > secret` returns `"Go LOWER!"` and `guess < secret` returns `"Go HIGHER!"`. I traced through the logic myself to check -- if my guess is 60 and the secret is 50, then 60 > 50 means my guess is too high, so I need to go *lower*. That confirmed the fix made sense. Then I ran the tests and both `test_bug10_too_high_says_lower` and `test_bug10_too_low_says_higher` passed, which felt like solid confirmation.

**Incorrect or misleading AI suggestion: wrong fix for the session-state bug**

When I described the secret-resetting problem, Claude's first suggestion was to use `@st.cache_data` on the random-number generation function. I wasn't immediately sure that was wrong, but something felt off. From what I read in the Streamlit docs, `st.cache_data` would basically give every player the same cached number -- which would be even worse than the original bug. I wasn't 100% certain at first, but the docs backed it up, so I rejected it. The actual fix was to check whether `"game"` already exists in `st.session_state` before creating a new game state, so the secret only gets generated once per session. I verified it worked by watching the secret in the debug panel stay constant across multiple guess submissions.

---

## 3. Debugging and testing your fixes

I wasn't confident a bug was actually fixed until two things checked out: I could play the game and it worked the way it should, AND the relevant tests went green. Using just one of those didn't feel like enough, playing the game could miss edge cases, and a passing test doesn't guarantee the UI wired things up correctly.

For the inverted-hint bug, I ran `pytest tests/ -v` after the fix and watched `test_bug10_too_high_says_lower` and `test_bug10_too_low_says_higher` both go green. The test for "Too High" calls `check_guess(60, 50)` and checks that `"LOWER"` appears in the message, which is simple enough that it's hard to accidentally pass if the swap is still wrong.

For the decimal-input bug (where `"3.7"` used to silently become `3`), I asked Claude to generate a parametrized test that fed several non-integer strings to `parse_guess` and checked that `ok is False`. Claude produced `test_bugA_parse_guess_rejects_non_integers`, which covers `"3.7"`, `"3.0"`, `"-2.5"`, `"1e2"`, and `"abc"`. Claude also helped me understand why the old code failed: `int(float("3.7"))` evaluates to `3` in Python without throwing any error, so the original code had no idea a decimal was entered.

---

## 4. What did you learn about Streamlit and state?

The way I started thinking about it: `st.session_state` is basically like the app has a little memory tied to your browser tab specifically. Every time you interact with the page -- click a button, submit a form -- Streamlit reruns the whole script from the top. So any normal variable just gets recreated with a new value every time. That's why the secret kept changing. `st.session_state` is the way out of that; it holds onto values across reruns for that specific session. It took me a bit to really get why that mattered, but once it clicked the fix made total sense: just check `if "game" not in st.session_state` before creating a new game, so the secret only gets rolled once.

---

## 5. Looking ahead: your developer habits

One habit I want to carry forward is writing a targeted test right after fixing a bug, before moving on. It takes a few minutes but means the bug can't sneak back in silently; future me will get a clear failing test instead of some mysterious gameplay complaint. The parametrized tests for the decimal-input edge cases were especially useful because they covered five variations with almost no extra code.

If I were doing this again, I would be more skeptical of the first AI suggestion whenever it involves a framework-specific concept like Streamlit session state. Claude's `st.cache_data` answer sounded plausible but was wrong for this situation. Next time I'll ask a follow-up before applying it: "Is there a scenario where this makes things worse?"

This project changed how I think about AI-generated code. I used to assume that if the AI gave a confident answer it was probably right. Now I actually read through what it gives me before applying it, which sounds obvious -- but I wasn't really doing that before. Treating AI output the way I'd treat code from someone else, actually checking it instead of just trusting it, is something I want to keep doing.
