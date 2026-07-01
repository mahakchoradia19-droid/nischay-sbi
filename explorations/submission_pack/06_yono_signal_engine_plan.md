# YONO Signal Engine: Stronger Product Plan

This is the stronger framing for YONO Nexus.
The current project has several good demos, but the weak point is that they can feel like separate ideas.
The stronger version is one decision system:

> YONO watches customer and prospect signals, ranks the next best action, explains the score, and then launches the right agentic flow.

## Inspiration Taken

### From STEP Mirror

Use a clear staged product journey:

```text
capture signal
  -> analyze
  -> show layered progress
  -> reveal score/result
  -> recommend next action
  -> let user act/share/continue
```

For SBI, this becomes:

```text
observe customer moment
  -> score action priority
  -> explain score drivers
  -> generate one governed nudge
  -> execute or defer
  -> learn from response
```

STEP Mirror is strong because the user immediately understands the product loop.
YONO Nexus needs the same tight loop.

### From Trend Recommendations

Use a visible weighted scoring model instead of a vague "AI recommends" story.

The trend dashboard is persuasive because it answers:

- why this recommendation,
- why now,
- how confident are we,
- what evidence supports it,
- what should not happen automatically.

YONO Nexus should do the same for banking actions.

## New Core Concept

### YONO Signal Engine

A ranked queue of customer/prospect moments across acquisition, onboarding, activation, and engagement.
Each item is scored, explained, and routed to the right agent.

This replaces the weaker "four pillars" framing with one operating system.

## Core Objects

### Signal

An observed event or pattern.

```json
{
  "id": "sig_001",
  "source": "transaction_pattern",
  "customerId": "CUST_RAMESH",
  "type": "emi_shortfall",
  "observedAt": "2026-06-29T09:30:00+05:30",
  "confidence": 0.91,
  "evidence": ["emi_due_2_days", "balance_4200", "emi_5000", "sweep_fd_available"]
}
```

### Moment

A cluster of related signals that may require action.

```json
{
  "id": "moment_emi_rescue",
  "customerId": "CUST_RAMESH",
  "title": "EMI shortfall before due date",
  "lifecycle": "urgent",
  "recommendedAction": "sweep_fd_transfer",
  "priorityScore": 91,
  "confidence": 0.88,
  "lane": "Fix Now"
}
```

### Action Brief

The judge-facing and banker-facing explanation.

```json
{
  "confirmed": ["EMI due in 2 days", "Current balance is INR 4,200"],
  "uncertain": ["Whether customer wants auto-transfer enabled permanently"],
  "scoreDrivers": {},
  "customerBenefit": "Avoid penalty and credit-score damage",
  "bankBenefit": "Prevent delinquency and improve trust",
  "guardrails": ["consent checked", "no product hard-sell", "single nudge only"]
}
```

## Nexus Action Score

Each possible action gets a score from `0-100`.

```text
Nexus Action Score =
    0.24 * urgency
  + 0.20 * customerBenefit
  + 0.16 * businessValue
  + 0.14 * confidence
  + 0.10 * channelFit
  + 0.08 * relationshipFit
  + 0.08 * freshness
  - 0.18 * riskOrFriction
```

### Score Drivers

- `urgency`: how soon action is needed before the moment decays.
- `customerBenefit`: avoided loss, saved time, better return, lower fraud risk, or clearer financial decision.
- `businessValue`: acquisition, deposit activation, product adoption, retention, or risk reduction.
- `confidence`: quality and consistency of supporting signals.
- `channelFit`: whether the action matches the customer's language, device, consent, and digital comfort.
- `relationshipFit`: whether this action feels appropriate for the customer's life stage and existing SBI relationship.
- `freshness`: how recent the strongest signal is.
- `riskOrFriction`: compliance risk, customer annoyance, low consent, repeated nudges, or operational burden.

## Action Lanes

| Score | Lane | Meaning | Example |
|---|---|---|---|
| 90-100 | Fix Now | urgent, high-confidence, customer-protective | EMI rescue, fraud warning |
| 75-89 | Act Today | valuable, time-sensitive, low-risk | idle balance to FD, first salary RD |
| 60-74 | Nurture This Week | useful but not urgent | FinSmart challenge, money health check |
| 40-59 | Watchlist | monitor until confidence improves | possible life event, uncertain salary gap |
| <40 | Suppress | do not nudge | low confidence, high friction, poor fit |

## How Existing Modules Fit

### Onboarding Agent

Becomes a `Fix Now` or `Act Today` flow for acquisition friction.

Input signal:

```text
prospect started KYC + uploaded docs + name mismatch found
```

Action:

```text
self-heal KYC mismatch, ask one targeted question, complete account opening
```

### FinSmart Arena

Becomes a `Nurture This Week` action, not just a standalone game.

Input signal:

```text
customer has low product adoption, idle balance, or fraud-risk behavior
```

Action:

```text
serve the right learning challenge, then route to the appropriate product action
```

### SCOUT

Becomes the acquisition-input side of the engine.

Input signal:

```text
life event, employer cluster, dormant Jan Dhan opportunity
```

Action:

```text
rank prospect, generate outreach brief, queue compliant message
```

### SAARTHI

Becomes the clearest proof of the Signal Engine.

Input signal:

```text
transaction rhythm, upcoming obligation, idle balance, salary pattern
```

Action:

```text
one timely nudge with a visible score, evidence, and guardrails
```

## New Demo Flow

The demo should start with a single control-tower view:

```text
YONO Signal Engine
  Fix Now
  Act Today
  Nurture This Week
  Watchlist
```

Each row shows:

- customer/prospect,
- recommended action,
- score,
- confidence,
- top 3 score drivers,
- routed agent.

Clicking a row launches the existing module:

- onboarding row opens the onboarding agent,
- literacy row opens FinSmart,
- acquisition row opens SCOUT,
- engagement row opens SAARTHI.

This makes the four demos feel like one product.

## What Judges Should See First

The first screen should not be a pitch.
It should be the ranked action queue.

Example visible rows:

| Lane | Customer | Action | Score | Agent |
|---|---|---|---:|---|
| Fix Now | Ramesh Kumar | Transfer INR 800 from sweep FD to prevent EMI bounce | 94 | SAARTHI |
| Act Today | Kavita Nair | Move idle INR 3.2L to FD/liquid option | 82 | SAARTHI |
| Act Today | Rahul Verma | Child SIP + term insurance outreach | 79 | SCOUT |
| Nurture | Arjun Mehta | FinSmart SIP challenge after salary credit | 68 | FinSmart |
| Watchlist | Name mismatch KYC | Ask one identity reconciliation question | 62 | Onboarding |

## Minimum Build Plan

### Phase 1: Make the story stronger in docs and demo

1. Replace "four pillars" language with "one Signal Engine, four routed agents."
2. Add the score formula and score bands to the README and submission one-pager.
3. Update the demo script to open with the decision queue concept.
4. Be explicit that the current score examples are deterministic demo-modeled values.

### Phase 2: Add a lightweight Signal Engine module

Create:

```text
signal_engine/
  scoring.py
  sample_moments.py
  README.md
```

Expose:

```text
GET /api/actions
GET /api/actions/:id
```

Return ranked actions with:

- score,
- lane,
- confidence,
- score drivers,
- routed agent,
- action brief.

### Phase 3: Add a control-tower UI

Add a simple dashboard on port `8004`:

- left side: lanes,
- center: ranked action queue,
- right side: action brief and score-driver bars,
- button: `Launch Agent`.

This can stay stdlib-only and reuse the current visual language.

### Phase 4: Connect existing demos

Each action row should deep-link or route to one existing demo:

- `8000` onboarding,
- `8001` FinSmart,
- `8002` SCOUT,
- `8003` SAARTHI.

The point is not deep integration yet.
The point is to make the system feel unified.

## Guardrails

Borrow these directly from the trend dashboard's discipline:

- Do not auto-execute financial actions without consent.
- Do not present low-confidence signals as action-ready.
- Do not mix confirmed evidence with inferred hypotheses.
- Do not rank by business value alone.
- Do not send multiple nudges when one high-quality nudge is enough.
- Do not let the LLM invent facts; it can format an action brief only after evidence exists.

## Stronger Submission Thesis

Use this line:

> YONO Nexus is not four separate demos. It is a next-best-action engine for SBI: it detects customer moments, scores urgency and value, explains the recommendation, and routes the right agent to act.

## Why This Is Stronger

The old framing says:

```text
we built onboarding + games + acquisition + nudges
```

The new framing says:

```text
we built SBI's decision layer for customer growth and protection
```

That is more competitive because it gives judges:

- one core innovation,
- a scoring model they can inspect,
- a visible product loop,
- clear guardrails,
- a production path.
