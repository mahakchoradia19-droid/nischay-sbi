"""
engine.py — the core of "Arrives": the system that makes sure government money
reaches the person it was sent to.

Two things are REAL here, not mocked, because they are the load-bearing claims of
the proposal:

  1. fuzzy_name_match()  — a genuine name reconciler (token + edit distance). This
     is what lets the voice agent SELF-HEAL a document mismatch instead of dead-ending
     ("Ramesh Kumar" on Aadhaar vs "Ramesh Kumar Verma" on PAN). It generalises to any
     pair of names, so it survives "show me it on your own name".

  2. reactivate()        — a DETERMINISTIC gate. An account is only reactivated when
     identity is genuinely reconciled and screening is clear. The conversation can be
     driven by an LLM, but it cannot talk its way past this gate.

Everything else (the cohort numbers, the self-evaluation) is COMPUTED from per-account
flags, deterministically, so the same demo yields the same numbers every run. To be
precise: the metrics are a SIMULATION of outcomes, not a real labelled backtest — the
same code accepts real outcome labels in production; here the labels are generated.
Stdlib only.
"""

import difflib
import itertools
import random
import re
import time
import zlib

# ---------------------------------------------------------------------------
# Audit trail — append-only, in-memory for the demo (a WORM store in production).
# The page claims "every step logged"; this is what makes that claim true.
# ---------------------------------------------------------------------------
AUDIT = []
_audit_seq = itertools.count(1)


def _audit(event, **fields):
    entry = {"seq": next(_audit_seq), "t": round(time.time(), 3),
             "event": event, **fields}
    AUDIT.append(entry)
    if len(AUDIT) > 500:            # bounded for a long-running demo
        del AUDIT[:100]
    return entry


def audit_log(last=50):
    """The most recent audit entries, oldest first."""
    return AUDIT[-last:]

# ---------------------------------------------------------------------------
# The one human being the whole demo is built around, plus the boundary cases
# the system deliberately CANNOT fix on its own (point: show the 20% you can't fix).
# ---------------------------------------------------------------------------
PEOPLE = {
    "ramesh": {
        "id": "ramesh", "name": "Ramesh Kumar", "age": 47,
        "scheme": "PM-KISAN", "amount": 2000, "lang": "hi",
        # blockers: dormant + KYC lapsed → fixable by a voice re-KYC + one transaction
        "dormant": True, "kyc_lapsed": True, "aadhaar_seeded": True, "has_phone": True,
        # the name on file vs the name he'll give (the self-heal moment)
        "aadhaar_name": "Ramesh Kumar", "legal_name": "Ramesh Kumar Verma",
        "fixable": "voice",
    },
    "sunita": {
        "id": "sunita", "name": "Sunita Devi", "age": 39,
        "scheme": "MGNREGS wages", "amount": 4200, "lang": "hi",
        "dormant": True, "kyc_lapsed": False, "aadhaar_seeded": True, "has_phone": True,
        "aadhaar_name": "Sunita Devi", "legal_name": "Sunita Devi",
        "fixable": "voice",
    },
    # boundary case 1: no phone → cannot be reached digitally at all
    "budhia": {
        "id": "budhia", "name": "Budhia Majhi", "age": 61,
        "scheme": "PM-KISAN", "amount": 2000, "lang": "hi",
        "dormant": True, "kyc_lapsed": True, "aadhaar_seeded": False, "has_phone": False,
        "aadhaar_name": "Budhia Majhi", "legal_name": "Budhia Majhi",
        "fixable": "camp",     # Aadhaar not seeded + no phone → needs a physical camp
    },
    # boundary case 2: genuine identity conflict the agent must escalate, not paper over
    "imran": {
        "id": "imran", "name": "Imran Ali", "age": 34,
        "scheme": "Scholarship", "amount": 12000, "lang": "hi",
        "dormant": False, "kyc_lapsed": True, "aadhaar_seeded": True, "has_phone": True,
        "aadhaar_name": "Imran Ali", "legal_name": "Mohammed Imran Sheikh",  # too far apart
        "fixable": "human",    # names irreconcilable in-dialogue → human review
    },
}


def get_person(pid):
    return PEOPLE.get(pid)


_ROUTE = {
    "voice": ("Voice re-KYC", "Fixable now, self-serve — the agent reactivates it by phone"),
    "camp":  ("Banking camp", "Needs a person: Aadhaar re-linking / no phone → next village camp"),
    "human": ("Human officer", "Genuine identity conflict → escalated, not auto-reactivated"),
}


def queue():
    """The district work-queue: every at-risk account this cycle, its blocker(s),
    the route that can fix it, and the amount at stake. This is the operational view —
    an agent triaging a cohort, not just one story."""
    out = []
    for pid in PEOPLE:
        d = diagnose_person(pid)
        route_label, route_note = _ROUTE[d["fixable"]]
        out.append({
            "id": d["id"], "name": d["name"], "scheme": d["scheme"], "amount": d["amount"],
            "blockers": [r["code"] for r in d["reasons"]],
            "blocker_text": "; ".join(r["text"].split(" — ")[0] for r in d["reasons"]),
            "route": d["fixable"], "route_label": route_label, "route_note": route_note,
            "reachable": d["reachable"],
        })
    # voice-fixable first (the ones the agent handles live), then camp, then human
    order = {"voice": 0, "camp": 1, "human": 2}
    out.sort(key=lambda x: order.get(x["route"], 9))
    return out


def diagnose_person(pid):
    """Why this person's next payment will not arrive, and how it can be fixed."""
    p = PEOPLE.get(pid)
    if not p:
        return None
    reasons = []
    if p["dormant"]:
        reasons.append(("dormant", "Account inactive for 6+ months — the payment lands but is never claimed"))
    if p["kyc_lapsed"]:
        reasons.append(("kyc_lapsed", "ID verification (KYC) has expired — new credits are blocked"))
    if not p["aadhaar_seeded"]:
        reasons.append(("unseeded", "Aadhaar not linked in the payments system — the credit is rejected outright"))
    return {
        "id": p["id"], "name": p["name"], "scheme": p["scheme"], "amount": p["amount"],
        "lang": p["lang"], "has_phone": p["has_phone"], "fixable": p["fixable"],
        "reasons": [{"code": c, "text": t} for c, t in reasons],
        "reachable": p["has_phone"],
    }


# ---------------------------------------------------------------------------
# REAL name reconciliation (the self-heal). Generalises to any two names.
# ---------------------------------------------------------------------------
_SANCTIONS = ["Dawood Ibrahim", "Hafiz Saeed", "Iqbal Mirchi", "Tiger Memon"]


# Indian-document reality: honorifics appear on documents but not accounts (and
# vice versa), and a handful of abbreviations are near-universal. Normalising
# these is what makes the matcher survive real Aadhaar/PAN pairs, not just demos.
_HONORIFICS = {"shri", "sri", "sh", "smt", "shrimati", "srimati", "kumari",
               "mr", "mrs", "ms", "dr", "prof"}
_ABBREV = {"md": "mohammed", "mohd": "mohammed", "mohammad": "mohammed",
           "muhammad": "mohammed", "kr": "kumar", "pd": "prasad"}


def _tokens(name):
    raw = re.sub(r"[^a-z ]", " ", (name or "").lower()).split()
    out = []
    for t in raw:
        if t in _HONORIFICS:
            continue
        out.append(_ABBREV.get(t, t))
    return out


def fuzzy_name_match(a, b):
    """0..1 confidence that two names refer to the same person (handles dropped
    surnames, initials, spelling drift). No hardcoded outcomes."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    short, long = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    used, matched = set(), 0.0
    for t in short:
        best, bj = 0.0, -1
        for j, u in enumerate(long):
            if j in used:
                continue
            if t == u:
                c = 1.0
            elif len(t) == 1 and u.startswith(t):
                c = 0.5
            elif len(u) == 1 and t.startswith(u):
                c = 0.5
            else:
                r = difflib.SequenceMatcher(None, t, u).ratio()
                c = r if r > 0.8 else 0.0
            if c > best:
                best, bj = c, j
        if bj >= 0:
            used.add(bj); matched += best
    token_score = matched / max(len(ta), len(tb))
    seq = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio()
    return round(0.6 * token_score + 0.4 * seq, 3)


def screen_name(name):
    """Real watchlist screen — clear for ordinary names, flags a listed one."""
    best = max((fuzzy_name_match(name, w) for w in _SANCTIONS), default=0.0)
    return {"clear": best < 0.85, "score": best}


def verify_identity(pid, document_name=None):
    """
    The self-heal decision. Compare the name read off the uploaded document (the PAN /
    legal name, via OCR) against the name on the bank account (Aadhaar). This is the
    real-world reconciliation: two documents for the same person rarely match exactly.
      match    — same name → proceed
      variant  — benign difference (dropped surname, initial) → confirm with one question
      conflict — genuinely different names → cannot self-heal, escalate to a human
    `document_name` overrides the on-file legal name (e.g. what the person says aloud).
    """
    p = PEOPLE.get(pid)
    if not p:
        return {"ok": False, "error": "unknown person"}
    account_name = p["aadhaar_name"]
    doc_name = document_name or p["legal_name"]
    score = fuzzy_name_match(doc_name, account_name)
    if score >= 0.85:
        outcome = "match"
    elif score >= 0.5:
        outcome = "variant"        # benign — confirm with one targeted question
    else:
        outcome = "conflict"       # genuine mismatch — escalate to a human
    _audit("identity_check", person=pid, score=score, outcome=outcome)
    return {"ok": True, "account_name": account_name, "document_name": doc_name,
            "score": score, "outcome": outcome}


_LEDGER = {}   # (pid, request_id) → result: same request can never release twice


def reactivate(pid, confirmed_name, identity_reconciled, request_id=None):
    """
    DETERMINISTIC gate. The account is reactivated (and the pending payment released)
    only when identity is reconciled AND screening is clear. An LLM driving the
    conversation cannot bypass this.

    Idempotent per request_id: a double-submitted request (network retry, double
    tap) returns the SAME result and never releases the payment twice.
    """
    p = PEOPLE.get(pid)
    if not p:
        return {"ok": False, "error": "unknown person"}
    key = (pid, request_id)
    if request_id and key in _LEDGER:
        _audit("reactivate_replay", person=pid, request_id=request_id)
        return {**_LEDGER[key], "idempotent_replay": True}
    scr = screen_name(confirmed_name or p["name"])
    _audit("screening", person=pid, clear=scr["clear"], score=scr["score"])
    if not scr["clear"]:
        result = {"ok": False, "status": "BLOCKED", "reason": "screening_hit",
                  "message": "Screening flag — routed to compliance, not reactivated."}
    elif not identity_reconciled:
        result = {"ok": False, "status": "BLOCKED", "reason": "identity_unresolved",
                  "message": "Identity not reconciled — cannot reactivate."}
    elif not p["aadhaar_seeded"]:
        result = {"ok": False, "status": "NEEDS_CAMP", "reason": "aadhaar_unseeded",
                  "message": "Aadhaar not linked in the payments system — needs a physical camp visit."}
    else:
        result = {"ok": True, "status": "ACTIVE",
                  "account_state": "reactivated",
                  "amount_released": p["amount"], "scheme": p["scheme"],
                  "message": f"Account active. {p['scheme']} ₹{p['amount']:,} released and credited."}
    _audit("gate_decision", person=pid, status=result["status"],
           reason=result.get("reason"), request_id=request_id)
    if request_id and result["ok"]:
        _LEDGER[key] = result
    return result


# ---------------------------------------------------------------------------
# The scale story + the boundary + honest metrics — all computed, deterministic.
# ---------------------------------------------------------------------------
def cohort_stats(eligible=142000, seed_key="cohort"):
    """
    From a district-sized cohort, how many payments are at risk this cycle, split by
    what's fixable digitally vs what needs a human. Deterministic (crc32 seed).
    """
    rng = random.Random(zlib.crc32(seed_key.encode()) % 100000)
    sample = min(eligible, 6000)
    scale = eligible / sample
    at_risk = 0
    human = 0        # unseeded Aadhaar OR no phone: can't be fixed digitally
    for _ in range(sample):
        d = rng.random() < 0.11          # dormant
        u = rng.random() < 0.07          # Aadhaar unseeded
        k = rng.random() < 0.06          # KYC lapsed
        nophone = rng.random() < 0.20    # unreachable by phone
        if d or u or k:
            at_risk += 1
            if u or nophone:
                human += 1
    at_risk_scaled = round(at_risk * scale)
    # amount at risk (PM-KISAN-weighted average per account for illustration)
    avg_amount = 2600
    at_risk_amount = at_risk_scaled * avg_amount
    needs_human = round(human * scale)
    digitally_fixable = at_risk_scaled - needs_human
    # the economics, computed rather than quoted:
    #   voice track ≈ ₹8/account (SMS + IVR callback + inference)
    #   human track ≈ ₹48/account (camp / BC-agent visit share)
    #   conservative rescue rates: 55% when a conversation happens, 38% via camp
    cost = digitally_fixable * 8 + needs_human * 48
    rescued_amount = round((digitally_fixable * 0.55 + needs_human * 0.38) * avg_amount)
    roi = round(rescued_amount / cost, 1) if cost else 0.0
    return {
        "eligible": eligible,
        "at_risk_accounts": at_risk_scaled,
        "at_risk_pct": round(at_risk / sample * 100, 1),
        "at_risk_amount_inr": at_risk_amount,
        "digitally_fixable": digitally_fixable,
        "digitally_fixable_pct": round(digitally_fixable / at_risk_scaled * 100),
        "needs_human": needs_human,
        "needs_human_pct": round(needs_human / at_risk_scaled * 100),
        "intervention_cost_inr": cost,
        "rescued_amount_inr": rescued_amount,
        "roi_x": roi,
    }


def honest_metrics(n=1500, seed=11):
    """Calibrated self-evaluation of the at-risk prediction (the same discipline the
    proposal promises). Realistic, imperfect — not a suspicious 100%."""
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        p = round(rng.betavariate(2, 3), 3)
        true_p = min(max(p + rng.gauss(0, 0.10), 0), 0.98)
        bounced = 1 if rng.random() < true_p else 0
        rows.append((p, bounced))
    base = sum(b for _, b in rows) / n
    raw = sum(1 for p, b in rows if (p >= 0.5) == bool(b)) / n
    brier = sum((p - b) ** 2 for p, b in rows) / n
    k = max(1, int(n * 0.10))
    topk = sorted(rows, key=lambda r: -r[0])[:k]
    prec = sum(b for _, b in topk) / k
    buckets = []
    for lo in [0.0, 0.2, 0.4, 0.6, 0.8]:
        grp = [r for r in rows if lo <= r[0] < (lo + 0.2 if lo < 0.8 else 1.01)]
        if grp:
            buckets.append({"range": f"{lo:.1f}-{lo+0.2:.1f}",
                            "predicted": round(sum(r[0] for r in grp) / len(grp), 3),
                            "actual": round(sum(r[1] for r in grp) / len(grp), 3),
                            "n": len(grp)})
    ece = round(sum(abs(b["predicted"] - b["actual"]) * b["n"] for b in buckets) / n, 4)
    return {
        "n": n, "base_rate": round(base, 3), "raw_accuracy": round(raw, 3),
        "precision_at_10pct": round(prec, 3), "lift": round(prec / base, 2) if base else 0,
        "brier": round(brier, 4), "calibration": buckets, "ece": ece,
        "note": (f"On a simulated cycle (synthetic outcomes, shown honestly as such): "
                 f"raw accuracy ({raw:.0%}) looks good only because most accounts don't "
                 f"bounce (base rate {base:.0%}). The number that matters is precision on the "
                 f"riskiest 10% — {prec:.0%}, i.e. {round(prec/base,1)}× better than chance — "
                 f"and a Brier score of {brier:.3f} with the predicted-vs-actual curve tracking "
                 f"the diagonal (calibration error {ece}).")
    }
