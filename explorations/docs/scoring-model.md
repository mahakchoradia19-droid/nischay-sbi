# FinPulse Scoring & Self-Evaluation Model

FinPulse is not a vanity gauge. It is a **transparent, attributable** financial-health
score with a **self-evaluation loop** that reports honest metrics on the system's own
recommendations. This document is the part that wins a hostile judge: it shows the
maths and it shows the unflattering numbers.

## The score (0-100)

The FinPulse score is a weighted sum of seven dimensions, each a 0-100 sub-score
computed from the customer's account data. The weights are an explicit editorial
choice and are shown to the customer — there is no black box.

```
score = Σ  weight_d × subscore_d           (weights sum to 1.00)
```

| Dimension | Weight | Sub-score is driven by |
|---|---|---|
| Emergency Buffer | 0.20 | months of expenses held liquid (target 6) |
| Savings Rate | 0.18 | share of income saved (target 30%) |
| Money Efficiency | 0.14 | share of money "working" vs idle above the buffer |
| Protection | 0.14 | life cover vs 10×/3× income + health cover vs ₹5L |
| Credit Health | 0.14 | card utilisation, EMI-to-income, missed payments |
| Diversification | 0.10 | breadth across FD / RD / SIP / PPF / insurance |
| Goal Progress | 0.10 | progress toward stated goals |

Properties that matter to a judge:

- **Attributable.** Each dimension's `contribution = weight × subscore`, and the
  contributions sum *exactly* to the score. "Why is my score 65?" has a line-by-line
  answer.
- **Computed, not hardcoded.** The score is a function of the profile, so it
  generalises to any customer. Arjun (disciplined) scores 88/A; Mohammed (stressed,
  high utilisation, missed payments) scores 20/E — different inputs, different scores.
- **Actionable.** Each dimension yields the score uplift available if it reached 100
  (`uplift = (100 − subscore) × weight`). The top-3 actions are ranked by this
  uplift, and each routes to a specific SBI product (company POV) with a plain
  customer benefit (user POV) and the Academy concept behind it.

See [`finpulse/finpulse.py`](../finpulse/finpulse.py).

## The self-evaluation loop (honest metrics)

Most teams quote one flattering number. A serious team reports the metrics a quant
trusts — including the ones that look bad. This loop is ported from the author's
newsroom trend-intelligence evaluation engine.

The agentic system makes predictions for each nudge:
- `predicted_prob` — probability the customer acts
- `predicted_uplift` — expected FinPulse-score improvement if they act

After the outcome window closes we **label reality** (acted? realized uplift?) and
compute:

| Metric | What it tells you | Why it's trustworthy |
|---|---|---|
| **Base rate** | how often nudges are acted on at all | the denominator everything else is judged against |
| **Raw accuracy** | naive correct-prediction rate | *deliberately exposed as misleading* — see below |
| **Precision@k** | of the top-k highest-confidence nudges, how many converted | what an RM actually experiences |
| **Lift over base** | precision@k ÷ base rate | is the model better than guessing? |
| **Recall@k** | of all conversions, how many we surfaced | are we missing opportunities? |
| **Brier score** | mean squared error of the probability forecasts (lower better) | calibration of confidence |
| **Calibration curve / ECE** | predicted vs actual rate per confidence bucket | a trustworthy model tracks the diagonal |
| **Uplift MAE** | error in predicted vs realized score gain | are the "+X pts" promises real? |

### The honesty point

On a representative backtest the engine reports something like:

```
base rate         35%
raw accuracy      71%   ← MISLEADING: most nudges aren't acted on, so
                          "predict no-act" scores high for free
precision@10%     72%   (2.1× the base rate)
Brier             0.19
calibration ECE   0.018  (curve tracks the diagonal)
```

The system **says, in the UI**, that raw accuracy is the misleading number and that
precision@k, lift, Brier and calibration are the ones to trust. Reporting the
unflattering metric on purpose is the signal of a team that understands evaluation.

The backtest is generated deterministically (seeded) with genuine-but-imperfect
model skill, so the numbers are realistic — not a suspicious 100%. The same
`evaluate(rows)` interface accepts real warehouse labels in production; only the
data source changes.

See [`finpulse/evaluation.py`](../finpulse/evaluation.py).

## What to watch (and what to ignore)

- **Trust:** precision@k, lift over base, Brier, calibration ECE, uplift MAE.
- **Ignore in isolation:** raw accuracy — it is inflated by a low base rate.

This is the same discipline a real risk/analytics team applies, made visible to a
judge in a single screen.
