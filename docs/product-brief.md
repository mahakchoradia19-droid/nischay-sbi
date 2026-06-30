# Product Brief — YONO Nexus

## The thesis

SBI loses to HDFC and ICICI on digital experience, not on product. SBI's deposit
rates are competitive, its loan products are often cheaper, its network is the
deepest in India. The gap is **interaction design** — and it is widest for exactly
the customers SBI most needs to serve: first-time digital users, vernacular
speakers, small-town India.

Private banks can copy technology. They cannot copy SBI's data and distribution
moat — 500M customers, Jan Dhan penetration, DBT rails, presence in every district.
That moat is **inert without an intelligence layer** on top of it. YONO Nexus is
that layer.

## The conversion loop

A good product is a loop, not a feature list. YONO Nexus closes one:

```
   a stranger                         a thriving, engaged customer
       │                                          ▲
   SCOUT finds them ──► onboarding opens ──► FinPulse scores ──┐
       (acquisition)     the account            their health   │
                         by voice               (0-100)        │
                                                   │           │
                         Academy teaches  ◄──  SAARTHI acts ◄──┘
                         the concept           on the weakest
                         (literacy)            dimension (engagement)
```

Every step produces the input for the next. The customer is never dropped into a
menu and left to fend for themselves; the system always knows the next best action
*for this person* and either does it or teaches it.

## The customer we design for

Two customers, one app:

- **Ramesh**, 47, kirana owner in Bhagalpur, Hindi-first, cracked ₹9,000 phone.
  Today YONO is a 14-screen English form he abandons. In YONO Nexus he opens an
  account by *talking* to the app in Hindi, gets a FinPulse score of 43 with three
  plain-language actions, and is taught compound interest by a voice that sounds
  like a patient bank officer.
- **Arjun**, 31, engineer in Pune, English-first, confident. He gets a data-rich
  view, a FinPulse score of 88, and nudges that respect his time.

Same code, same agents — an experience that adapts to the person.

## What "good" feels like

The product works when the customer feels:

```
this is exactly where my money stands
this is the one thing that would help most
and the app just... did it, in my language, before I asked
```

## Business case (illustrative, see scoring-model.md for honesty notes)

- **Acquisition.** SCOUT turns a data moat into a ranked, explainable prospect
  pipeline across dormant Jan Dhan, employer payroll, and life events.
- **Adoption.** Voice-first onboarding removes the funnel's biggest drop-off (form
  friction on low-end devices); the Academy builds the literacy that makes customers
  comfortable transacting digitally.
- **Engagement.** FinPulse + SAARTHI convert idle relationships into active ones,
  each nudge routing to a specific product with a stated rationale — and the system
  measures its own conversion honestly so the bank can trust the funnel.

The numbers in the submission are modelled on synthetic-but-consistent data and are
labelled as such. The point of the build is that the **mechanism is real**: plug in
warehouse data and the same code produces the same kinds of outputs.
