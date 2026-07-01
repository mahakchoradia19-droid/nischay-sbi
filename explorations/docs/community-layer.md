# The Community Layer — YONO Nexus's Uncopyable Moat

## The strategic problem this solves

Everything in the individual layer — voice KYC, FinPulse, SAARTHI, the Academy —
is excellent, but **HDFC and ICICI can copy all of it** with bigger tech budgets,
in 6 months. A winning proposal must weaponise the one thing SBI has that **no
private bank can ever buy**.

> **SBI is the only bank that can see, and act on, the financial health of an entire
> village, cluster, or cohort — because it is the custodian of India's financial
> infrastructure.**

Private banks compete at the level of *one customer → one recommendation*. YONO
Nexus operates at *one village → one intervention*. That is a different category,
and SBI is structurally alone in it.

## The flagship: the DBT Gap Agent

Every cycle, government credits (PM-KISAN, MGNREGS wages, PMAY-G, scholarships)
route to beneficiaries through the **Aadhaar Payment Bridge (APBS)** via the
**NPCI Aadhaar Mapper**. A credit **fails and returns to PFMS**, or lands in an
account where it sits **unclaimed**, when:

- the account is **dormant** (no transaction for months),
- the Aadhaar is **not seeded** in the NPCI mapper (APBS rejects),
- **KYC has lapsed** and the account is restricted.

SBI's systems *see this happening* but today do nothing proactively — the money
just returns or sits idle. As **lead bank (SLBC)** in ~200 districts, SBI is the
only entity that sees this at cohort scale *and* has the national mandate to fix it.

The DBT Gap Agent runs a four-step loop, **all computed** (see
[`../community/dbt_engine.py`](../community/dbt_engine.py)):

1. **DETECT** — "In Bhagalpur, ~32,000 of 142,000 eligible accounts are at risk this
   cycle; ≈₹20 Cr will bounce or go unclaimed." (Computed from per-account blocker flags.)
2. **DIAGNOSE** — segment the at-risk accounts by **root cause** → the specific fix:
   dormant → a one-tap reactivation nudge; Aadhaar unseeded → re-seeding via a
   banking camp; KYC lapsed → assisted video-KYC. Each with a calibrated rescue rate.
3. **ACT** — draft the right intervention per segment at cohort scale: bulk Hindi
   SMS + IVR for the self-serve segment, a video-KYC deeplink for the assisted
   segment, and a **camp deployment plan naming the villages** with the densest
   unseeded clusters.
4. **MEASURE** — report **honest, calibrated** metrics on the bounce prediction and
   the rescue (precision@k, lift, Brier, a calibration curve, rescue-when-acted),
   and openly flag raw accuracy as misleading — the same discipline as FinPulse.

The economics are the headline: in one district, ≈₹7–8 lakh of intervention rescues
≈₹10 Cr of citizens' entitlements — a **~130× ROI**, and **not a rupee of cross-sell**.

## Why it cannot be copied

| What it needs | SBI | HDFC / ICICI |
|---|---|---|
| DBT / APBS disbursement visibility | ✅ primary channel | ❌ no access |
| Jan Dhan accounts at village density | ✅ ~53 cr, every district | ❌ urban-concentrated |
| Lead-bank / SLBC mandate to fix gaps | ✅ banker to the nation | ❌ no mandate |
| SHG / cluster account visibility | ✅ primary holder | ❌ marginal |

Private banks can build better individual UX. They cannot build this — not for lack
of technology, but because they do not hold the accounts, the rails, or the mandate.

## Why this is the ethical high ground (and fixes an audit weakness)

An adversarial audit flagged the *individual* layer's acquisition agent for
"targeting welfare beneficiaries for cross-sell" — surveillance optics. The DBT Gap
Agent is the **exact inverse**: same data, opposite morality. It sells nothing; it
ensures citizens **receive money they are already owed**. In a room of SBI
executives, that reframes the entire system from "clever bank marketing" to "SBI
using its unique data for financial inclusion" — unassailable.

## The two layers together

- **Individual layer** (built, working): SCOUT, Onboarding, FinPulse, SAARTHI, Academy.
- **Community layer** (this): DBT Gap Agent today; Village FinPulse (aggregate health
  of a village, not a person) and Cluster SCOUT (SHG / employer cohorts) next.

The individual layer is the working proof that the agentic machinery is real. The
community layer is the vision that puts YONO Nexus in a category of one.

## The paragraph that wins the proposal

> *Private banks compete on personalization. SBI has something no personalization
> engine can manufacture: it is the custodian of India's financial infrastructure —
> Jan Dhan, DBT, the salary accounts of half of government, the SHG deposits of rural
> India. YONO Nexus is the intelligence layer that turns this dormant data advantage
> into active interventions — not just for one customer, but for entire villages,
> clusters, and cohorts. The DBT Gap Agent alone can rescue thousands of crore in
> government credits that bounce back unclaimed every cycle, and reactivate the
> accounts they belong to. HDFC cannot build this. They don't have the accounts.*

## Production path

The demo computes on synthetic-but-consistent cohorts. In production the same
interfaces read the **APBS/PFMS reconciliation feed** and the **NPCI mapper status**
through SBI's existing rails — the agent code is unchanged; only the data source is.
All figures beyond the four demo districts are labelled extrapolations.
