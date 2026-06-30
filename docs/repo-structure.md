# Repository Structure & Conventions

## Naming conventions

- **One directory per pillar**, lowercase, named for the product (`onboarding/`,
  `scout/`, `engage/`, `finpulse/`, `finlearn/`).
- **Same file shape in each pillar:**
  - `app.py` — the stdlib HTTP server / entry point for that pillar.
  - `agent.py` — the agent orchestrator (offline state machine + live tool-loop),
    where applicable.
  - `tools.py` — the typed tool layer the agent calls (the only place that touches
    "external systems").
  - `web/` — the vanilla HTML/CSS/JS frontend (`index.html`, plus a pillar-named JS).
- **Root launchers:** `run_<pillar>.py` — a tiny shim that puts the repo root and
  the pillar dir on `sys.path`, `chdir`s into the pillar, and calls `app.main()`.
  This lets every pillar start from the repo root with one command.
- **Shared code at the root:** `security.py` (middleware used by all pillars).

## File map

```
SBI_hackathon/
├── README.md                     project front door
├── security.py                   shared middleware (CORS, rate-limit, validation,
│                                  PII masking, session TTL)
│
├── run_onboarding.py             root launchers (one per pillar)
├── run_scout.py
├── run_engage.py
├── run_finpulse.py
│
├── onboarding/                   :8000  voice KYC agent
│   ├── app.py                    stdlib server + JSON API
│   ├── agent.py                  dual-path orchestrator + bilingual copy
│   ├── tools.py                  OCR, PAN/AML, fuzzy matcher, compliance gate
│   └── web/  index.html app.js style.css
│
├── scout/                        :8002  acquisition agent
│   ├── app.py  agent.py  tools.py
│   └── web/  index.html scout.js style.css
│
├── engage/                       :8003  SAARTHI proactive engagement
│   ├── app.py  agent.py  tools.py
│   └── web/  index.html engage.js style.css
│
├── finpulse/                     :8004  Money Health Score (the unifying spine)
│   ├── app.py                    serves /api/cohort, /api/score, /api/evaluation
│   ├── finpulse.py               transparent weighted score engine
│   ├── evaluation.py             self-evaluation / honest metrics
│   ├── profiles.py               synthetic-but-consistent customers
│   └── web/  index.html app.js style.css
│
├── finlearn/                     :8001  FinSmart Arena + Academy
│   ├── game_server.py            server (Arena APIs + /api/academy/*)
│   ├── finance_math.py           real calculators
│   ├── question_engine.py        procedural fresh-question generator
│   ├── curriculum.py             lessons + spoken tutor scripts
│   ├── ai_agents.py              TutorAgent + generators (offline fallback)
│   ├── game_data.py              Arena content (badges, levels, scenarios)
│   └── web/  index.html (Arena)  academy.html (Academy)  *.js  *.css
│
├── docs/                         architecture · scoring-model · product-brief · this file
└── submission_pack/              judge quickstart, one-pager, demo script, etc.
```

## How to add a pillar (the pattern)

1. Create `newpillar/` with `app.py` (copy an existing stdlib server), `agent.py`/
   engine, `tools.py`, and `web/`.
2. Import shared middleware: `sys.path.insert(0, repo_root)` then `import security`.
3. Add `run_newpillar.py` at the root.
4. Pick the next free port and document it in the README table.

## Ports

| Port | Pillar |
|---|---|
| 8000 | Onboarding |
| 8001 | FinSmart (Arena + Academy) |
| 8002 | SCOUT |
| 8003 | SAARTHI |
| 8004 | FinPulse |
