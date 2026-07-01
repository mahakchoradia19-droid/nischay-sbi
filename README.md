# Arrives — the bank that makes sure the money arrives

**An SBI Hackathon project · Mahak Choradia**

There is a quiet, expensive problem hiding inside India's welfare system, and it has
nothing to do with corruption or leakage. It's this: the government sends money to
people who are entitled to it, and a lot of the time, **the money doesn't arrive** —
not because anyone stole it, but because the person's bank account had a small,
fixable problem, and nobody noticed in time.

This project is a working system that notices, and fixes it, before the money turns
around and goes home. It is deliberately built around **one idea done properly**,
because that idea happens to be one only SBI can act on.

If you want to skip straight to it: `python3 app.py`, then open
[http://localhost:8000](http://localhost:8000). The centrepiece is a voice agent that
reactivates a farmer's account, live, in Hindi, in your browser. Everything below
explains why that ninety seconds matters more than it looks.

---

## Meet Ramesh (because a number is forgettable and a person is not)

Ramesh is a farmer. Last week the government approved his ₹2,000 support payment.
It never reached him. Not fraud, not a mistake he made — his account had gone dormant
from disuse and his ID verification (KYC) had quietly expired. So when the money came
knocking, the door was shut. The payment bounced back to the government. Ramesh
doesn't even know it happened. Next season, it will happen again.

There are millions of Rameshes. The reasons are always small and always the same:

- the account went **dormant** (unused for months), so the money lands but is never noticed,
- the **Aadhaar was never properly linked** in the system that routes these payments, so the credit is rejected outright,
- or the **KYC lapsed**, freezing the account against new money.

None of these is the person's fault, and none is hard to fix — *if someone notices
before the payment cycle runs.* Today, nobody does. **That gap is the entire problem,
and closing it is the entire project.**

---

## Why this is an SBI idea, and not a fintech idea

Any bank can build a nicer app. If that were the pitch, HDFC or ICICI would copy it
within a year, with bigger budgets. This is different, because it rests on three
things a private bank simply cannot buy:

| What closing this gap requires | SBI | HDFC / ICICI |
|---|---|---|
| Seeing the government's payments as they route | ✅ a primary pipeline for direct benefit transfers | ❌ no equivalent access |
| Accounts at village-level density | ✅ tens of crores, in every district | ❌ urban-concentrated |
| The mandate to fix inclusion gaps | ✅ banker to the nation, by role | ❌ no such mandate exists |

So this isn't a UX race SBI might lose to someone faster. It's a problem **only SBI is
positioned to solve at all** — and, just as importantly, it isn't a sales pitch. The
system sells nothing. It gets people money that is already theirs. That is a more
trustworthy thing for a bank to do with its data than "use AI to cross-sell," and it
is the honest reading of what "banker to the nation" should mean.

---

## How it actually works — and where the real technology is

Here's the honest part most AI pitches skip: **most of this doesn't need AI, and that
is good.** Spotting which accounts are about to bounce a payment is a careful database
check — simple, auditable, the kind of thing a regulator can inspect line by line. We
*want* that part boring.

The hard part — the part that genuinely needs AI — is **the last hundred metres:
actually fixing Ramesh's account without asking him to travel to a branch, in a
language he speaks.** That is where the real engineering went, and it's what the demo
shows working:

1. **Notice** — before the payment cycle, flag that Ramesh's account will bounce, and *why*.
2. **Reach** — contact him the way he actually communicates: a message and a call in his own language, not an English app notification he'll ignore.
3. **Reactivate by voice** — he taps a link and a voice agent talks to him in Hindi, walks him through re-verifying his identity out loud, reads his document, and **self-heals the small mismatch** that normally dead-ends these flows (his Aadhaar says "Ramesh Kumar", his other document says "Ramesh Kumar Verma" — the system recognises these as the same person and asks one confirming question instead of failing). Then it reactivates the account.
4. **The money lands.** The door was open when it knocked.

That voice conversation is the load-bearing piece, and it's the piece that *only
recently became possible* — before, this needed a human at a branch counter, so it
never scaled. That's the unlock, and it's what you can try live in the browser.

---

## The five things that push this past "a good idea"

Anyone can have the idea. These are the details that separate a proposal from a
product, and each one is built into the demo:

**1. One thing is genuinely real, not simulated.**
The voice agent uses your browser's real speech engine to *speak and listen*, and the
name-reconciliation and the reactivation decision are **real code running on the
server** — you can see the actual match score in the live trace. The reconciler
generalises to any pair of names, so it works on yours, not just Ramesh's. One
authentic, un-fakeable moment defeats the suspicion every judge silently carries.

**2. The demo is one human's ninety seconds, not a dashboard.**
You watch a rescue *happen* — the payment about to bounce, the message arriving, the
conversation, the account waking up, the money landing. Dashboards inform; a rescue is
remembered.

**3. It shows the 20% it *can't* fix.**
A system that claims to save everyone hasn't met the real world. This one names its
limits out loud — the person with no phone, the person whose two documents carry
genuinely different names — and hands those cases to a human or a banking camp on
purpose. Volunteering the boundary of your own system is the strongest signal of
maturity there is, and almost no one does it.

**4. It scores itself honestly, including the unflattering numbers.**
The "at-risk" prediction is evaluated on a labelled backtest and reports a calibration
curve, a Brier score, and precision on the riskiest cases — and it explicitly points
out that *raw accuracy is misleading* (it looks high only because most accounts don't
bounce). Reporting the number that makes you look worse is how you earn the one that
makes you look good.

**5. It answers the hard questions before they're asked.**
*Why hasn't SBI already done this? Is it even allowed? Why is this AI and not a
spreadsheet?* All three are answered plainly on the page, because pre-empting the
question a judge is proud to ask is the whole game.

---

## What's real today, and what I'm asking for

**Honestly:** the entire loop — the noticing, the sorting by cause, the voice agent
that reactivates an account, and the honest scorecard that reports its own misses — is
**built and running**, on realistic but synthetic sample data, because I don't have
SBI's real data. **The logic and the voice are real; only the people are simulated.**
I'd rather show a real system on fake data than a fake system on real promises.

**The ask:** run this for real, in one limited area, for one payment cycle — with
properly permissioned data — and measure it the honest way. Not just "how many did we
rescue," but the number that actually matters: **six months later, is the account
still active, and did the next payment land on its own?** Because the win isn't
rescuing the money once. It's making sure Ramesh never misses it again.

> SBI already holds the nation's money.
> **This makes SBI the bank that guarantees it arrives.**

---

## Running it

Requirements: **Python 3.9+. Nothing else** — no pip, no npm, no build step. Best in
Chrome, because the voice agent uses the browser's Web Speech API.

```bash
python3 app.py        # → http://localhost:8000
```

Then: scroll to **The rescue**, press **Start**, and let Ramesh's account get fixed.
Turn your speakers on — the agent talks. The **Hard questions** section answers the
things a judge will probe; the **At scale** section shows the computed district
numbers and the model's honest self-evaluation.

No API key is needed. (An `ANTHROPIC_API_KEY` would let a live model drive the
conversation instead of the scripted one; the mechanism and the gate are identical
either way.)

---

## What's in here

```
Arrives/
├── app.py          the server (Python standard library, ~90 lines)
├── engine.py       the real logic: name reconciliation, the reactivation gate,
│                   the cohort maths, and the honest-metrics backtest
├── web/            the single-page experience
│   ├── index.html  the narrative + the interactive rescue
│   ├── style.css   the design system (warm, editorial, calm)
│   └── app.js      the rescue state machine + the voice engine + the live trace
│
├── docs/
│   └── PROPOSAL.md the written proposal (plain-language, non-technical readers)
│
└── explorations/   the individual-customer build this grew out of — voice
                    onboarding, a financial-health score, proactive nudges, a
                    literacy academy. Real and runnable, kept as origin story and
                    evidence of range, not as competing pillars. See its README.
```

**Two things are real, on purpose**, because they are the claims the whole proposal
rests on: the **name reconciler** in `engine.py` (`fuzzy_name_match`) that self-heals a
document mismatch and generalises to any name, and the **reactivation gate**
(`reactivate`) that will not release a payment unless identity is genuinely reconciled
and screening is clear — a decision an LLM driving the conversation cannot talk its way
past. Everything else is computed deterministically, so the same demo produces the same
numbers every time you run it.

---

## A note on how this was built

This started as an individual-customer product (it's in `explorations/`), and then I
realised the same machinery — the voice KYC, the fuzzy matcher, the gate, the honest
metrics — pointed at a bigger problem that only SBI is positioned to solve. Rather than
pretend it was all one grand design, I'd rather tell you the true version: I built the
pieces, then found the idea they were really for. This repository is that idea, made as
sharp as I could make it.
