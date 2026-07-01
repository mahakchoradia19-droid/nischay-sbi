# SCOUT — Acquisition Agent (Pillar 1)

Turns SBI's data moat into a ranked, explainable prospect pipeline. SCOUT identifies
who to acquire across three channels and drafts hyper-personalised, compliance-checked
outreach.

## Run

```bash
python3 run_scout.py          # from repo root → http://localhost:8002
# live AI (optional): ANTHROPIC_API_KEY=sk-ant-... python3 run_scout.py
```

## Channels

- **Dormant Jan Dhan** — reactivate zero-balance PMJDY accounts (DBT-linked).
- **Employer partnership** — detect payroll outflow to competitor banks → corporate deal.
- **Life-event detection** — transaction patterns → a life moment → the right product.

## What to look at

Pick a prospect; the **Agent Reasoning Trace** runs `get_prospect_profile →
analyze_signals → score_prospect → generate_offer → log_outreach`. Different prospect
types route through different tool sequences — the agent reasons about which checks
matter, then produces a conversion probability, expected CLV, and a ready outreach
message in the prospect's language.

## Key files

| File | Role |
|---|---|
| `app.py` | server (`/api/pipeline`, `/api/analyse`) |
| `agent.py` | dual-path pipeline orchestrator + reasoning annotations |
| `tools.py` | prospect store + the 5 acquisition tools |
| `web/scout.js` | pipeline dashboard, prospect cards, trace panel |
