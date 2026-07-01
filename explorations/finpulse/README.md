# FinPulse — Money Health Score (Pillar 3, the unifying spine)

One transparent number (0-100) that ties the whole of YONO Nexus together, plus a
self-evaluation engine that reports **honest** metrics on the system's own
recommendations. Full methodology: [`../docs/scoring-model.md`](../docs/scoring-model.md).

## Run

```bash
python3 run_finpulse.py       # from repo root → http://localhost:8004
```
No API key needed — everything is computed.

## What to look at

1. **Score tab** — pick a customer. The animated ring shows the score; the breakdown
   shows all 7 dimensions with their weight, contribution and a plain "why". The
   contributions sum exactly to the score. Each dimension deep-links to the Academy
   lesson behind it. The top-3 actions are ranked by score uplift and route to SBI
   products.
2. **Honest Metrics tab** — the self-evaluation: base rate, precision@k, lift, Brier,
   a **calibration curve** drawn in SVG, per-nudge conversion, and a note that openly
   flags raw accuracy as misleading.

## Key files

| File | Role |
|---|---|
| `finpulse.py` | transparent weighted score (7 dimensions, attributable) |
| `evaluation.py` | self-evaluation over a labelled backtest (honest metrics) |
| `profiles.py` | 6 synthetic-but-consistent customers (shared with SCOUT/SAARTHI) |
| `app.py` | server (`/api/cohort`, `/api/score`, `/api/evaluation`) |
| `web/app.js` | score ring, dimension breakdown, SVG calibration chart |

## The defensible bit

The score is computed and attributable (survives "show me the maths"), and the system
grades itself with a calibration curve and a Brier score (survives "are your metrics
real?"). The backtest is synthetic and labelled as such; the same interface accepts
real warehouse labels in production.
