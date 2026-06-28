# YONO Nexus: One-Page Submission Brief

## One-line thesis

YONO Nexus turns SBI from a reactive banking app into an agentic growth engine that acquires, activates, and engages customers through autonomous, explainable workflows.

## Problem

SBI has scale, trust, and distribution, but loses digital momentum in three places:

- onboarding drop-offs caused by form-heavy, fragile flows,
- low engagement from customers who open YONO only when forced,
- idle balances and predictable stress signals that go unassisted until too late.

## What is built and runnable now

1. **Agentic Onboarding (port 8000)**  
   Autonomous KYC flow with tool orchestration, mismatch recovery, bilingual continuity, and full reasoning trace.
2. **FinSmart Arena (port 8001)**  
   Financial literacy game platform with 4 game modes, 32 static questions, badges, streaks, and optional AI personalization.
3. **SCOUT Acquisition Agent (port 8002)**  
   Prospect intelligence pipeline that analyzes signals, scores conversion likelihood, generates personalized offers, and logs outreach.
4. **SAARTHI Proactive Engagement Agent (port 8003)**  
   Customer rhythm monitoring that detects timely intervention moments and executes one high-relevance proactive nudge.

## Why this is differentiated

- Goal-driven agents, not FAQ/chat wrappers.
- Deterministic offline path plus optional live AI path over the same tools.
- Explainability-first UI with visible reasoning traces for every key step.
- Governance hooks included from day one: auditable actions, deterministic handoff conditions, masked identifiers in logs.

## Demo evidence (from runnable prototype behavior)

- Onboarding live metrics: `fields_auto_extracted: 7`, `fields_asked: 1`, straight-through completion with `human_handoffs: 0` on primary path.
- FinSmart content footprint: 32 questions across Interest/Cyber/Cards + advisor flow and badge progression.
- SCOUT sample dashboard metrics (demo-modeled): 14,820 prospects identified (7d), 14.0% conversion rate, INR 210 CAC.
- SAARTHI sample dashboard metrics (demo-modeled): 41.2M customers monitored, 37% acted-on rate, 18,400 EMI bounces prevented (7d).

## Technical architecture

- Python stdlib HTTP servers, no external framework dependency.
- Shared tool-layer pattern: deterministic stubs today, replaceable with real APIs without changing orchestration logic.
- Frontend: lightweight web UI focused on speed, readability, and trace transparency.

## Scope honesty

- Core integrations are simulated in the tool layer for hackathon-speed delivery.
- This is intentional for a no-setup reproducible demo.
- Productionization path is clear: replace tool stubs with SBI/internal service adapters.

## 30-day productionization plan

1. Replace top 3 high-value tool stubs with real service connectors.
2. Add auth + role boundaries + immutable audit sink.
3. Run pilot on one region/segment with conversion and retention instrumentation.

## Why this can win competitive rounds

- It is runnable.
- It is explainable.
- It maps directly to acquisition, activation, and engagement outcomes.
- It demonstrates both product imagination and implementation discipline.
