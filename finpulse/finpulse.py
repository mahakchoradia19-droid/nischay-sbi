"""
finpulse.py — the FinPulse Money Health Score engine.

ONE transparent number (0-100) that ties the whole of YONO Nexus together:
SCOUT acquires a customer, the onboarding agent opens the account, FinPulse
scores their financial health, SAARTHI acts on the weakest dimension, and the
Academy teaches the concept behind it. The score is the shared spine.

Design borrowed from the author's newsroom trend-intelligence engine: a
TRANSPARENT, weighted, explainable score — every point is attributable to a
named component with an explicit weight, a plain-language "why", and the single
highest-impact action to improve it (which maps to a real SBI product). No
black box, no hardcoded headline number: the score is COMPUTED from account
data, so it generalises to any customer and survives a "show me the maths" question.

Pure functions, stdlib only, fully testable.
"""

# ---------------------------------------------------------------------------
# Dimension weights — sum to 1.00. These are the editorial choice of the model
# (like the newsroom opportunity_score weights) and are shown to the customer
# so the score is never a black box.
# ---------------------------------------------------------------------------
WEIGHTS = {
    "emergency_buffer":  0.20,   # liquid months of expenses — survival first
    "savings_rate":      0.18,   # are you converting income into wealth?
    "idle_efficiency":   0.14,   # is your money working, or sleeping at 3.5%?
    "protection":        0.14,   # life + health cover vs dependents/income
    "credit_health":     0.14,   # utilisation + on-time + EMI-to-income
    "diversification":   0.10,   # breadth across FD/RD/SIP/PPF/insurance
    "goal_progress":     0.10,   # tracking toward stated life goals
}

GRADE_BANDS = [(85, "A", "Thriving"), (70, "B", "Healthy"),
               (55, "C", "Building"), (40, "D", "At risk"), (0, "E", "Fragile")]

# SBI product each improvement routes to (company POV: cross-sell; user POV: benefit)
_ACTIONS = {
    "emergency_buffer": ("Build a 6-month buffer with an auto-sweep RD",
                         "SBI Recurring Deposit + Savings sweep-in",
                         "An emergency fund means a job loss or medical bill never becomes a debt spiral."),
    "savings_rate": ("Automate a SIP on salary day so saving happens first",
                     "SBI SIP / Mutual Fund auto-debit",
                     "Paying yourself first is the single habit that builds wealth."),
    "idle_efficiency": ("Move idle cash above your buffer into an FD or liquid fund",
                        "SBI Fixed Deposit / Liquid Fund",
                        "Idle money at 3.5% quietly loses to inflation; an FD at ~6.8% out-runs it."),
    "protection": ("Add term life + health cover sized to your income",
                   "SBI Life term plan + SBI General health",
                   "One uninsured hospital event can erase years of savings."),
    "credit_health": ("Cut card utilisation below 30% and never miss an EMI",
                      "SBI Card usage alerts + EMI auto-pay",
                      "A stronger credit score means cheaper loans for the rest of your life."),
    "diversification": ("Add one missing pillar (FD, SIP, PPF or insurance)",
                        "SBI PPF / SIP",
                        "Spreading money across instruments reduces risk and improves returns."),
    "goal_progress": ("Set up a goal-linked SIP for your biggest milestone",
                      "SBI Goal-based investing",
                      "A goal with an automatic monthly amount behind it is a goal that happens."),
}


def _clip(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# Per-dimension sub-scores (0-100). Each returns (score, why, detail-dict).
# Inputs come from a normalised customer profile (see profiles.py).
# ---------------------------------------------------------------------------

def _emergency_buffer(p):
    months = (p["liquid_balance"] / p["monthly_expense"]) if p["monthly_expense"] else 0.0
    # target = 6 months; full marks at >=6, linear below
    score = _clip((months / 6.0) * 100.0)
    why = (f"You hold about {months:.1f} months of expenses in liquid form "
           f"(target: 6). " + ("Solid cushion." if months >= 6 else
           "A thinner cushion than ideal."))
    return score, why, {"months_buffer": round(months, 1), "target_months": 6}


def _savings_rate(p):
    rate = (p["monthly_saving"] / p["monthly_income"]) if p["monthly_income"] else 0.0
    # 20% saving = good (score 80), 30%+ = excellent (100)
    score = _clip(rate / 0.30 * 100.0)
    why = (f"You save about {rate*100:.0f}% of your income. " +
           ("Excellent discipline." if rate >= 0.30 else
            "Healthy." if rate >= 0.20 else "Room to save more."))
    return score, why, {"savings_rate_pct": round(rate * 100, 1), "target_pct": 30}


def _idle_efficiency(p):
    # how much sits idle ABOVE a 6-month buffer, earning only savings rate
    buffer_need = 6 * p["monthly_expense"]
    idle_excess = max(p["liquid_balance"] - buffer_need, 0)
    invested = p["invested_balance"]
    working = invested + buffer_need
    total = working + idle_excess
    score = _clip((working / total * 100.0) if total else 100.0)
    lost = round(idle_excess * (0.068 - 0.035))   # annual drag vs an FD
    why = (f"₹{idle_excess:,.0f} sits idle above your buffer. " +
           ("Your money is working well." if idle_excess < p["monthly_income"] else
            f"That idle cash loses ≈₹{lost:,}/yr versus an FD."))
    return score, why, {"idle_excess_inr": round(idle_excess), "annual_drag_inr": lost}


def _protection(p):
    # life cover target ~10x annual income if dependents; health target >= 5L
    annual = p["monthly_income"] * 12
    life_target = annual * (10 if p["dependents"] > 0 else 3)
    life_ratio = (p["life_cover"] / life_target) if life_target else 1.0
    health_ratio = min(p["health_cover"] / 500000.0, 1.0)
    score = _clip((0.6 * min(life_ratio, 1.0) + 0.4 * health_ratio) * 100.0)
    why = (f"Life cover is {life_ratio*100:.0f}% of the recommended "
           f"{'10×' if p['dependents'] else '3×'} income; health cover "
           f"{'meets' if p['health_cover'] >= 500000 else 'is below'} the ₹5L floor.")
    return score, why, {"life_cover_ratio_pct": round(life_ratio * 100),
                        "health_cover_inr": p["health_cover"]}


def _credit_health(p):
    util = p["card_utilisation"]                 # 0..1
    dti = p["emi_to_income"]                      # 0..1
    util_score = _clip((1 - util / 0.30) * 100) if util > 0 else 100  # <=30% ideal
    dti_score = _clip((1 - dti / 0.40) * 100)    # <=40% DTI ideal
    ontime = 100 if p["missed_payments_12m"] == 0 else _clip(100 - p["missed_payments_12m"] * 25)
    score = _clip(0.4 * util_score + 0.3 * dti_score + 0.3 * ontime)
    why = (f"Card utilisation {util*100:.0f}% (ideal <30%), EMIs are "
           f"{dti*100:.0f}% of income (ideal <40%), "
           f"{p['missed_payments_12m']} missed payment(s) in 12 months.")
    return score, why, {"utilisation_pct": round(util * 100),
                        "emi_to_income_pct": round(dti * 100),
                        "missed_payments_12m": p["missed_payments_12m"]}


def _diversification(p):
    pillars = ["has_fd", "has_sip", "has_ppf", "has_insurance", "has_rd"]
    held = sum(1 for k in pillars if p.get(k))
    score = _clip(held / len(pillars) * 100.0)
    missing = [k.replace("has_", "") for k in pillars if not p.get(k)]
    why = (f"You hold {held} of {len(pillars)} core instruments. " +
           ("Well diversified." if held >= 4 else
            f"Missing: {', '.join(missing)}."))
    return score, why, {"pillars_held": held, "missing": missing}


def _goal_progress(p):
    g = p.get("goal_progress_pct")
    if g is None:
        score, why = 50.0, "No goals set yet — a goal with a monthly amount behind it changes everything."
        return score, why, {"goal_progress_pct": None}
    score = _clip(g)
    why = f"You're {g:.0f}% toward your stated goals — " + ("on track." if g >= 60 else "behind pace.")
    return score, why, {"goal_progress_pct": round(g)}


_DIMS = {
    "emergency_buffer": _emergency_buffer, "savings_rate": _savings_rate,
    "idle_efficiency": _idle_efficiency, "protection": _protection,
    "credit_health": _credit_health, "diversification": _diversification,
    "goal_progress": _goal_progress,
}

DIM_LABELS = {
    "emergency_buffer": "Emergency Buffer", "savings_rate": "Savings Rate",
    "idle_efficiency": "Money Efficiency", "protection": "Protection",
    "credit_health": "Credit Health", "diversification": "Diversification",
    "goal_progress": "Goal Progress",
}
# the financial concept (Academy lesson) behind each dimension — closes the loop
DIM_CONCEPT = {
    "emergency_buffer": "fd_rd", "savings_rate": "compounding_magic",
    "idle_efficiency": "inflation_tvm", "protection": "jan_suraksha",
    "credit_health": "credit_score", "diversification": "fd_rd",
    "goal_progress": "compounding_magic",
}


def score_profile(profile: dict) -> dict:
    """Compute the FinPulse score with a full, transparent breakdown."""
    dims = {}
    weighted_total = 0.0
    for key, fn in _DIMS.items():
        sub, why, detail = fn(profile)
        w = WEIGHTS[key]
        contribution = sub * w
        weighted_total += contribution
        act_title, act_product, act_benefit = _ACTIONS[key]
        # potential score uplift if this dimension reached 100
        uplift = round((100 - sub) * w, 1)
        dims[key] = {
            "label": DIM_LABELS[key],
            "score": round(sub),
            "weight": w,
            "contribution": round(contribution, 1),
            "max_contribution": round(w * 100, 1),
            "why": why,
            "detail": detail,
            "uplift_if_fixed": uplift,
            "action": act_title,
            "product": act_product,
            "benefit": act_benefit,
            "concept": DIM_CONCEPT[key],
        }
    score = round(weighted_total)
    grade, label = _grade(score)

    # top actions: rank dimensions by the score uplift available (impact-first)
    ranked = sorted(dims.values(), key=lambda d: -d["uplift_if_fixed"])
    top_actions = [{
        "title": d["action"], "product": d["product"], "benefit": d["benefit"],
        "dimension": d["label"], "uplift": d["uplift_if_fixed"], "concept": d["concept"],
    } for d in ranked if d["uplift_if_fixed"] > 0][:3]

    return {
        "score": score,
        "grade": grade,
        "grade_label": label,
        "dimensions": dims,
        "top_actions": top_actions,
        "weights": WEIGHTS,
        "explanation": (f"FinPulse {score}/100 ({grade} · {label}). "
                        f"This is a weighted sum of 7 transparent dimensions — "
                        f"every point is attributable. Fixing your weakest dimensions "
                        f"could add up to {round(sum(a['uplift'] for a in top_actions),1)} points."),
    }


def _grade(score):
    for cutoff, g, label in GRADE_BANDS:
        if score >= cutoff:
            return g, label
    return "E", "Fragile"


def percentile_vs_cohort(score: int, cohort_scores: list) -> int:
    """Where this score sits vs a cohort (a shareable, motivating number)."""
    if not cohort_scores:
        return 50
    below = sum(1 for s in cohort_scores if s < score)
    return round(below / len(cohort_scores) * 100)
