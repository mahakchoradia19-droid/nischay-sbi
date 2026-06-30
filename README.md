# YONO Nexus — the intelligence layer for SBI

**SBI Hackathon submission · Agentic AI for customer acquisition, digital adoption & engagement**
**Team:** Mahak Choradia

> SBI already owns the raw materials to leapfrog HDFC and ICICI — 500M customers,
> the largest transaction dataset in India, Jan Dhan rails, and YONO's install base.
> What's missing is the **intelligence layer** between those assets and the customer.
> **YONO Nexus is that layer** — five agents tied together by one transparent,
> self-evaluated score.

Everything here is **runnable today** with `python3` and the standard library — no
pip, no npm, no Docker, no cloud accounts. The agentic behaviour, the financial
maths, the compliance gate, and the metrics are **computed, not mocked**.

---

## The one idea

Most submissions are four disconnected demos. YONO Nexus is **one product with one
spine** — the **FinPulse Money Health Score**. Every agent reads from or writes to it:

```
  SCOUT            ONBOARDING          FINPULSE            SAARTHI            ACADEMY
  acquire    →     open account   →    score (0-100)  →   act on the    →    teach the
  the right        by voice,           transparent,       weakest            concept behind
  customer         self-healing KYC    self-evaluated     dimension          that dimension
     │                  │                   │                  │                  │
     └──────────────────┴─────── one customer, one score, one journey ──────────┘
```

A judge asking *"are these four things actually one system?"* gets a real answer:
the same six customers flow across all five pillars, and FinPulse is the shared
state they read and write.

### Two layers — and the second one is uncopyable

The five pillars above are the **individual layer** (one customer → one action).
HDFC and ICICI can copy them. The **community layer** cannot be copied:

> **SBI is the only bank that can see, and act on, the financial health of an entire
> village, cluster, or cohort** — because it is the custodian of India's financial
> infrastructure (Jan Dhan, the Aadhaar Payment Bridge, DBT). Private banks don't
> have the accounts, the rails, or the mandate.

The flagship of the community layer is the **DBT Gap Agent** ([`community/`](community/),
:8005): it finds the government credits about to bounce back to PFMS unclaimed across
whole districts, diagnoses *why*, drafts the fix, and measures the rescue — helping
citizens **receive money they are already owed** (not a cross-sell). See
[`docs/community-layer.md`](docs/community-layer.md).

---

## The five pillars

| # | Pillar | Dir | Port | What it does |
|---|--------|-----|------|--------------|
| 1 | **SCOUT** — Acquisition agent | [`scout/`](scout/) | 8002 | Identifies & scores prospects across 3 channels (dormant Jan Dhan, employer partnerships, life-event detection) and drafts hyper-personalised outreach. |
| 2 | **Onboarding** — Voice KYC agent | [`onboarding/`](onboarding/) | 8000 | Opens a compliant account by **voice conversation** (TTS + STT, multilingual), self-heals a name mismatch, and passes a **deterministic AML/KYC compliance gate**. |
| 3 | **FinPulse** — Money Health Score | [`finpulse/`](finpulse/) | 8004 | The unifying layer: a transparent 0-100 score from 7 weighted dimensions, top-3 actions, and an **Honest Metrics** self-evaluation (calibration curve, Brier, lift). |
| 4 | **SAARTHI** — Proactive engagement | [`engage/`](engage/) | 8003 | Watches financial rhythms and surfaces one timely nudge in the customer's language ("helps you before you ask"). |
| 5 | **FinSmart** — Literacy: Arena + Academy | [`finlearn/`](finlearn/) | 8001 | A voice tutor that teaches money in your language with **fresh, computed, never-repeating** questions; plus the gamified Arena. |
| ★ | **DBT Gap Agent** — Community layer (the moat) | [`community/`](community/) | 8005 | Cohort-scale agent that detects → diagnoses → acts on → measures government credits about to bounce back unclaimed. **HDFC/ICICI structurally cannot build this.** |

Shared infrastructure lives in [`security.py`](security.py) (CORS, rate-limiting,
input validation, PII masking, session TTL) — used by every pillar.

---

## Why this is different (and defensible)

Three things almost no competing team will show:

1. **Real compliance, not theatre.** Account creation passes a deterministic gate
   that *physically refuses* unless AML cleared and identity reconciled — even when
   the LLM drives the flow. Idempotent per PAN. (See [`onboarding/tools.py`](onboarding/tools.py).)

2. **Honest, self-evaluated metrics.** FinPulse scores *itself*: precision@k, lift
   over base rate, Brier score, and a **calibration curve** — and deliberately
   exposes raw accuracy as misleading. When a judge asks "are your numbers real?",
   the answer is a calibration chart. (See [`finpulse/evaluation.py`](finpulse/evaluation.py)
   and [`docs/scoring-model.md`](docs/scoring-model.md).)

3. **Voice-first, vernacular-first.** The onboarding agent and the Academy tutor
   *speak and listen* in the customer's language — English + Hindi fully offline,
   seven more via the live model, with an honest English fallback (never a faked
   translation).

---

## Quick start

Requirements: **Python 3.9+. Nothing else.** Best viewed in Chrome (voice uses the
Web Speech API). Start any pillar from the repo root:

```bash
python3 run_onboarding.py     # → http://localhost:8000   Onboarding (voice KYC)
python3 run_scout.py          # → http://localhost:8002   SCOUT (acquisition)
python3 run_engage.py         # → http://localhost:8003   SAARTHI (engagement)
python3 run_finpulse.py       # → http://localhost:8004   FinPulse (health score)
python3 run_community.py      # → http://localhost:8005   DBT Gap Agent (the moat)
cd finlearn && python3 game_server.py   # → http://localhost:8001/academy.html
```

**Suggested judge path:** FinPulse (`:8004`) first — pick a customer, read the
transparent breakdown, then open the **Honest Metrics** tab. Then watch the same
customer's story in Onboarding, SAARTHI, and the Academy.

### Optional AI enhancement
- `ANTHROPIC_API_KEY` — onboarding/SCOUT/SAARTHI hand the same tools to Claude
  (Opus 4.8), which plans and calls them itself. Without a key, a deterministic
  path produces identical user-facing output.
- `GEMINI_API_KEY` (free, no card) — activates the Academy's live tutor for the
  seven additional vernaculars and novel question scenarios.

Everything works fully **without any key**.

---

## Repository structure

```
SBI_hackathon/
├── README.md                 ← you are here
├── security.py               ← shared middleware (CORS, rate-limit, PII masking)
├── run_onboarding.py         ← root launchers (one per pillar)
├── run_scout.py
├── run_engage.py
├── run_finpulse.py
├── run_community.py
│
├── onboarding/               Pillar 2 — voice KYC agent (:8000)
│   ├── app.py  agent.py  tools.py
│   └── web/    (index.html, app.js, style.css)
├── scout/                    Pillar 1 — acquisition agent (:8002)
├── engage/                   Pillar 4 — SAARTHI proactive engagement (:8003)
├── finpulse/                 Pillar 3 — Money Health Score (:8004)
│   ├── app.py  finpulse.py  evaluation.py  profiles.py
│   └── web/
├── finlearn/                 Pillar 5 — FinSmart Arena + Academy (:8001)
│   ├── game_server.py  finance_math.py  question_engine.py  curriculum.py  ai_agents.py
│   └── web/    (index.html = Arena, academy.html = Academy)
├── community/                Community layer — DBT Gap Agent, the moat (:8005)
│   ├── app.py  dbt_engine.py
│   └── web/
│
├── docs/                     architecture · scoring model · product brief · community layer · structure
└── submission_pack/          judge quickstart, one-pager, demo script
```

Every pillar follows the **same shape** (`app.py` server · `agent.py`/engine ·
`tools.py` · `web/` frontend) so the repo is predictable to navigate.

---

## Documentation

- [`docs/product-brief.md`](docs/product-brief.md) — the thesis and the conversion loop.
- [`docs/architecture.md`](docs/architecture.md) — how the five pillars fit, the
  dual offline/live path, and the production mapping.
- [`docs/scoring-model.md`](docs/scoring-model.md) — the FinPulse transparent score
  and the self-evaluation methodology (the part that wins a hostile judge).
- [`docs/community-layer.md`](docs/community-layer.md) — the DBT Gap Agent and the
  uncopyable moat (the part that wins the *category*).
- [`docs/repo-structure.md`](docs/repo-structure.md) — naming conventions and a file map.
- Each pillar has its own `README.md` with run instructions and key files.

---

## Status & honesty

Built and verified: voice onboarding + real compliance gate; SCOUT; SAARTHI;
FinSmart Academy (real finance maths + procedural fresh-question engine, 1000-question
correctness sweep clean); FinPulse score + self-evaluation. All five pillars import
cleanly and serve over HTTP.

Synthetic-but-honest: customer profiles and the evaluation backtest are synthetic
and **labelled as such** — they exercise real algorithms (the score and the metrics
are computed, the same interfaces accept real warehouse data in production). We
report the unflattering metrics alongside the flattering ones on purpose.
