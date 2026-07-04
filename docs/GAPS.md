# Gaps — the honest internal list

Not for the judges. This is the list of things that are missing, thin, or fakeable —
written plainly so we fix or pre-empt them, in roughly the order a sharp judge would
find them.

## 1 · Domain / banking-expertise gaps (the ones that bite hardest)

These are where a real SBI or RBI person, not a generic tech judge, will push.

- **The APBS/NPCI-mapper mechanism is described, not proven.** We say a DBT credit
  fails when the account is dormant / Aadhaar-unseeded / KYC-lapsed. That is directionally
  right, but the *exact* failure taxonomy (NACH return reason codes, APBS reject codes
  like "account frozen", "Aadhaar not mapped", "inactive") is not modelled. A banker
  will ask "which reject code are you actually catching?" We have no code list. *Fix:*
  add a short, correct reject-code table to the proposal even if the demo doesn't use it.
- **"Reactivating a dormant account" is regulated and we hand-wave it.** RBI rules on
  inactive/dormant accounts require specific re-KYC and, in some cases, a fresh customer
  due-diligence step — you cannot simply "wake" an account with one transaction in all
  cases. Our demo implies a one-tap reactivation. *Fix:* state precisely that we trigger
  the *mandated* re-KYC (V-CIP) flow, not a shortcut around it.
- **V-CIP has hard requirements we don't show.** RBI's Video-based Customer
  Identification Process mandates a live agent or a tightly specified assisted flow,
  liveness/face-match, geotagging, and audit retention. Our "fix it by talking" reads as
  lighter than V-CIP actually is. *Fix:* frame the voice agent as the *front door to*
  V-CIP, with the human/liveness steps intact — never as a replacement.
- **Aadhaar re-seeding isn't the bank's unilateral action.** Re-linking Aadhaar in the
  NPCI mapper depends on the customer's consent and UIDAI/NPCI turnaround; the bank
  can't just do it. Our "camp re-seeds Aadhaar" glosses this. *Fix:* say the camp
  *initiates and assists* the re-seed; it doesn't complete it instantly.
- **Consent & DPDP specifics are asserted, not designed.** We claim "most defensible use
  of the data." True in spirit, but we show no consent artifact, no purpose-limitation
  record, no data-retention/localisation stance. A DPDP-aware judge wants the mechanism,
  not the assurance. *Fix:* one slide on consent (scheme-owner-initiated, purpose-bound,
  auditable) — we have the audit trail; tie it to consent.
- **The economics use invented unit costs.** ₹8/voice, ₹48/camp, 55%/38% rescue rates
  are *our* assumptions, labelled as such, but a judge may still ask for provenance.
  *Fix:* cite any public benchmark for BC-agent/camp cost per account, or explicitly call
  them planning assumptions to be validated in the pilot.

## 2 · Technical gaps

- **No LLM is actually wired in.** The "AI agent" is a scripted, deterministic dialogue
  today. That is honestly stated, and the gate is the real defensible part — but a judge
  expecting to see an agent *reason* will not. *Fix (optional):* an opt-in `ANTHROPIC_API_KEY`
  path that lets a model drive the same tool-calls, with the gate unchanged, would make
  the "agentic" claim literal.
- **Speech recognition is browser-only and English/Hindi-only.** `webkitSpeechRecognition`
  is Chrome-centric, fails on many dialects and in noise, and there's no real ASR for the
  20+ languages the "vernacular" claim implies. *Fix:* name the production path (Bhashini
  / on-device models) and keep the button fallback prominent.
- **All state is in-memory.** Journey memory, the audit log, the idempotency ledger, the
  rate limiter — all reset on restart and don't survive multiple workers. Fine for a demo,
  but the "durable resume" and "append-only audit (WORM)" claims are aspirational. *Fix:*
  say "in-memory for the demo; a datastore/WORM in production" wherever we make the claim
  (we mostly do — audit the wording once more).
- **The metrics are a simulation, and the calibration is engineered to look good.** We
  label it honestly, but the backtest generates its own "true" probabilities, so the
  near-diagonal calibration is a property of the generator, not evidence of a real model.
  A quant judge who reads `honest_metrics()` will see this. *Fix:* keep labelling it a
  simulation; never imply the calibration validates a trained model.
- **No accessibility pass.** No ARIA on the mic/voice controls, no keyboard path through
  the rescue, no captions toggle on the site (the film has them; the demo doesn't). For an
  *inclusion* product this is an ironic gap. *Fix:* a small a11y pass.
- **The film's audio is macOS-generated.** Good enough and correctly pronounced, but it's
  Apple `say`, not a premium neural voice; a discerning ear can tell. *Fix:* acceptable;
  note it's a rendering choice, upgradeable to a neural TTS.

## 3 · Product / UX gaps

- **One person, one scheme, one district.** The demo is deliberately narrow. It reads as a
  vignette, not a system, unless the queue + at-scale sections carry the weight. *Fix:*
  make sure the presentation spends time on the queue, not just Ramesh.
- **No RM / bank-staff view.** Everything is customer-facing. A bank runs on the officer's
  screen — the camp list, the escalation queue, the daily rescue report. We gesture at it
  (queue, "human review") but don't show it. *Fix:* a single ops-view mock would close this.
- **No failure/rollback story in the UI.** We show the gate blocking, but not "what the
  customer sees when we can't help" beyond a line. *Fix:* minor.

## 4 · Evidence gaps (known, still open)

- **Zero field data.** No survey, no real user, no third-party validation. This remains the
  single biggest gap between "excellent build" and "proof". The kit to close it is
  `docs/FIELD_KIT.md`; it just hasn't been executed.
- **No rendered demo video file.** The film is a live page; the `.mp4` is produced by
  screen-recording it. There's no pre-rendered video artifact in the repo.

## The one-line triage

If we can only touch three before submission: (1) tighten the **V-CIP / dormant-account /
re-seeding** language so a banker can't catch us over-claiming, (2) run the **field
survey** for one real number, (3) add the **consent slide**. Everything else is polish.
