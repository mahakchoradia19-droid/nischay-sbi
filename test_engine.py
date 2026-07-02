"""
test_engine.py — tests for the parts that must be real.

Plain asserts, no pytest needed:   python3 test_engine.py

These cover the two load-bearing claims (name reconciliation self-heals; the
reactivation gate can't be talked past), the boundary routing, and the fact that
the numbers are deterministic.
"""

import engine as e

_passed = 0


def check(name, cond):
    global _passed
    assert cond, f"FAILED: {name}"
    _passed += 1
    print(f"  ok · {name}")


# ── name reconciliation (the self-heal) ─────────────────────────────
check("identical names score 1.0", e.fuzzy_name_match("Ramesh Kumar", "Ramesh Kumar") == 1.0)
check("dropped-surname variant lands in the 0.5–0.85 self-heal band",
      0.5 <= e.fuzzy_name_match("Ramesh Kumar Verma", "Ramesh Kumar") < 0.85)
check("unrelated names score low", e.fuzzy_name_match("Suresh Yadav", "Ramesh Kumar") < 0.4)
check("matcher generalises (order/initials)",
      e.fuzzy_name_match("A P J Kalam", "Kalam") >= 0.4)

# ── verify_identity outcomes ────────────────────────────────────────
check("Ramesh → benign variant (self-heal, not dead-end)",
      e.verify_identity("ramesh")["outcome"] == "variant")
check("Sunita → exact match", e.verify_identity("sunita")["outcome"] == "match")
check("Imran → genuine conflict (must escalate)",
      e.verify_identity("imran")["outcome"] == "conflict")

# ── the reactivation gate (cannot be talked past) ───────────────────
check("gate opens only when reconciled",
      e.reactivate("ramesh", "Ramesh Kumar Verma", True)["status"] == "ACTIVE")
check("gate refuses when identity unresolved",
      e.reactivate("ramesh", "Ramesh Kumar Verma", False)["status"] == "BLOCKED")
check("unseeded Aadhaar cannot be fixed digitally → camp",
      e.reactivate("budhia", "Budhia Majhi", True)["status"] == "NEEDS_CAMP")
check("a screened name is blocked, not reactivated",
      e.reactivate("ramesh", "Dawood Ibrahim", True)["status"] == "BLOCKED")
check("released amount equals the pending payment",
      e.reactivate("ramesh", "Ramesh Kumar Verma", True)["amount_released"] == 2000)

# ── watchlist screen ────────────────────────────────────────────────
check("ordinary name is clear", e.screen_name("Ramesh Kumar Verma")["clear"] is True)
check("listed name is flagged", e.screen_name("Dawood Ibrahim")["clear"] is False)

# ── the district queue ──────────────────────────────────────────────
q = e.queue()
check("queue returns every person", len(q) == len(e.PEOPLE))
check("voice-fixable cases are triaged first", q[0]["route"] == "voice")
check("queue rows carry route + amount",
      all("route_label" in r and "amount" in r for r in q))

# ── determinism (same demo, same numbers) ───────────────────────────
check("cohort stats are deterministic across calls",
      e.cohort_stats()["at_risk_accounts"] == e.cohort_stats()["at_risk_accounts"])

# ── self-evaluation is honest and sane ──────────────────────────────
m = e.honest_metrics()
check("metrics expose base rate and precision",
      "base_rate" in m and "precision_at_10pct" in m)
check("model beats chance (lift > 1)", m["lift"] > 1.0)
check("calibration curve has buckets", len(m["calibration"]) >= 3)
check("note admits the outcomes are simulated", "simulated" in m["note"].lower())

print(f"\n  {_passed} checks passed.")
