# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| | | | | |
| | | | | |
| | | | | |

---

## Linting & Style (Challenge 3: Professional Documentation and Style)

**Prompts used:**

Prompt 1 (docstrings):
```
Review every function in logic_utils.py and rewrite the docstrings to
professional grade: each one should have a one-line summary, a Parameters
block, and a Returns block with types and a description of every possible
return value. Keep them accurate to the current implementation.
```

Prompt 2 (linting):
```
Run flake8 on logic_utils.py and app.py and list every PEP 8 violation.
Then apply fixes to bring both files to zero warnings.
```

**Linting output before fixes:**

```
$ python3 -m flake8 logic_utils.py app.py
app.py:77:80: E501 line too long (81 > 79 characters)
logic_utils.py:37:80: E501 line too long (86 > 79 characters)
logic_utils.py:81:80: E501 line too long (80 > 79 characters)
logic_utils.py:103:80: E501 line too long (90 > 79 characters)
logic_utils.py:108:80: E501 line too long (105 > 79 characters)
logic_utils.py:110:80: E501 line too long (100 > 79 characters)
logic_utils.py:135:80: E501 line too long (104 > 79 characters)
logic_utils.py:144:80: E501 line too long (80 > 79 characters)
logic_utils.py:188:80: E501 line too long (80 > 79 characters)
logic_utils.py:207:80: E501 line too long (80 > 79 characters)
logic_utils.py:227:80: E501 line too long (81 > 79 characters)
```

**Linting output after fixes:**

```
$ python3 -m flake8 logic_utils.py app.py
(no output -- zero violations)
```

**Changes applied:**

All 11 violations were E501 (line too long). The AI identified two categories:

1. Inline comments that ran past column 79: moved the comment text to a
   dedicated line above the code it describes, which also makes the comments
   easier to read.

2. Docstring parameter and return description lines that were too wide: wrapped
   them at a natural phrase boundary to stay within 79 characters.

For docstrings, the AI rewrote every function in logic_utils.py to include a
one-line summary sentence, a Parameters block with type annotations and a
description per argument, and a Returns block that lists every possible return
value with its type and meaning. The existing docstrings already had this
structure; the AI tightened the wording and ensured every edge case in the
return values (for example, the (False, None, error) triple from parse_guess)
was explicitly documented.

One AI suggestion I did not apply: it proposed changing the inline FIX: comment
style to full block comments with a "Bug:" prefix. That would have changed the
meaning of the commit history comments, so I kept the existing comment style and
only reformatted the lines that were too long.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
