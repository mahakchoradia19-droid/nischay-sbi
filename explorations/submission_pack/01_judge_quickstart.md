# Judge Quickstart (60 seconds)

This runbook is meant for judges and evaluators.
It minimizes setup and gets all core demos live fast.

## Prerequisites

- Python `3.9+`
- No `pip`, no `npm`, no Docker required

## Start the demos

From repository root:

```bash
# Terminal 1: Onboarding Agent (port 8000)
python3 app.py
```

```bash
# Terminal 2: Financial Literacy Game (port 8001)
cd finlearn && python3 app.py
```

```bash
# Terminal 3: Acquisition Agent (port 8002)
python3 run_scout.py
```

```bash
# Terminal 4: Proactive Engagement Agent (port 8003)
python3 run_engage.py
```

## Open in browser

- `http://localhost:8000` → YONO Nexus Onboarding
- `http://localhost:8001` → FinSmart Arena
- `http://localhost:8002` → SCOUT Acquisition Agent
- `http://localhost:8003` → SAARTHI Engagement Agent

## 90-second validation checklist

1. Onboarding (`8000`): click `Upload Aadhaar + PAN`, confirm identity, select occupation, verify account created with trace and live metrics.
2. FinSmart (`8001`): start one quiz and verify points/streak/badges update.
3. SCOUT (`8002`): select any prospect and verify 5-step tool trace + generated outreach.
4. SAARTHI (`8003`): select any customer and verify proactive nudge + reasoning trace.

## Optional AI enhancement (not required for demo)

```bash
# Optional: live Claude for onboarding/scout/engage
export ANTHROPIC_API_KEY=your_key

# Optional: live Gemini for FinSmart personalization
export GEMINI_API_KEY=your_key
```

Without keys, all demos still run with deterministic offline behavior.
