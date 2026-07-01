# YONO Nexus — The DBT Gap Agent
### Getting citizens the government money they're already owed
**SBI Hackathon Proposal · Mahak Choradia**

---

## 1. The Problem

Every cycle, the Government of India disburses crores of rupees directly into bank
accounts — PM-KISAN to farmers, MGNREGS wages to rural workers, PMAY-G housing
instalments, scholarships to students. This money moves through Direct Benefit
Transfer (DBT): the government approves the payment, and it routes through the
**Aadhaar Payment Bridge System (APBS)** via the **NPCI Aadhaar Mapper** into the
beneficiary's bank account.

The government has already decided this person should get the money. The amount is
sanctioned. The only thing standing between a citizen and their entitlement is a
**banking-side technicality**:

- their account is **dormant** (no transaction in 6+ months), so the credit lands
  but is never noticed or claimed,
- their Aadhaar is **not seeded** in the NPCI mapper, so APBS **rejects the credit
  outright** and it bounces back to the government's PFMS system,
- their **KYC has lapsed**, freezing the account against new credits.

None of these are the citizen's fault in any meaningful sense, and none of them are
hard to fix — *if someone notices in time*. Today, nobody does. The credit simply
bounces back, or sits unclaimed, and the cycle repeats next quarter for the same
family.

**This is not a product problem. It is a visibility problem.** The data needed to
catch this exists — inside SBI's core banking and DBT systems — but nobody is
watching it proactively. SBI's systems see the failure happen. They do not act on it.

---

## 2. Why SBI, and Only SBI, Can Fix This

This is the part that makes the idea strategically sharp, not just useful.

A well-funded private bank can match SBI on app design, AI chatbots, even voice
banking, within a year. What they **cannot** match is data they don't have access to:

| What this needs | SBI | A private bank |
|---|---|---|
| Visibility into DBT/APBS disbursement and rejection | ✅ — SBI is a primary DBT-receiving bank | ❌ no equivalent access |
| Jan Dhan accounts at village-level density | ✅ — ~53 crore accounts, every district | ❌ urban-concentrated, thin in rural India |
| **Lead Bank (SLBC) mandate** to act on financial-inclusion gaps in ~200 districts | ✅ — a formal RBI-assigned role | ❌ no such mandate exists |
| Primary holder of SHG and rural cluster accounts | ✅ | ❌ marginal presence |

A private bank could theoretically build the *software*. It cannot get the *data*,
and it has no *mandate* to act on a citizen's PM-KISAN eligibility. This is not a
UX race SBI might lose — it's a category SBI is alone in by structural default. The
hackathon brief asks for agentic AI that drives acquisition, adoption, and
engagement. This does all three at once, for the one population SBI is uniquely
positioned to serve: financially excluded, rural, first-generation banking
customers — exactly where SBI's Jan Dhan and DBT footprint is deepest and private
banks are thinnest.

It is also, deliberately, **not a sales pitch**. The agent recommends nothing,
upsells nothing. It helps a citizen receive money the government already decided
they should have. That is a different, more defensible category than "AI-driven
cross-sell" — and it directly serves SBI's financial-inclusion mandate as banker to
the nation.

---

## 3. The Agent: Detect → Diagnose → Act → Measure

The DBT Gap Agent runs a four-step loop, named at the level of a real account, not
just an aggregate statistic:

**1. DETECT** — Scan DBT-eligible accounts in a district ahead of the next
disbursement cycle. Flag every account where the credit is **at risk**: dormant,
Aadhaar-unseeded, or KYC-lapsed. Output: *"In Bhagalpur, ~32,000 of 142,000 eligible
accounts are at risk this cycle — approximately ₹20 Cr will bounce or go
unclaimed."*

**2. DIAGNOSE** — For every at-risk account, identify the **specific, fixable
root cause** and route it to the right remediation:

| Root cause | Fix | Channel | Effort |
|---|---|---|---|
| Account dormant | One transaction reactivates it | Hindi SMS + missed-call callback | Self-serve |
| KYC lapsed | Re-KYC via video call | App deeplink + assisted video-KYC | Assisted |
| Aadhaar not seeded | Re-seed Aadhaar to the bank IIN in the NPCI mapper | Branch / BC agent / banking camp | Physical |

**3. ACT** — Dispatch the right intervention at the right scale: bulk Hindi SMS and
IVR callbacks for the accounts that just need reactivation, a video-KYC link for
the lapsed-KYC segment, and a **named camp deployment plan** — "deploy a banking
camp to Sabour and Nathnagar villages, where the unseeded accounts cluster" — for
the cases that need a human and a form.

**4. MEASURE** — Report **honest, calibrated** results, not a flattering single
number. The system reports precision at top-confidence (how often the highest-risk
flags were correct), lift over the base rate, a Brier score and a calibration
curve (do predicted-risk accounts actually fail at the predicted rate?), and the
realised rescue rate once an intervention has run — and it explicitly flags which
of these numbers is misleading on its own (raw accuracy looks good mostly because
most accounts *don't* fail — that number alone proves nothing).

**The economics, in one district:** intervening on Bhagalpur's at-risk accounts
costs roughly ₹7–8 lakh in outreach and camp deployment and rescues an estimated
₹10 crore in entitlements — a **~130× return**, with zero cross-sell revenue
involved. Extrapolated (clearly labelled as an estimate, not a measured figure)
across SBI's ~200 lead-bank districts, the unclaimed/bounced pool this represents
runs into thousands of crore per cycle.

---

## 4. What's Built vs. What's Proposed

To be precise about where the line is, because that precision is itself part of
the pitch:

**Built and runnable today** (Python, zero setup, `python3 app.py`):
the full detect → diagnose → act → measure loop, computing real numbers from
synthetic-but-internally-consistent district data — four demo districts, per-account
blocker flags, segment-level remediation plans with calibrated rescue rates, drafted
Hindi intervention messages, and a self-evaluation report with a real calibration
curve. The mechanism (APBS / NPCI mapper / PFMS) is modelled accurately; the
*specific account-level data* is synthetic because real DBT/KYC data isn't available
outside SBI's systems.

**Proposed for a pilot:** wiring the same engine to a real APBS/PFMS reconciliation
feed and SBI's KYC/CKYC status data for one SLBC district, for 90 days — detect this
quarter's at-risk cohort, run the three remediation tracks, and measure the actual
rescue rate against the model's calibrated prediction. The code does not change
between the demo and the pilot; only the data source does.

---

## 5. The Ask

A 90-day pilot in a single SLBC lead-bank district (Bhagalpur or comparable), with
read access to the DBT/APBS rejection feed and account KYC-status data for that
district's Jan Dhan and DBT-eligible accounts. Success is measured honestly: the
calibration of the risk model against what actually bounces, and the realised
rescue rate of the three intervention tracks against their predicted rates — the
same metrics the demo already reports on synthetic data, now on real outcomes.

If it works at the rate the model predicts, the case for scaling to all ~200 lead
districts is the ROI number above, validated rather than estimated.

---

*This proposal is the lead idea inside a broader build, YONO Nexus, which also
includes a voice-led KYC onboarding agent, a transparent Money Health Score, a
proactive engagement agent, and a financial-literacy academy — built to prove the
same agentic approach also works at the individual-customer level. Those are
available to review but are intentionally secondary to this proposal: the DBT Gap
Agent is the one idea worth SBI's full attention, because it is the one idea SBI's
competitors cannot copy.*
