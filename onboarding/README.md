# Onboarding — Voice KYC Agent (Pillar 2)

Opens a compliant SBI savings account through a **voice conversation**, not a
14-screen form. The agent speaks each step, listens for spoken answers, self-heals
a name mismatch between Aadhaar and PAN, and passes a deterministic compliance gate.

## Run

```bash
python3 run_onboarding.py     # from repo root → http://localhost:8000
# live AI (optional): ANTHROPIC_API_KEY=sk-ant-... python3 run_onboarding.py
```
Best in Chrome — voice uses the Web Speech API (TTS + STT). English + Hindi work
fully offline; 7 more vernaculars activate with a live key (honest English fallback
otherwise).

## What to look at

- Tap 🎤 and say "I'd like to open an account" — the agent talks you through it.
- The **Agent Reasoning Trace** panel: `ocr_extract → validate_pan` (real fuzzy
  score) → name-mismatch self-heal → `ckyc_lookup → aml_screen` → **Compliance gate**
  → `create_account`.
- **Live Metrics**: 7 fields auto-extracted, 1 asked, 0 human handoffs, straight-through.

## Key files

| File | Role |
|---|---|
| `app.py` | stdlib server + JSON API (`/api/start`, `/api/message`) |
| `agent.py` | dual-path orchestrator (offline state machine + live Claude tool-loop), bilingual copy, language handling |
| `tools.py` | `ocr_extract`, `validate_pan` (real fuzzy matcher), `ckyc_lookup`, `aml_screen` (real watchlist), `create_account` (**deterministic gate + idempotency**) |
| `web/app.js` | voice engine (TTS/STT), document capture, trace + metrics rendering |

## The defensible bit

`create_account` refuses unless `aml_decision == "CLEAR"` and `identity_reconciled`
— the LLM cannot bypass it — and is idempotent per PAN. The fuzzy matcher and AML
watchlist are real algorithms, so behaviour generalises to any name.
