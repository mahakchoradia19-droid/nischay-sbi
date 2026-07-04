# Solution Design — from "rescue" to a payment-readiness engine

This is the deeper architecture behind the demo. The demo shows one rescue; this
document shows the system that rescue is a single frame of. It answers one question:
**given a database of people, their fields, and whether each payment landed — what is
the best, cheapest, most creative way for an agent to close the gap?**

## The reframe

The demo's story is *reactive*: a payment is about to bounce, so we fix it. The
stronger system is *proactive* and reframes the whole problem:

> Every DBT-eligible account is a **completeness vector** of the fields a payment needs
> to land. The agent's job is to keep every account **payment-ready before the
> disbursement calendar event** — not to rescue payments after they fail.

The fields that must all be "green" for money to land:

| Field | Green when… | If red, the fix |
|---|---|---|
| Aadhaar seeded (NPCI mapper) | mapped to SBI's IIN | re-seed (camp/BC/AePS) |
| KYC valid | not expired | re-KYC (voice → V-CIP) |
| Account active | transacted recently | one-transaction reactivation |
| Name reconciled | doc name ≈ account name | auto-match (zero touch) |
| Mobile linked | a reachable number on file | register / pull from sibling account |
| DBT flag / IFSC correct | scheme-linked, valid | correct the record |

The **missing field is the atomic unit of work.** The database the user describes —
`(person, fields[], received?)` — is exactly the substrate. The agent loops over it.

## The agent loop over the database

```
for each account where  next_scheme_event ≤ T+15 days  and  readiness < PAYMENT_READY:
    missing = red_fields(account)
    plan    = cheapest_resolution(missing, account)     # the waterfall below
    dispatch(plan)                                       # zero-touch → voice → camp → human
after the event:
    label account.received? and account.field_outcomes   # feeds the learning loop
```

Two design choices make this efficient rather than brute-force:

## 1 · Fix the cheapest way first — the resolution waterfall

Most systems would call everyone. That is the expensive, low-yield path. Resolve in
ascending order of cost and customer burden, and stop as soon as an account goes green:

1. **Zero-touch, internal reconciliation (₹0, no contact).** Many "missing" fields are
   not missing — they already exist inside SBI's own data. A valid KYC done at another
   branch; a mobile number on the customer's second account; an Aadhaar on a joint
   account; a name that only *looks* mismatched. **Research says 36% of Aadhaar/bank
   issues are just spelling errors** (Dvara, 2022) — those are fixed by the name
   matcher with no human contact at all. Auto-fill from what the bank already knows,
   first, always.
2. **Consented government pull (₹0–low, no branch).** For a genuinely missing document,
   fetch it from **DigiLocker** (Aadhaar/PAN) or via the **Account Aggregator** framework
   with the customer's consent — government-to-government, not customer burden.
3. **Voice re-KYC (₹ a few, self-serve).** The smartphone voice agent for the
   reachable, KYC-lapsed segment. (This is the demo.)
4. **IVR / missed-call / USSD (₹ low, feature phones).** The ~40% on feature phones get
   a vernacular IVR walk-through — reach without a smartphone.
5. **Banking camp, batched by field + village (₹ higher, physical).** Cluster every
   unseeded Aadhaar in a village into one camp visit; deploy where the rupees-per-visit
   is highest. Route by *field type and geography*, not one person at a time.
6. **Human officer (₹ highest).** Only the genuine identity conflicts.

Each rung handles a slice and passes the rest down. The average cost per rescued
account collapses because the cheap rungs do most of the volume.

## 2 · Ride the disbursement calendar (predict, don't wait)

PM-KISAN instalments, MGNREGS cycles, scholarship terms run on **known schedules.** So
the agent never waits for a bounce:

- **T-15 health check:** before every scheduled event, sweep the eligible cohort and
  fix red fields ahead of time.
- **Predictive lapse:** dormancy and KYC expiry are predictable from transaction cadence
  and KYC date — fix accounts that *will* lapse in the next 90 days before they break.

Preventive maintenance, not emergency repair.

## The multiplier that changes the economics: fix-once, benefit-forever

Seeding one Aadhaar, or renewing one KYC, doesn't unblock one ₹2,000 payment. It
unblocks **every current and future scheme for that person, for every future cycle.**
The return isn't per-payment; it's per-account-lifetime. One 90-second fix compounds
across *N schemes × M cycles*. This is why the cheap-first waterfall wins so hard: the
zero-touch fixes are permanent.

## Other creative levers

- **The Readiness Score (0–100).** A single per-account number — a credit score for
  *delivery*, not creditworthiness. The bank's console becomes "show me every account
  below 60 in this district, by fixable field." One number to sort, target, and track.
- **Household graph routing.** Model families as a graph; use one active, reachable
  member as the bridge to fix a dependent's blocked account (where the relationship and
  consent permit).
- **Outcome-closed learning loop.** Reweight routing on the *real* outcome — did the
  next payment actually land — not on "we contacted them." The system learns who to fix
  and how.
- **The open-ecosystem gap we sit in.** The rails exist (NPCI/APBS), the auth exists
  (Aadhaar libraries), the failure data exists (RTI collections like `kaarana/dbt-data`).
  What does *not* exist anywhere public is the **prediction + last-mile remediation
  layer**. That whitespace is the product — and only SBI has the accounts to run it on.

## What's implemented vs. designed

The demo implements the reactive rescue, the deterministic gate, and the honest metrics.
The **readiness score and the cheapest-fix-first router** are implemented as a small,
real module (`engine.readiness()` / `engine.resolution_plan()`), so this document is not
only a plan — the reframe runs too. Everything above the pilot line is the roadmap; the
substrate (the `(person, fields, received?)` database and the agent loop over it) is
exactly what a pilot would wire to real warehouse data.
