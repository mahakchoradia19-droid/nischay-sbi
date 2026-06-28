# YONO Nexus — SBI Hackathon Submission

**Team:** Mahak Choradia
**Track:** Agentic AI for Customer Acquisition, Digital Adoption & Engagement
**Submission:** Two working prototypes + a documented roadmap for three additional pillars

---

## What We Built

Most hackathon banking submissions are slide decks with wireframes. This is not that.

This repository contains **two fully runnable systems** — no cloud accounts, no Docker, no npm install. Both start with a single `python3` command and work completely offline. They can be demoed in 30 seconds in any conference room, on any laptop, with or without an internet connection.

The two systems together make a single argument: **SBI already owns the raw materials to leapfrog HDFC and ICICI — 500M customers, the largest transaction dataset in India, Jan Dhan infrastructure, and YONO's existing install base. What's missing is the intelligence layer between those assets and the customer.** YONO Nexus is that layer.

---

## The Problem We're Solving

SBI is the largest bank in India by almost every measure — branches, customers, balance sheet. Yet private banks consistently outrank it on digital experience. The gap is not product quality or pricing. SBI's FD rates are competitive. Its loan products are often cheaper. The gap is **interaction design**.

Three specific failures:

**1. Onboarding is a funnel with holes.** Digital account opening asks users to re-key information the bank could extract from their Aadhaar and PAN. When a field fails validation — a name mismatch between documents, a rejected PIN code — the system dead-ends and tells the user to visit a branch. The branch visit never happens. That customer is lost. Industry onboarding drop-off sits at 60–70% (Nielsen Norman Group, digital banking research).

**2. The app assumes the wrong user.** YONO was designed for a digitally fluent, English-first, high-bandwidth urban user. SBI's actual modal customer is none of those things. A 45-year-old teacher in Bhagalpur opening her first digital account gets the same interface as a 26-year-old engineer in Bengaluru. One of them is well-served. The other abandons.

**3. Money sits idle because the bank waits for the customer to ask.** The average SBI savings account balance earns 3.5% p.a. Millions of customers have lakhs sitting untouched for months when SBI could — and should — be offering FDs, liquid funds, SIPs, or insurance. The data to identify these customers exists. The action never happens because the system is reactive: it responds to requests, it does not initiate advice.

---

## Our Solution: Three Pillars, One Intelligence Layer

### Pillar 1 — Agentic Onboarding (built, running on port 8000)
Convert account opening from a form-filling exercise into a goal-completing conversation. The agent's objective is *open a compliant account*, not *render the next screen*. It sequences tool calls autonomously, extracts data from documents instead of asking for it, self-heals on validation failures, and escalates to a human only when policy requires it.

### Pillar 2 — FinSmart Arena: Financial Literacy Games (built, running on port 8001)
A game-based financial literacy platform embedded directly within the YONO experience. Four mini-games teach compound interest, fraud detection, card selection, and investment basics — with points, badges, streaks, and an AI advisor agent that analyses each player's mock financial profile and recommends specific SBI products. This is the **adoption and engagement** lever: it brings customers back to YONO who have no current financial need, builds the trust and literacy required to accept AI-driven advice, and creates a measurable activation path from "learned about FDs in the game" to "opened an FD in YONO."

### Pillar 3 — Money Health Score (designed, not yet built)
A single-number score (0–100) representing a customer's financial health, computed from their SBI account data: savings rate, idle balance duration, product diversification, spending patterns, EMI-to-income ratio. The agent surfaces three specific, actionable improvements with direct links to the relevant YONO products. The score is shareable — a viral acquisition mechanic. This is the proactive engagement trigger that converts idle accounts into active financial relationships.

### Pillar 4 — Life-Stage Journey Map (designed, not yet built)
Rather than a product catalogue, a personalised visual timeline: "You're 27. Here's what financially secure people your age have done by 30, 35, 40." Each milestone (first FD, term insurance, SIP, home loan pre-approval) is clickable and opens the product directly. The agent personalises the map against the customer's current SBI account data and recalibrates monthly. This replaces product discovery with a guided roadmap and gives customers a concrete reason to return to YONO.

---

## Repository Structure

```
SBI_hackathon/
│
├── README.md                       ← you are here
│
├── app.py                          ← Onboarding Agent server (port 8000)
├── agent.py                        ← Agentic orchestrator (offline + live Claude)
├── tools.py                        ← Simulated SBI tool layer
├── web/                            ← Onboarding Agent frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── finlearn/                       ← FinSmart Arena (port 8001)
    ├── app.py                      ← Game server
    ├── agents.py                   ← 4 Gemini-powered AI agents
    ├── game_data.py                ← 32 questions, 8 badges, investment profiles
    └── web/
        ├── index.html
        ├── style.css
        └── game.js
```

---

## Quick Start

**Requirements:** Python 3.9+, nothing else. No pip, no npm, no Docker.

```bash
# Clone or unzip the submission
cd SBI_hackathon

# Start Pillar 1: Onboarding Agent
python3 app.py
# → http://localhost:8000

# In a separate terminal: Start Pillar 2: FinSmart Arena
cd finlearn && python3 app.py
# → http://localhost:8001
```

Both systems run completely offline with zero network dependency. AI enhancement is available optionally (see below).

---

## Pillar 1: YONO Nexus Onboarding Agent

### What it does

The agent opens a fully compliant savings account in a two-minute conversation with zero human handoff. The user photographs their Aadhaar and PAN — everything else is autonomous.

### Why it's not a chatbot

A chatbot responds to what you say. An agent pursues a goal. The difference matters:

| Chatbot behaviour | Agent behaviour |
|---|---|
| "Your name doesn't match. Please visit a branch." | Detects the mismatch, reasons about its likely cause, asks one targeted question, reconciles, continues. |
| Presents form field 1, waits, presents field 2, waits… | Calls OCR, PAN validation, CKYC lookup, AML screen, and account creation autonomously in sequence. |
| Fails on bad network | Deterministic offline path runs identically with no network. |
| Switches language, loses all context | Retains name, current state, and unresolved threads across language switch. |

### The demo flow

1. Open `http://localhost:8000`
2. Click "Upload Aadhaar + PAN" — the agent calls OCR on both documents simultaneously
3. Watch the Agent Reasoning Trace panel: it calls `ocr_extract` → `validate_pan` → detects a name mismatch → reasons about it in-trace → asks one question
4. Click "Yes, same person" — agent continues to `ckyc_lookup` → `aml_screen` → asks one final question (occupation, the only thing it cannot infer)
5. Account opens: Live Metrics shows `fields_auto_extracted: 7`, `fields_asked: 1`, `human_handoffs: 0`, `straight_through: true`
6. Switch language mid-flow using the "🌐 हिंदी / English" button — agent replies in Hindi and retains all prior context

### Architecture

```
Flutter-equivalent frontend (web/)
        │
        │  POST /api/message (JSON)
        ▼
app.py — stdlib HTTP server
        │
        ▼
agent.py — Supervisor orchestrator
  ├── OFFLINE PATH: deterministic goal state-machine
  │     States: await_docs → await_identity_confirm → await_occupation → done
  │     Transitions driven by tool results and user confirmation
  │
  └── LIVE PATH (ANTHROPIC_API_KEY set): Claude Opus 4.8 via raw urllib
        Claude receives: system prompt + tool schemas + conversation history
        It plans, calls tools, receives results, continues until goal complete
        Same tools, same governance, identical UI output
        │
        ▼ (both paths converge here)
tools.py — typed, permissioned tool layer
  ├── ocr_extract(document_type)         → OCR + liveness simulation
  ├── validate_pan(pan, name)            → NSDL registry check + name match
  ├── ckyc_lookup(aadhaar_last4, name)   → CKYC deduplication
  ├── aml_screen(name, dob)              → Sanctions/PEP screen
  └── create_account(...)               → TCS BaNCS account creation
```

Every tool is a stub today. In production, each function becomes a gRPC or REST call to the corresponding SBI/regulatory system. The agent code does not change — only the tool implementations.

### Live Claude (optional)

```bash
ANTHROPIC_API_KEY=sk-ant-... python3 app.py
```

With a key, the same tool schemas are handed to Claude Opus 4.8, which plans and executes the onboarding autonomously. The Agent Reasoning Trace panel updates in real time. Without a key, the deterministic path runs identically — the demo is indistinguishable to the user.

### Governance (built-in, not bolted-on)

- **No credential holding:** the agent calls tools, it never holds API keys or customer credentials
- **Deterministic escalation:** the human handoff path triggers on a specific, auditable condition (unresolvable identity conflict), not on agent confusion
- **Full audit trail:** every tool call, input, and output is logged in the trace, ready for RBI examination
- **DPDP Act compliance hook:** PAN and Aadhaar numbers are masked in all logs (`XX7731`, `ABKPS4416Q` truncated for display)

---

## Pillar 2: FinSmart Arena — Financial Literacy Game

### The strategic rationale

Financial literacy and engagement are the same problem viewed from different angles. A customer who understands compound interest opens FDs. A customer who can spot a phishing SMS trusts digital banking. A customer who learns what a credit card actually costs uses it responsibly. And a customer who plays a game on YONO has a reason to open YONO that isn't bill payment.

FinSmart Arena is not an educational add-on. It is a **customer activation and retention mechanism** that happens to be educational.

### The four games

**Interest Island 🏝️**
Teaches: simple vs compound interest, the Rule of 72, FD rates, RD mechanics, real vs nominal returns, tax efficiency (PPF vs FD after tax), SIP compounding over 20 years.
Format: 12 MCQ questions with Indian rupee figures, SBI-specific product examples, and difficulty progression from definitional (level 1) to tax-optimisation edge cases (level 3).
Why it matters: Most Indians cannot compute compound interest and do not understand why an FD beats a savings account over 5 years. This game closes that gap in 5 minutes.

**Cyber Shield 🛡️**
Teaches: phishing SMS patterns, vishing (voice fraud), UPI request vs payment distinction, URL structure analysis, screen-share fraud, OTP discipline, password hygiene.
Format: 12 real-world scenarios (SMS, email, WhatsApp, phone call, UPI screen) presented as authentic-looking message cards. Player swipes SAFE or SCAM within a 10-second timer. Streak multiplier rewards sustained accuracy.
Why it matters: UPI fraud in India crossed ₹1,400 crore in FY2024. The majority of victims are SBI customers. Every player who can spot a fake UPI collect request is one fewer fraud complaint.

**Card Clash 💳**
Teaches: credit vs debit card selection by scenario, cash advance costs, forex cards, EMI traps (the interest-free period collapse mechanic), prepaid cards, secured credit cards for credit-building, what to do when a card is stolen.
Format: 8 customer persona scenarios (the student, the vendor, the international traveller, the person whose card was stolen). Player selects the correct card from four options. Each scenario reveals a common expensive mistake.
Why it matters: SBI issues more debit cards than any bank in India. A large fraction of customers do not know what credit card cash advance interest costs, or that paying minimum-due collapses the grace period entirely.

**Wealth Wizard 💰**
Teaches: opportunity cost of idle savings, FD vs liquid fund vs SIP vs PPF trade-offs, risk appetite alignment, tax efficiency, emergency fund allocation.
Format: Player enters their age, idle balance amount, months sitting idle, risk appetite, and financial goal. An AI agent computes the opportunity cost they have already incurred, explains it plainly, and ranks four SBI product options with personalised reasoning for each. Not punishing — the player earns coins and a badge for completing it.
Why it matters: This is the direct commercial conversion path. A customer who learns they've missed ₹3,150 in potential returns on ₹1.2 lakh sitting idle for 9 months — and sees an FD button one tap away — converts at a fundamentally different rate than one who sees a generic "Invest Now" banner.

### The engagement mechanics

**Points and coins:** Every correct answer earns coins (50–100 for interest/cards, 100 for cyber questions). Streak multipliers up to 4× reward sustained performance. Coins persist across sessions in browser local storage.

**XP and levels:** 11 levels from Rookie to SBI Champion. Levelling up triggers a full-screen animation and unlocks a higher player avatar. The XP bar is always visible — a constant progress signal.

**Badges:** 8 badges unlockable across the four games (Compound King, PhishBuster Pro, Card Wizard, Money Grower, On Fire, FinSmart Legend, Speed Demon, Welcome). Each badge award triggers a popup and is displayed permanently on the hub screen. The FinSmart Legend badge requires completing all four games — creating a completion incentive across the full product surface.

**AI explanations:** When a player answers incorrectly, there is a 40% chance the system calls the Gemini ExplainerAgent for a fresh, contextual explanation of why the correct answer is right. This prevents the game from feeling repetitive on replay.

### The four AI agents (finlearn/agents.py)

All four agents degrade gracefully to rich static content if no API key is present. With a free Gemini key, they activate automatically.

**QuizAgent**
Generates personalised MCQ questions calibrated to the player's current XP level and the concepts they have already seen. At level 1 it produces definitional questions. At level 7 it produces tax-and-regulation edge cases. Takes: topic, level (1–10), list of recently seen concepts. Returns: a complete question object in the same schema as the static questions, allowing the frontend to treat them identically.

**AdvisorAgent**
The core of Wealth Wizard. Takes a customer's financial profile (age, idle balance, months idle, current savings rate, risk appetite, financial goal) and computes: opportunity cost already incurred, a personalised narrative of 3 ranked investment options, and why each fits this specific customer. Falls back to a static expert-system response that is still specific to the profile, not generic.

**ExplainerAgent**
Triggered probabilistically after wrong answers. Takes the question text, the wrong answer chosen, the correct answer, and the financial concept being tested. Returns a 2–3 sentence explanation that is encouraging (not critical), uses an analogy or real Indian example where possible, and ends with one actionable takeaway. Designed to make wrong answers educational rather than punishing.

**ScenarioAgent**
Generates novel cyber-fraud scenarios based on current India-specific threat trends: QR code fraud, deepfake video calls, AI voice cloning, digital arrest scams, SIM swap attacks. The static library covers 12 evergreen scenario types; the ScenarioAgent ensures the game stays current as fraud tactics evolve. At the end of each Cyber Shield session, one AI-generated scenario is appended if a key is available.

### Running with Gemini AI (free, no credit card required)

1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) — this is Google's free tier, no billing setup required
2. Create a key (takes 30 seconds)
3. Run:

```bash
cd finlearn
GEMINI_API_KEY=your_key_here python3 app.py
```

The AI pill on the hub screen switches from grey ("Offline Mode") to purple ("AI Active · Gemini 2.0 Flash"). All four agents activate. The game is fully playable and rich without the key — the key adds personalisation and novel content generation.

### API endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/api/questions/interest` | Returns all 12 interest questions |
| POST | `/api/questions/cyber` | Returns all 12 cyber scenarios |
| POST | `/api/questions/cards` | Returns all 8 card scenarios |
| POST | `/api/quiz/ai` | Gemini: generate a personalised question |
| POST | `/api/advisor` | Gemini: full investment advice for a profile |
| POST | `/api/explain` | Gemini: explain a wrong answer |
| POST | `/api/scenario/ai` | Gemini: generate a novel fraud scenario |
| POST | `/api/status` | Server health, AI active state, content counts |

---

## Technical Stack

### What we chose and why

**Python standard library only (no pip)** — both servers run on Python 3.9+ with zero package installation. This was a deliberate choice: in a hackathon room, demo setup time is a real risk. A server that starts in 3 seconds and needs no virtualenv never fails due to dependency resolution.

**Raw `urllib` for all external API calls** — no `requests`, no `httpx`. Same reason. The live Claude path and the Gemini path both use `urllib.request.urlopen`, which has been in the standard library since Python 2.

**Vanilla HTML/CSS/JS frontend** — no React, no build toolchain, no node_modules. The frontend is three static files served directly by the Python server. This means the entire submission is 7 Python files and 6 web files — nothing to build, nothing to compile.

**Dual execution paths (offline + live AI)** — both systems are designed so that removing the API key does not degrade the demo below a useful threshold. The offline onboarding agent runs a deterministic state machine that produces identical user-facing output to the Claude path. The game runs 32 questions, 8 badges, and full investment advice without Gemini. The AI layers are genuine enhancements, not requirements.

**State in browser localStorage** — player progress, coins, XP, badges, and level persist across browser sessions without a database. This is appropriate for a hackathon prototype. The production version would move this to a customer profile service.

### Production architecture (what these prototypes map to)

```
These prototypes                    Production equivalent
─────────────────────────────────────────────────────────────
tools.py stubs                  →   gRPC calls to TCS BaNCS,
                                    DigiLocker/CKYC, NSDL, AML engine

urllib HTTP server              →   Kubernetes-deployed FastAPI service
                                    behind SBI's API gateway

agent.py state machine          →   LangGraph stateful graph with
                                    durable checkpoints and retry logic

Gemini (free tier)              →   Private VPC deployment of frontier
                                    model (Claude Opus 4.8 or equivalent)
                                    for data residency compliance

localStorage progress           →   Customer profile service, integrated
                                    with YONO's existing profile layer

Hardcoded mock documents        →   Real DigiLocker + Aadhaar OTP eKYC

Static investment profiles      →   Real-time transaction data pipeline
                                    (Kafka ingest → Flink → feature store)
```

---

## Business Case

### The numbers behind the build

**Onboarding drop-off recovery**
If YONO Nexus raises digital onboarding completion from a typical 35% to 70%, and SBI's existing digital acquisition funnel brings in 1 million monthly applicants, the straight-through accounts increase by 350,000 per month. At ₹400 per branch-assisted account opening (staff time, physical handling), that is ₹14 crore per month in operational savings before any revenue impact.

**Idle money activation**
SBI holds approximately ₹43 lakh crore in customer deposits. A conservative estimate suggests 15–20% of retail savings balances sit idle in savings accounts at 3.5% p.a. for more than 6 months. The Wealth Wizard's advisory agent targets precisely this population. Moving even 2% of that idle balance into FDs or SIPs generates meaningful additional revenue per customer — at scale, this is tens of thousands of crore in AUM shift.

**Fraud cost reduction**
The Cyber Shield game trains customers to recognise the fraud vectors that generate the highest complaint and remediation volumes for SBI. Reduced fraud complaints reduce the cost of the contact centre, the fraud remediation team, and the regulatory reporting overhead.

**Engagement and cross-sell**
McKinsey's personalization research shows that organisations deploying real-time behavioural personalization achieve 5–15% revenue uplift from cross-sell. The FinSmart Arena creates a documented, measurable path from "played Wealth Wizard" to "opened FD within 30 days" — a conversion funnel SBI currently has no equivalent of.

### Why SBI specifically has an unfair advantage

Private banks can copy the technology. They cannot copy the data. SBI's 500M+ customer relationships, Jan Dhan penetration, the DBT payment rails it operates, and its presence in every district of India represent a data and distribution moat that no private bank can replicate in less than a decade. The agentic layer we have built is the mechanism that converts that moat into personalised, proactive customer interactions. Without the intelligence layer, the moat is inert. With it, SBI's scale becomes a compounding advantage.

---

## What Judges Can Test Right Now

```bash
# 1. Start both systems (two terminals)
python3 app.py                          # port 8000 — onboarding agent
cd finlearn && python3 app.py           # port 8001 — game

# 2. Onboarding: http://localhost:8000
#    Click "Upload Aadhaar + PAN"
#    Watch the Agent Reasoning Trace panel
#    Note: 7 fields extracted, 1 asked, 0 human handoffs
#    Click "🌐 हिंदी / English" — agent switches language, retains context

# 3. Game: http://localhost:8001
#    Play Interest Island — try getting an answer wrong, read the explanation
#    Play Cyber Shield — the 10-second timer creates real pressure
#    Try Wealth Wizard — enter ₹2,50,000 idle for 14 months, risk = medium
#    Watch badges accumulate on the hub screen

# 4. (Optional) Enable AI — free, takes 60 seconds to set up
#    Get key: https://aistudio.google.com/apikey
#    GEMINI_API_KEY=your_key cd finlearn && python3 app.py
#    The AI pill on the hub turns purple — Wealth Wizard advice becomes personalised
```

---

## Planned Pillars (not yet built)

### Pillar 3: Money Health Score
A single computed score (0–100) representing a customer's overall financial health, derived from SBI account data: savings rate, idle balance duration, product diversification (FD/SIP/insurance presence), spending pattern stability, EMI-to-income ratio, and credit utilisation if a credit card is held.

The agent computes the score, assigns a colour grade (red/amber/green), and surfaces three specific improvements ranked by impact — each linked directly to the relevant YONO product. The score is shareable as a card image, creating an organic acquisition mechanic: customers share their FinSmart score, others open YONO to check theirs.

Technical implementation: a scoring agent reads from the transaction feature store (already described in the architecture), runs a weighted rubric, and formats personalised output. The scoring rubric is transparent — the customer can see exactly which factors changed their score.

### Pillar 4: Life-Stage Journey Map
A personalised visual timeline displayed within YONO showing the customer their current position and the milestones financially secure people at their life stage typically achieve. At 26: first FD, term insurance, SIP initiation. At 35: home loan pre-approval, child education fund. At 50: retirement planning review, health insurance adequacy check.

The agent personalises the map using current account data: if the customer already has an FD, that milestone is marked complete. If not, clicking it opens the FD product page pre-filled with a recommended amount based on their savings balance. The map updates monthly, creating a pull mechanism that brings customers back to YONO without a push notification.

Technical implementation: a lightweight profile agent reads the customer's product holdings from the core banking layer and diffs them against a life-stage milestone matrix keyed by age bracket. No LLM required for the core journey — the LLM layer adds personalised commentary for each milestone.

---

## Files Reference

### Root (Onboarding Agent — port 8000)

| File | Purpose |
|---|---|
| `app.py` | stdlib HTTP server, serves `web/` and exposes `/api/start`, `/api/message` |
| `agent.py` | Dual-path orchestrator: offline state machine + live Claude tool-calling loop. Contains bilingual copy (English/Hindi), conversation state, tool dispatch |
| `tools.py` | 5 simulated SBI tools with production-ready schemas. The mock Aadhaar/PAN data is designed to trigger the self-healing mismatch flow |
| `web/index.html` | Single-page chat interface with Agent Reasoning Trace panel and Live Metrics dashboard |
| `web/style.css` | SBI blue theme, responsive |
| `web/app.js` | Thin client: renders messages, trace events, metrics; calls the API |
| `.env.example` | Instructions for optional Anthropic key |

### finlearn/ (FinSmart Arena — port 8001)

| File | Purpose |
|---|---|
| `app.py` | Game server, all API endpoints, imports agents and game_data |
| `agents.py` | QuizAgent, AdvisorAgent, ExplainerAgent, ScenarioAgent — all call Gemini 2.0 Flash if key is set, fall back to static content if not |
| `game_data.py` | 12 interest questions, 12 cyber scenarios, 8 card scenarios, 2 investment profiles, 8 badge definitions, 11 level thresholds |
| `web/index.html` | Full game UI: hub, 4 game screens, results screen, toast/badge/level-up overlays |
| `web/style.css` | Dark game aesthetic, SBI-branded, responsive |
| `web/game.js` | Complete game engine: state management, all four game loops, points/XP/badge system, API calls, localStorage persistence |
