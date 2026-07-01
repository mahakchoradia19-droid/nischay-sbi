# FinSmart — Literacy: Arena + Academy (Pillar 5)

Two front doors to financial literacy on one server:
- **Academy** (`/academy.html`) — a **voice tutor** that teaches money in your
  language, with fresh, computed, never-repeating questions. The flagship.
- **Arena** (`/index.html`) — the gamified quiz experience (badges, XP, streaks).

## Run

```bash
cd finlearn && python3 game_server.py     # → http://localhost:8001
#   Academy:  http://localhost:8001/academy.html
#   Arena:    http://localhost:8001/index.html
# live tutor (optional, free): GEMINI_API_KEY=... python3 game_server.py
```
Best in Chrome (voice). English + Hindi tutor scripts work offline.

## What to look at (Academy)

Pick a topic → the tutor **teaches the lesson aloud** → "Practice" gives
procedurally-generated questions; it **reads each question and the explanation**.
The quiz is adaptive (prioritises your weakest concept) and tracks mastery/XP.

## Why it's genuinely valuable

- `finance_math.py` — real calculators (SI/CI, FD/RD/PPF, EMI reducing,
  flat-vs-reducing unmasking, inflation, real return, credit-card APR, min-due trap).
- `question_engine.py` — **infinite fresh MCQs whose answers are computed** (a
  1000-question sweep produced 0 wrong keys and 0 duplicate options); distractors are
  built from real mistakes.
- `curriculum.py` — 6 modules / 15 lessons (CASA, FD/RD, DICGC deposit insurance,
  cards, payments, loans, govt schemes) with spoken tutor scripts (6 in Hindi).

## Key files

| File | Role |
|---|---|
| `game_server.py` | server (Arena APIs + `/api/academy/*`) |
| `finance_math.py` | real financial calculators |
| `question_engine.py` | procedural fresh-question generator |
| `curriculum.py` | lessons + spoken tutor scripts |
| `ai_agents.py` | TutorAgent + generators (Gemini-backed, offline fallback) |
| `web/academy.html` / `academy.js` | the voice Academy |
| `web/index.html` / `game.js` | the Arena |

Each FinPulse dimension deep-links into the matching Academy lesson (`#lesson_id`),
closing the score → learn loop.
