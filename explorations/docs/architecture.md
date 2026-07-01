# Architecture — YONO Nexus

## Principles

1. **Zero-setup.** Python standard library only. Every pillar starts in seconds with
   one command, no pip/npm/Docker. Demo-room reliability is a feature.
2. **One shape per pillar.** Each pillar is `app.py` (stdlib HTTP server) + an
   engine (`agent.py` / `finpulse.py` / `game_server.py`) + `tools.py` + a `web/`
   frontend (vanilla HTML/CSS/JS). Predictable to read and extend.
3. **Dual path, identical contract.** Agentic pillars run a deterministic offline
   path AND, when an API key is present, hand the *same tools* to a frontier model
   that plans and calls them itself. The UI output is identical, so a demo never
   depends on the network.
4. **One spine.** FinPulse is the shared state. The same customers appear across
   pillars so the system reads as one product.

## System map

```
                         ┌────────────────────────────────────────────┐
                         │                FinPulse (:8004)             │
                         │   transparent score · self-evaluation       │
                         │   profiles.py  finpulse.py  evaluation.py    │
                         └───────▲───────────────┬───────────▲─────────┘
                                 │ scores         │ weakest    │ concept
                                 │                ▼ dimension   │ to teach
   ┌──────────────┐   ┌──────────┴─────┐   ┌──────┴───────┐   ┌┴─────────────┐
   │ SCOUT :8002  │──►│ Onboarding     │   │ SAARTHI :8003│   │ FinSmart     │
   │ acquisition  │   │ :8000 voice KYC│   │ engagement   │   │ :8001 learn  │
   │ agent.py     │   │ agent.py       │   │ agent.py     │   │ academy +    │
   │ tools.py     │   │ tools.py       │   │ tools.py     │   │ arena        │
   └──────────────┘   └────────┬───────┘   └──────────────┘   └──────────────┘
                               │
                      ┌────────▼────────┐
                      │  security.py    │  CORS · rate-limit · input validation
                      │  (shared)       │  · PII masking · session TTL
                      └─────────────────┘
```

## Per-pillar internals

### Onboarding (`onboarding/`, :8000)
- `agent.py` — dual-path orchestrator. Offline: a goal state-machine
  (`await_docs → await_identity_confirm → await_occupation → done`). Live: a bounded
  Claude tool-loop over the same `tools.py` schemas.
- `tools.py` — `ocr_extract`, `validate_pan` (real fuzzy matcher), `ckyc_lookup`,
  `aml_screen` (real sanctions/PEP watchlist), `create_account` (**deterministic
  compliance gate** + per-PAN idempotency).
- Voice: `web/app.js` uses the Web Speech API for TTS (the agent speaks) and STT
  (it listens); language drives both. English/Hindi offline; 7 more via the live model.

### SCOUT (`scout/`, :8002)
- 5-tool pipeline: `get_prospect_profile → analyze_signals → score_prospect →
  generate_offer → log_outreach`. Different prospect types route through different
  tool sequences — the agent reasons about which checks matter.

### SAARTHI (`engage/`, :8003)
- Watches a customer's patterns and runs a scenario-specific tool sequence
  (`snapshot → scan → obligations → shortfall → funding → recommend → execute`),
  surfacing exactly one timely nudge in the customer's language.

### FinPulse (`finpulse/`, :8004)
- `finpulse.py` — the transparent weighted score (see `scoring-model.md`).
- `evaluation.py` — the self-evaluation engine (honest metrics over a labelled backtest).
- `profiles.py` — synthetic-but-consistent customers shared with SCOUT/SAARTHI.

### FinSmart (`finlearn/`, :8001)
- `finance_math.py` — real calculators. `question_engine.py` — procedural,
  always-correct fresh questions. `curriculum.py` — lessons + spoken tutor scripts.
  `ai_agents.py` — TutorAgent / generators (Gemini-backed, offline fallback).
- `web/index.html` = the Arena (games); `web/academy.html` = the voice Academy.

## Production mapping

| Prototype | Production equivalent |
|---|---|
| stdlib stub tools | gRPC/REST to TCS BaNCS, DigiLocker/CKYC, NSDL, AML engine |
| `security.py` middleware | API gateway (auth, TLS, WAF, rate limiting) |
| in-memory sessions | customer profile service |
| synthetic profiles & backtest | real-time feature store (Kafka → Flink) + warehouse labels |
| Web Speech API | on-device/edge ASR-TTS with dialectal models |
| offline state machine | durable agent graph (e.g. LangGraph) with the same tools |

The agent code does not change between prototype and production — only the tool
implementations and the data source behind them do.
