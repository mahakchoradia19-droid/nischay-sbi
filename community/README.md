# DBT Gap Agent — Community Layer (the moat)

The pillar that puts YONO Nexus in a category HDFC/ICICI **structurally cannot enter**.
It operates at *one village → one intervention* scale, finding government credits about
to bounce back to PFMS unclaimed and helping citizens **receive money they're owed**.
Full positioning: [`../docs/community-layer.md`](../docs/community-layer.md).

## Run

```bash
python3 run_community.py      # from repo root → http://localhost:8005
```
No API key needed — everything is computed.

## The loop (all computed)

1. **DETECT** — accounts at risk this cycle + ₹ at risk, per district (from per-account
   blocker flags: dormant / Aadhaar-unseeded / KYC-lapsed).
2. **DIAGNOSE** — segment at-risk accounts by root cause → the specific remediation,
   each with a calibrated rescue rate and cost.
3. **ACT** — draft the intervention per segment at cohort scale (bulk Hindi SMS + IVR,
   video-KYC deeplink, or a camp deployment plan naming the villages).
4. **MEASURE** — honest, calibrated metrics on the bounce prediction and rescue
   (precision@k, lift, Brier, calibration ECE), raw accuracy flagged as misleading.

## What to look at

National hero (₹ at risk across ~200 lead districts, labelled extrapolation) → pick a
district → watch the four steps. The headline is the **~130× ROI**: a few lakh of
intervention rescues ~₹10 Cr of citizens' entitlements, with zero cross-sell.

## Key files

| File | Role |
|---|---|
| `dbt_engine.py` | detect / diagnose / act / measure — the computed core |
| `app.py` | server (`/api/overview`, `/api/district`, `/api/measure`) |
| `web/app.js` | the "war room" dashboard |

## Why it's uncopyable

Needs DBT/APBS visibility, Jan Dhan density, the SLBC lead-bank mandate, and SHG/cluster
account holding — all of which SBI has and private banks do not. Same data the audit
called "creepy" when used for cross-sell becomes the ethical high ground when used to
deliver entitlements.
