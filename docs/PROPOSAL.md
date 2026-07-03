# Arrives
### The bank that makes sure the money arrives
**An SBI Hackathon proposal · Mahak Choradia**

---

There is a moment that happens millions of times a year in India, and almost nobody
sees it.

The government approves a payment - ₹2,000 to a farmer, a fortnight's wages to a
worker, a scholarship to a student. The money is sanctioned. It is *sent*. It travels
down the payment rails toward a bank account… and the account can't receive it. The
payment turns around and goes back. No alarm rings. No one calls. The family it was
meant for never learns it existed.

Then, next cycle, it happens to the same family again.

This proposal is about ending that moment - not with a new scheme, not with more
money, but by fixing the one link in the chain that already belongs to a bank:
**the account the money was sent to.**

---

## 1 · The problem is small, boring, and enormous

Money sent through Direct Benefit Transfer fails to land for reasons that would be
almost funny if they weren't so costly:

- the account went **dormant** - unused for months, so the credit sits unclaimed or
  is turned away;
- the **Aadhaar was never linked** in the mapper that routes the payment, so the
  rails reject it outright;
- the **KYC lapsed** - a formality expired, and the account froze.

Notice what's *not* on that list: fraud, error, ineligibility. The person did nothing
wrong. The government did nothing wrong. A technicality nobody was watching simply
closed the door before the money knocked.

And here is the detail that turns this from sad to solvable: **the bank's own systems
can see every one of these conditions in advance.** The dormancy flag, the missing
Aadhaar link, the lapsed KYC - all of it sits in the database, days before the
payment cycle runs. The failure is fully predictable. It is simply never acted on.

This is not a technology gap. It is an *ownership* gap. Nobody's job is the moment
between "sent" and "arrived."

**We are proposing that SBI make it SBI's job - because no one else can.**

---

## 2 · Why this belongs to SBI alone

Strip away the technology and ask: what does closing this gap actually require? Three things no private bank can buy. First, SBI is a primary pipeline for government benefit transfers, so it sees the payments as they route. Second, it holds tens of crores of accounts in every district, including villages where private banks have no branch. Third, it carries a formal government mandate to fix financial-inclusion gaps. A private bank could write this software in a quarter, then have nothing to run it on: not the payment visibility, not the village-level accounts, not the standing to act. SBI is not the best bank to build this. SBI is the **only** bank that can.

And note what the idea refuses to be: it is **not a sales engine**. It recommends nothing, upsells nothing, moves no money on its own. It exists to complete a delivery the nation already decided to make. For a bank whose name carries the word *State*, it is hard to imagine a purer use of its position.

---

## 3 · How it works - and where the AI actually is

Most of the system is deliberately boring. Finding the at-risk accounts is a careful,
auditable database check - a regulator can read it line by line, and should. We claim
no intelligence there, because none is needed.

The hard part is the last hundred metres. Detecting a dormant account is trivial;
**getting a 47-year-old farmer's KYC renewed without a branch visit is not.** That is
where the AI lives, and only there:

1. **Notice.** Days before the cycle, the system flags every account that will fail,
   and *why* - each cause needs a different fix.
2. **Reach.** A message and a call in the person's own language - not an English app
   notification that means nothing to them.
3. **Fix, by talking.** They tap once, and a voice agent speaks to them in Hindi (or
   their language), walks them through re-verifying identity out loud, reads the
   document, and - crucially - **self-heals the small mismatches** that dead-end
   these flows today. His account says *Ramesh Kumar*; his document says *Ramesh
   Kumar Verma*. Today, that kills the process. Here, the system recognises a benign
   variant, asks one confirming question, and proceeds. Ninety seconds, no branch,
   no form.
4. **Arrive.** The account is live when the cycle runs. The money lands. The family
   knows nothing except that, this time, it came.

**The guardrails, stated before anyone asks:** the conversation *re-skins* the
mandatory verification steps - it removes none of them. The agent's powers are tiny
and closed: verify identity, reactivate an account. It **never moves money**; the
credit arrives from the government through the existing rails. Every consequential
decision runs through deterministic code - a gate the conversational layer cannot
talk its way past - and anything ambiguous defaults to a human being. The worst case
of an AI mistake is a payment that stays exactly as blocked as it already was. We
built it so that the people least able to catch an AI's errors are the people the AI
can least affect.

**And the system grades itself in public.** It reports the honest numbers - how often
its risk flags were right, how well its confidence matches reality, and which of its
own metrics is misleading (raw accuracy, which looks impressive only because most
accounts don't fail). A system that will touch entitlements must be the kind that
volunteers its own scorecard. This one does, by construction.

---

## 4 · What it's worth

**To a family:** the difference between ₹2,000 arriving and not arriving is not 2,000
rupees. It is seed for a sowing season, a school fee paid on time, a loan not taken
from a moneylender. Multiply by every cycle, every scheme, every year of a life.

**To SBI:** a voice conversation costs a few rupees; the payment it unblocks is worth
hundreds to thousands. In our modelled district, about ₹8 lakh of outreach rescues an
estimated ₹3.8 crore of entitlements - **roughly a 47× return** - with zero
cross-sell, using deliberately conservative assumptions (55% rescue when a
conversation happens, 38% via camps, and the no-phone segment honestly priced at
human-visit cost). These aren't slide numbers: they fall out of the same code that
runs the demo, so a reviewer can re-derive them. Every rescued account also stops
being a dead entry and becomes a living customer: active, transacting, reachable. And
the institutional prize sits above all of it - being *visibly* the bank that delivers
the nation's money is worth more than any product line, because it is the reason SBI
holds its mandate at all.

**To the country:** extrapolated across SBI's lead-bank footprint, the pool of
bounced and unclaimed benefit money plausibly runs to thousands of crore per cycle.
We label that figure for what it is - an extrapolation from modelled districts, not a
measurement - and we note the only honest way to replace it with a real number:
run the pilot.

---

## 5 · What exists today - and what we ask

**Built and running now** (`python3 app.py`, one file server, no dependencies): the
full loop. The district queue that triages every at-risk account by cause and fix
route. The voice agent that speaks and *listens* - Hindi and English - and reactivates
an account through a real, deterministic gate. The self-healing name reconciliation,
generalising to any pair of names. The honest self-evaluation, calibration curve and
all. And the boundary, shown rather than hidden: the person with no phone routed to a
banking camp, the genuine identity conflict routed to a human, because a system that
pretends it can fix everyone hasn't met the real world.

**What is synthetic, said plainly:** the people and the district numbers. We don't
have SBI's data, so the demo runs on internally-consistent sample data and says so on
every screen where it matters. The logic and the voice are real. We would rather show
a real system on simulated data than a simulated system on real promises.

**The ask** is one pilot: a single lead-bank district, one payment cycle, properly
permissioned data. Measured the honest way - not "how many accounts did we touch"
but **six months later, is the account still alive, and did the next payment land on
its own?** Because rescuing money once is a demo. Making sure a family never misses
a payment again is infrastructure.

---

## 6 · Where this goes

Look past the hackathon for a moment.

Every entitlement - every pension, every scholarship, every subsidy, every wage, 
shares the same failure point: the last metre between a government system and a
human being's account. Whoever owns that metre owns the most meaningful position in
Indian finance: **the delivery-guarantee layer of the welfare state.**

That layer will exist. The rails exist, the data exists, the need compounds every
cycle. The only open question is whether it is built by the institution whose
accounts, rails and mandate it runs on - or assembled awkwardly around that
institution, years later, by someone else.

Start with one district and one payment cycle. End with a country where "the
government sent it" and "the family received it" are, finally, the same sentence.

**SBI already holds the nation's money.**
**This makes SBI the bank that guarantees it arrives.**

---

*Everything claimed here is inspectable: the code is small enough to read in twenty
minutes, ships with its own tests, and an 80-second film of the product, 
generated by the product - is at `/film.html`. This proposal grew out of a broader
agentic-banking build; everything that wasn't this one idea was deliberately cut,
because the idea deserves a repository with nothing else in it.*
