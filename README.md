# Arrives - the bank that makes sure the money arrives

**An SBI Hackathon project · Mahak Choradia**
![tests](https://github.com/mahakchoradia19-droid/arrives-sbi/actions/workflows/tests.yml/badge.svg) · MIT licensed

There is a quiet, expensive problem hiding inside India's welfare system, and it has
nothing to do with corruption or leakage. It's this: the government sends money to
people who are entitled to it, and a lot of the time, **the money doesn't arrive**, 
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
It never reached him. Not fraud, not a mistake he made - his account had gone dormant
from disuse and his ID verification (KYC) had quietly expired. So when the money came
knocking, the door was shut. The payment bounced back to the government. Ramesh
doesn't even know it happened. Next season, it will happen again.

There are millions of Rameshes. The reasons are always small and always the same:

- the account went **dormant** (unused for months), so the money lands but is never noticed,
- the **Aadhaar was never properly linked** in the system that routes these payments, so the credit is rejected outright,
- or the **KYC lapsed**, freezing the account against new money.

None of these is the person's fault, and none is hard to fix - *if someone notices
before the payment cycle runs.* Today, nobody does. **That gap is the entire problem,
and closing it is the entire project.**

---

## Why this is an SBI idea, and not a fintech idea

Any bank can build a nicer app. If that were the pitch, a well-funded private bank would copy it within a year. This is different because it rests on three things no private bank can buy: SBI is a primary pipeline for government benefit transfers, so it actually sees the payments as they route. It holds tens of crores of accounts in every district, including villages where private banks have no branch. And it carries a formal mandate to fix financial-inclusion gaps. A private bank could write this software in a quarter, then have nothing to run it on. This is not a UX race SBI might lose to someone faster. It is a problem only SBI is positioned to solve at all. And it is not a sales pitch: the system sells nothing. It gets people money that is already theirs.

---

## How it actually works - and where the real technology is

Here's the honest part most AI pitches skip: **most of this doesn't need AI, and that
is good.** Spotting which accounts are about to bounce a payment is a careful database
check - simple, auditable, the kind of thing a regulator can inspect line by line. We
*want* that part boring.

The hard part - the part that genuinely needs AI - is **the last hundred metres:
actually fixing Ramesh's account without asking him to travel to a branch, in a
language he speaks.** That is where the real engineering went, and it's what the demo
shows working:

1. **Notice** - before the payment cycle, flag that Ramesh's account will bounce, and *why*.
2. **Reach** - contact him the way he actually communicates: a message and a call in his own language, not an English app notification he'll ignore.
3. **Reactivate by voice** - he taps a link and a voice agent talks to him in Hindi, walks him through re-verifying his identity out loud, reads his document, and **self-heals the small mismatch** that normally dead-ends these flows (his Aadhaar says "Ramesh Kumar", his other document says "Ramesh Kumar Verma" - the system recognises these as the same person and asks one confirming question instead of failing). Then it reactivates the account.
4. **The money lands.** The door was open when it knocked.

That voice conversation is the load-bearing piece, and it's the piece that *only
recently became possible* - before, this needed a human at a branch counter, so it
never scaled. That's the unlock, and it's what you can try live in the browser.

---

## The five things that push this past "a good idea"

Anyone can have the idea. These are the details that separate a proposal from a
product, and each one is built into the demo:

**1. One thing is genuinely real, not simulated.**
The voice agent **speaks** with your browser's speech engine and **listens** with its
speech-recognition engine - say "haan / yes" or "nahi / no" and it responds (with tap
buttons as a fallback where a browser or microphone isn't available). And the
name-reconciliation and the reactivation decision are **real code running on the
server** - you can see the actual match score in the live trace. The reconciler
generalises to any pair of names, so it works on yours, not just Ramesh's. One
authentic, un-fakeable moment defeats the suspicion every judge silently carries.

**2. The demo is one human's ninety seconds, not a dashboard.**
You watch a rescue *happen* - the payment about to bounce, the message arriving, the
conversation, the account waking up, the money landing. Dashboards inform; a rescue is
remembered.

**3. It shows the 20% it *can't* fix.**
A system that claims to save everyone hasn't met the real world. This one names its
limits out loud - the person with no phone, the person whose two documents carry
genuinely different names - and hands those cases to a human or a banking camp on
purpose. Volunteering the boundary of your own system is the strongest signal of
maturity there is, and almost no one does it.

**4. It scores itself honestly, including the unflattering numbers.**
The "at-risk" prediction is evaluated on a **simulated cycle** - synthetic outcomes,
labelled as such, not a real backtest - and reports a calibration curve, a Brier score,
and precision on the riskiest cases, while explicitly pointing out that *raw accuracy is
misleading* (it looks high only because most accounts don't bounce). The same evaluation
code accepts real outcome labels in production; only the data source changes. Reporting
the number that makes you look worse is how you earn the one that makes you look good.

**5. It answers the hard questions before they're asked.**
*Why hasn't SBI already done this? Is it even allowed? Why is this AI and not a
spreadsheet?* All three are answered plainly on the page, because pre-empting the
question a judge is proud to ask is the whole game.

---

## What's real today, and what I'm asking for

**Honestly:** the entire loop - the noticing, the sorting by cause, the voice agent
that reactivates an account, and the honest scorecard that reports its own misses - is
**built and running**, on realistic but synthetic sample data, because I don't have
SBI's real data. **The logic and the voice are real; only the people are simulated.**
I'd rather show a real system on fake data than a fake system on real promises.

**The ask:** run this for real, in one limited area, for one payment cycle - with
properly permissioned data - and measure it the honest way. Not just "how many did we
rescue," but the number that actually matters: **six months later, is the account
still active, and did the next payment land on its own?** Because the win isn't
rescuing the money once. It's making sure Ramesh never misses it again.

> SBI already holds the nation's money.
> **This makes SBI the bank that guarantees it arrives.**

---

## Running it

Requirements: **Python 3.9+. Nothing else** - no pip, no npm, no build step. Best in
Chrome, because the voice agent uses the browser's Web Speech API.

```bash
python3 app.py           # → http://localhost:8000
python3 test_engine.py   # 31 checks over the real logic
python3 test_server.py   # 15 checks: the security attack pass, codified
```

Then: scroll to **The rescue**, press **Start**, and let Ramesh's account get fixed.
Turn your speakers on - the agent talks, and listens. The **Hard questions** section
answers the things a judge will probe; the **At scale** section shows the computed
district numbers and the model's honest self-evaluation.

**The film:** [http://localhost:8000/film.html](http://localhost:8000/film.html) - an
80-second, ad-style film that plays itself, narrated live by the same voice engine
the product uses (English scenes, and the agent's line in Hindi). It isn't a rendered
video file - it's *generated by the product each time*, so it can never go stale. To
produce an `.mp4` for a submission portal, screen-record one play-through.

No API key, no internet, no accounts - it runs entirely on your machine. The agent's
dialogue is a fixed, honest script today; in production a live model could drive the
conversation, and the reactivation gate would refuse to release money on its say-so
just the same. The point of the gate is that it doesn't trust the talker.

---

## What's in here

```
Arrives/
├── app.py           the hardened server (stdlib only): rate-limited, size-capped,
│                    security headers, localhost-bound by default
├── engine.py        the real logic: name reconciliation (honorific/abbreviation-aware),
│                    the reactivation gate (idempotent, audit-logged), the district
│                    queue, the cohort economics, the self-evaluation
├── test_engine.py   31 checks over the real logic
├── test_server.py   15 checks: the security attack pass, codified
├── web/
│   ├── index.html   the narrative + the district queue + the interactive rescue
│   ├── film.html    the 80-second self-playing film (the product narrates itself)
│   ├── style.css    the design system (warm, editorial, calm)
│   └── app.js       the rescue state machine, the voice engine (speak + listen),
│                    the queue, and the live trace
├── docs/
│   ├── PROPOSAL.md  the written proposal (plain-language, for non-technical readers)
│   └── FIELD_KIT.md the survey + real-user demo script for primary evidence
├── .github/         CI: both test suites run on every push
└── LICENSE          MIT
```

That's the whole thing. No framework, no build step, no hidden services - a handful of
files you can read end to end in twenty minutes, with 46 checks a CI badge attests to.

**Two things are real, on purpose**, because they are the claims the whole proposal
rests on: the **name reconciler** in `engine.py` (`fuzzy_name_match`) that self-heals a
document mismatch and generalises to any name, and the **reactivation gate**
(`reactivate`) that will not release a payment unless identity is genuinely reconciled
and screening is clear - a decision an LLM driving the conversation cannot talk its way
past. Everything else is computed deterministically, so the same demo produces the same
numbers every time you run it.

---

## Security posture

A demo that handles identity-shaped flows should behave like it knows that, even
locally. The server is hardened accordingly:

- **Localhost-bound by default** - it never listens beyond your machine unless you
  explicitly set `HOST=0.0.0.0` (and it warns you when you do).
- **Same-origin only** - no CORS headers are emitted at all; nothing cross-origin
  can call the API from a browser.
- **Every response carries security headers** - a Content-Security-Policy,
  `nosniff`, frame-denial, and a no-referrer policy.
- **Inputs are distrusted** - JSON-only content type, a 16 KB body cap, all string
  fields bounded, per-IP rate limiting.
- **Path traversal is closed** - static paths resolve through `realpath` and must
  land inside `web/`, which defeats both `../` tricks and symlink escapes.
- **No version disclosure** - the server doesn't announce its Python or HTTP version.
- And the deepest control isn't HTTP at all: **the reactivation gate is
  deterministic server-side code.** The front end - or a compromised client, or an
  LLM - cannot fake a reconciliation or talk money loose. The decision that matters
  never leaves the server.

In production, TLS, auth, and audit logging arrive with the bank's API gateway; the
demo's job is to show the *shape* of a system that takes custody of trust seriously.

---

## A note on how this was built

This started as a broader individual-customer product - voice onboarding, a
financial-health score, proactive nudges. Building it, I ended up with the pieces that
turned out to matter: the voice KYC, the fuzzy name matcher, the reactivation gate, the
honest-metrics discipline. Then I realised those pieces pointed at a bigger problem that
only SBI is positioned to solve, and I cut everything that wasn't that. Rather than
pretend it was all one grand design, here's the true version: I built the machinery,
found the idea it was really for, and made the repository only that. Focus was the
hardest and most important decision in the whole project.

---

## Sources, and what is / isn't claimed

The mechanism is real and publicly documented; the specific account-level numbers in
the demo are illustrative, because I don't have SBI's data. To keep the two clearly
separated:

**Real, and citable by name (the how):**
- **Aadhaar Payment Bridge System (APBS)** and the **NPCI Aadhaar Mapper** - the rails
  that route DBT credits by Aadhaar; a credit fails when the account isn't seeded in the
  mapper. (NPCI documentation.)
- **PFMS** (Public Financial Management System) - the government system a failed DBT
  credit returns to. (pfms.nic.in.)
- **PMJDY / Jan Dhan** - publicly reported at roughly 53–55 crore accounts, the bulk in
  rural and semi-urban India. (pmjdy.gov.in dashboard.)
- **Lead Bank Scheme / SLBC** - the RBI framework under which a bank is responsible for
  financial-inclusion coordination in its lead districts. (RBI.)
- **DBT scheme figures** - scheme-wise disbursement is published on the DBT Bharat
  portal. (dbtbharat.gov.in.)

**Illustrative, and labelled as such (the how-much):**
- The people (Ramesh, and the queue) are synthetic.
- The district cohort figures are computed from modelled blocker rates, not measured.
- The self-evaluation runs on a **simulated cycle with synthetic outcomes** - the
  method is real (calibration, Brier, precision on the riskiest cases); the labels are
  generated, not observed. The same code accepts real outcome labels in a pilot.

The honest one-line version: **the logic and the voice are real; the data is not, and
the code says so out loud wherever it matters.**

The next step is replacing "illustrative" with "observed": a micro-survey and a real-user
demo video, planned in [`docs/FIELD_KIT.md`](docs/FIELD_KIT.md).
