# 3-Minute Demo Script (Judge-Facing)

Use this script for live judging rounds.
Goal: show "real build + clear business value" in under 3 minutes.

## 0:00 to 0:20 - Context

"YONO Nexus is an agentic layer for SBI across three outcomes: acquisition, activation, and proactive engagement. This demo is fully runnable offline, with optional live AI enhancement."

## 0:20 to 1:05 - Onboarding Agent (port 8000)

1. Open `http://localhost:8000`.
2. Click `Upload Aadhaar + PAN`.
3. Point to trace panel as tools fire and mismatch is handled.
4. Confirm identity and select occupation.
5. Highlight live metrics:
   - 7 fields auto-extracted
   - only 1 user-asked field
   - straight-through path and zero human handoff

Line to say:
"This is goal-completion behavior, not scripted chat behavior."

## 1:05 to 1:45 - FinSmart Arena (port 8001)

1. Open `http://localhost:8001`.
2. Launch one game (Interest Island or Cyber Shield).
3. Answer once, show explanation/feedback loop.
4. Return to hub and show coins, XP, badge progression.

Line to say:
"This solves engagement by making financial literacy sticky and measurable."

## 1:45 to 2:20 - SCOUT Acquisition (port 8002)

1. Open `http://localhost:8002`.
2. Select any life-event prospect.
3. Show conversion probability, CLV, and outreach message generated.
4. Scroll trace and show tool-by-tool reasoning.

Line to say:
"SCOUT converts SBI data signals into explainable, personalized acquisition action."

## 2:20 to 2:50 - SAARTHI Proactive Engagement (port 8003)

1. Open `http://localhost:8003`.
2. Select `CUST_RAMESH` (EMI shortfall scenario).
3. Show proactive nudge card and one-tap resolution CTA.
4. Show reasoning trace proving why this nudge was selected.

Line to say:
"The agent helps before the customer asks, at the right moment and in their language."

## 2:50 to 3:00 - Close

"We built runnable prototypes today with clear upgrade paths to production adapters. Judges can run this locally in under a minute using our quickstart."

## Backup lines for common judge questions

- "Is this dependent on external APIs?"  
  "No. Offline deterministic mode runs end-to-end; optional keys enable live AI."

- "How production-ready is this?"  
  "Orchestration and UX are production-structured; integrations are stubbed for hackathon speed and can be swapped to real services."

- "What is real vs planned?"  
  "Four runnable modules are live now; deeper score/life-stage capabilities are documented as next-phase extensions."
