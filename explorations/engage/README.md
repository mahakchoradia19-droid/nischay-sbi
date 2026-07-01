# SAARTHI — Proactive Engagement Agent (Pillar 4)

"Saarthi" (सारथी) = the charioteer who guides. SAARTHI watches a customer's financial
rhythms and surfaces **one** timely nudge in their language — *before* they ask.

## Run

```bash
python3 run_engage.py         # from repo root → http://localhost:8003
# live AI (optional): ANTHROPIC_API_KEY=sk-ant-... python3 run_engage.py
```

## What to look at

Pick a customer; SAARTHI reads the pattern and a YONO push notification drops onto a
phone mockup. Five scenarios, each routing through a different tool sequence:

- **EMI shortfall** — sweep ₹800 from FD before a bounce (the narrative's peak).
- **Education planning** — quarterly school fee → Child Education SIP.
- **Salary → SIP** — reinforce the saving habit on payday.
- **Idle balance** — computed opportunity cost → FD.
- **Hardship support** — salary gap → relief options, *not* a cross-sell.

## Key files

| File | Role |
|---|---|
| `app.py` | server (`/api/customers`, `/api/analyse`) |
| `agent.py` | per-scenario tool routing + the proactive reasoning |
| `tools.py` | customer store + 8 engagement tools (snapshot, scan, obligations, shortfall, funding, opportunity cost, recommend, execute) |
| `web/engage.js` | phone-mockup notification + trace panel |

The customers here are the same people scored by FinPulse — SAARTHI acts on the
weakest FinPulse dimension.
