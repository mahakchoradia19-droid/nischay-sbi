"""
SAARTHI — Proactive Engagement Agent tool layer.

"Saarthi" (सारथी) = the charioteer who guides. This agent watches a customer's
financial rhythms and steps in BEFORE they ask — the third superpower of YONO
Nexus: it helps you before you ask.

In production each function reads from SBI's real-time transaction feature store
(Kafka → Flink → feature store) and the core banking layer. Here they are
deterministic stubs so the demo runs with zero setup and zero network.

The schemas at the bottom (TOOL_SCHEMAS) are handed to Claude when a key is set,
so the live and offline paths call exactly the same tools.
"""

import random
import time

# ---------------------------------------------------------------------------
# Customer corpus — five customers, each carrying a distinct proactive moment
# drawn straight from the YONO Nexus narrative. Every record mirrors what the
# feature store would expose: balance, obligations, transaction patterns, and
# the funding sources the agent can act on.
# ---------------------------------------------------------------------------
_CUSTOMERS = {
    # ── Ramesh — the EMI rescue (the narrative's emotional peak) ───────────
    "CUST_RAMESH": {
        "id": "CUST_RAMESH",
        "name": "Ramesh Kumar Verma",
        "first_name": "Ramesh",
        "age": 47,
        "location": "Bhagalpur, Bihar",
        "preferred_lang": "hi",
        "mode": "sahaj",                       # behavioural profile → simple UI
        "balance_inr": 4200,
        "savings_rate_pa": 3.5,
        "obligations": [
            {"type": "emi", "label": "Home loan EMI", "amount_inr": 5000,
             "due_in_days": 2, "merchant": "SBI Home Loan", "recurring": "monthly"},
        ],
        "funding_sources": [
            {"type": "fd", "label": "Fixed Deposit", "available_inr": 85000,
             "liquid": True, "penalty": "nil (sweep-in linked)"},
        ],
        "patterns": ["emi_5000_monthly_5th", "kirana_upi_inflow_daily",
                     "balance_trending_down_week"],
        "scenario": "emi_shortfall",
    },

    # ── Sunita — school fee → education planning ───────────────────────────
    "CUST_SUNITA": {
        "id": "CUST_SUNITA",
        "name": "Sunita Devi",
        "first_name": "Sunita",
        "age": 38,
        "location": "Kanpur, UP",
        "preferred_lang": "hi",
        "mode": "sahaj",
        "balance_inr": 61000,
        "savings_rate_pa": 3.5,
        "obligations": [
            {"type": "school_fee", "label": "School fee (quarterly)",
             "amount_inr": 18000, "due_in_days": 21,
             "merchant": "Saraswati Vidya Mandir", "recurring": "quarterly"},
        ],
        "funding_sources": [
            {"type": "savings", "label": "Savings balance", "available_inr": 61000,
             "liquid": True, "penalty": "none"},
        ],
        "patterns": ["school_fee_quarterly_18k", "child_age_8_inferred",
                     "no_education_product_held"],
        "scenario": "education_planning",
    },

    # ── Arjun — salary credit → SIP continuation ───────────────────────────
    "CUST_ARJUN": {
        "id": "CUST_ARJUN",
        "name": "Arjun Mehta",
        "first_name": "Arjun",
        "age": 31,
        "location": "Pune, Maharashtra",
        "preferred_lang": "en",
        "mode": "pro",                         # confident user → data-rich UI
        "balance_inr": 142000,
        "savings_rate_pa": 3.5,
        "obligations": [],
        "funding_sources": [
            {"type": "savings", "label": "Savings balance", "available_inr": 142000,
             "liquid": True, "penalty": "none"},
        ],
        "patterns": ["salary_credit_82k_1st", "sip_3000_last_2_months",
                     "discretionary_spend_stable", "surplus_after_expenses_24k"],
        "scenario": "salary_sip",
    },

    # ── Kavita — idle balance → opportunity cost ───────────────────────────
    "CUST_KAVITA": {
        "id": "CUST_KAVITA",
        "name": "Kavita Nair",
        "first_name": "Kavita",
        "age": 44,
        "location": "Kochi, Kerala",
        "preferred_lang": "en",
        "mode": "pro",
        "balance_inr": 320000,
        "savings_rate_pa": 3.5,
        "obligations": [],
        "funding_sources": [
            {"type": "savings", "label": "Savings balance", "available_inr": 320000,
             "liquid": True, "penalty": "none"},
        ],
        "patterns": ["balance_idle_240_days", "no_fd_no_sip",
                     "monthly_inflow_outflow_balanced"],
        "scenario": "idle_balance",
    },

    # ── Mohammed — salary gap → financial-stress check-in ──────────────────
    "CUST_MOHAMMED": {
        "id": "CUST_MOHAMMED",
        "name": "Mohammed Irfan",
        "first_name": "Irfan",
        "age": 35,
        "location": "Hyderabad, Telangana",
        "preferred_lang": "hi",
        "mode": "sahaj",
        "balance_inr": 9800,
        "savings_rate_pa": 3.5,
        "obligations": [
            {"type": "emi", "label": "Two-wheeler loan EMI", "amount_inr": 3200,
             "due_in_days": 6, "merchant": "SBI Vehicle Loan", "recurring": "monthly"},
            {"type": "credit_card", "label": "Credit card min due", "amount_inr": 2100,
             "due_in_days": 9, "merchant": "SBI Card", "recurring": "monthly"},
        ],
        "funding_sources": [
            {"type": "savings", "label": "Savings balance", "available_inr": 9800,
             "liquid": True, "penalty": "none"},
        ],
        "patterns": ["salary_not_credited_2_months", "balance_declining",
                     "multiple_obligations_pending"],
        "scenario": "financial_stress",
    },
}

CUSTOMER_IDS = list(_CUSTOMERS.keys())


# ---------------------------------------------------------------------------
# Tool functions — each is one step in SAARTHI's proactive reasoning pipeline.
# ---------------------------------------------------------------------------

def get_account_snapshot(customer_id: str) -> dict:
    """Read the customer's current balance, savings rate, and profile from core banking."""
    time.sleep(0.12)
    c = _CUSTOMERS.get(customer_id)
    if not c:
        return {"ok": False, "error": f"customer '{customer_id}' not found"}
    return {
        "ok": True,
        "customer_id": customer_id,
        "name": c["name"],
        "balance_inr": c["balance_inr"],
        "savings_rate_pa": c["savings_rate_pa"],
        "preferred_lang": c["preferred_lang"],
        "mode": c["mode"],
    }


def scan_transactions(customer_id: str) -> dict:
    """Scan recent transactions for recurring patterns and behavioural signals."""
    time.sleep(0.18)
    c = _CUSTOMERS.get(customer_id, {})
    patterns = c.get("patterns", [])
    pattern_labels = {
        "emi_5000_monthly_5th": "₹5,000 EMI debited on the 5th, every month",
        "kirana_upi_inflow_daily": "Daily UPI inflows (kirana store receipts)",
        "balance_trending_down_week": "Balance trending down over the past week",
        "school_fee_quarterly_18k": "₹18,000 school fee every quarter",
        "child_age_8_inferred": "Recurring child-related spend → school-age child inferred",
        "no_education_product_held": "No education SIP or child plan currently held",
        "salary_credit_82k_1st": "₹82,000 salary credited on the 1st",
        "sip_3000_last_2_months": "₹3,000 SIP run for the last 2 months",
        "discretionary_spend_stable": "Discretionary spending stable month-on-month",
        "surplus_after_expenses_24k": "~₹24,000 surplus after monthly expenses",
        "balance_idle_240_days": "₹3.2L sitting idle for 240 days at 3.5%",
        "no_fd_no_sip": "No FD, no SIP — zero product diversification",
        "monthly_inflow_outflow_balanced": "Inflow ≈ outflow, surplus accumulating",
        "salary_not_credited_2_months": "Salary not credited for 2 consecutive months",
        "balance_declining": "Balance steadily declining",
        "multiple_obligations_pending": "Multiple obligations pending against low balance",
    }
    return {
        "ok": True,
        "customer_id": customer_id,
        "patterns_detected": [{"code": p, "description": pattern_labels.get(p, p)}
                              for p in patterns],
        "pattern_count": len(patterns),
    }


def detect_obligations(customer_id: str) -> dict:
    """Identify upcoming financial obligations (EMIs, fees, bills) and their due dates."""
    time.sleep(0.15)
    c = _CUSTOMERS.get(customer_id, {})
    obligations = c.get("obligations", [])
    total_due_soon = sum(o["amount_inr"] for o in obligations if o["due_in_days"] <= 7)
    return {
        "ok": True,
        "customer_id": customer_id,
        "obligations": obligations,
        "obligation_count": len(obligations),
        "total_due_within_7d_inr": total_due_soon,
    }


def compute_shortfall(customer_id: str) -> dict:
    """Compare balance against imminent obligations and compute any shortfall."""
    time.sleep(0.12)
    c = _CUSTOMERS.get(customer_id, {})
    balance = c.get("balance_inr", 0)
    imminent = [o for o in c.get("obligations", []) if o["due_in_days"] <= 7]
    total_imminent = sum(o["amount_inr"] for o in imminent)
    shortfall = max(total_imminent - balance, 0)
    return {
        "ok": True,
        "customer_id": customer_id,
        "balance_inr": balance,
        "imminent_obligations_inr": total_imminent,
        "shortfall_inr": shortfall,
        "at_risk": shortfall > 0,
        "imminent_items": [o["label"] for o in imminent],
    }


def find_funding_source(customer_id: str, amount_inr: int) -> dict:
    """Find the least-cost liquid source to cover a shortfall (e.g. sweep-in FD)."""
    time.sleep(0.14)
    c = _CUSTOMERS.get(customer_id, {})
    sources = sorted(c.get("funding_sources", []),
                     key=lambda s: 0 if s["type"] == "fd" else 1)
    chosen = None
    for s in sources:
        if s["available_inr"] >= amount_inr and s["liquid"]:
            chosen = s
            break
    return {
        "ok": True,
        "customer_id": customer_id,
        "amount_needed_inr": amount_inr,
        "funding_source": chosen,
        "feasible": chosen is not None,
    }


def compute_opportunity_cost(customer_id: str) -> dict:
    """Compute money already lost to idle balance vs. an FD at SBI's current rate."""
    time.sleep(0.12)
    c = _CUSTOMERS.get(customer_id, {})
    balance = c.get("balance_inr", 0)
    # find idle days from patterns (default 240)
    idle_days = 240 if any("idle" in p for p in c.get("patterns", [])) else 0
    fd_rate = 6.8
    savings_rate = c.get("savings_rate_pa", 3.5)
    spread = (fd_rate - savings_rate) / 100.0
    lost = round(balance * spread * (idle_days / 365.0))
    return {
        "ok": True,
        "customer_id": customer_id,
        "idle_balance_inr": balance,
        "idle_days": idle_days,
        "fd_rate_pa": fd_rate,
        "savings_rate_pa": savings_rate,
        "opportunity_cost_inr": lost,
    }


def recommend_action(customer_id: str, scenario: str) -> dict:
    """Craft the proactive nudge: the right help, in the right language, at the right moment."""
    time.sleep(0.18)
    c = _CUSTOMERS.get(customer_id, {})
    name = c.get("first_name", "")
    lang = c.get("preferred_lang", "en")

    # Each scenario carries a bilingual nudge, a one-tap action, and a product CTA.
    nudges = {
        "emi_shortfall": {
            "title_en": "EMI shortfall — act before it bounces",
            "title_hi": "EMI में कमी — बाउंस होने से पहले कार्रवाई करें",
            "msg_en": (f"{name} ji, your ₹5,000 EMI is due in 2 days, but your account "
                       f"has only ₹4,200. Shall I transfer ₹800 from your FD? One tap "
                       f"and it's done — no bounce, no penalty."),
            "msg_hi": (f"{name} जी, आपकी ₹5,000 EMI परसों है, लेकिन आपके खाते में सिर्फ "
                       f"₹4,200 हैं। आपके FD से ₹800 ट्रांसफर कर दूँ? एक टैप में हो जाएगा — "
                       f"न बाउंस, न पेनल्टी।"),
            "cta": "Transfer ₹800 from FD",
            "action_type": "sweep_transfer",
            "urgency": "HIGH",
        },
        "education_planning": {
            "title_en": "School fee is recurring — plan ahead",
            "title_hi": "स्कूल फीस आ रही है — पहले से योजना बनाएं",
            "msg_en": (f"{name} ji, your ₹18,000 school fee is due in 3 weeks. This repeats "
                       f"every quarter. A small Child Education SIP could cover it "
                       f"automatically and grow a fund for higher studies. Want to see how?"),
            "msg_hi": (f"{name} जी, ₹18,000 की स्कूल फीस का समय आ रहा है — यह हर तिमाही आती "
                       f"है। एक छोटी Child Education SIP इसे अपने-आप संभाल सकती है और उच्च "
                       f"शिक्षा के लिए फंड भी बना सकती है। देखना चाहेंगे?"),
            "cta": "Explore Child Education SIP",
            "action_type": "product_explore",
            "urgency": "MEDIUM",
        },
        "salary_sip": {
            "title_en": "Salary credited — keep your SIP going",
            "title_hi": "सैलरी आ गई — अपनी SIP जारी रखें",
            "msg_en": (f"Hi {name}, your salary just arrived. Last month you set aside "
                       f"₹3,000 in a SIP. You have ₹24,000 surplus this month — continue "
                       f"the ₹3,000 SIP, or step it up to ₹5,000?"),
            "msg_hi": (f"नमस्ते {name}, आपकी सैलरी आ गई है। पिछले महीने आपने ₹3,000 SIP में "
                       f"डाले थे। इस महीने ₹24,000 सरप्लस है — ₹3,000 SIP जारी रखें, या "
                       f"₹5,000 कर दें?"),
            "cta": "Continue SIP · ₹3,000",
            "action_type": "sip_continue",
            "urgency": "MEDIUM",
        },
        "idle_balance": {
            "title_en": "₹3.2L is sitting idle — put it to work",
            "title_hi": "₹3.2L बेकार पड़ा है — उसे काम पर लगाएं",
            "msg_en": (f"Hi {name}, ₹3,20,000 has been idle in savings for 240 days at "
                       f"3.5%. At SBI's 6.8% FD rate, you've already missed ₹"
                       f"{compute_opportunity_cost(customer_id)['opportunity_cost_inr']:,} "
                       f"in returns. Move it to an FD in one tap?"),
            "msg_hi": (f"नमस्ते {name}, ₹3,20,000 पिछले 240 दिनों से सिर्फ 3.5% पर पड़ा है। "
                       f"SBI की 6.8% FD दर पर आप पहले ही ₹"
                       f"{compute_opportunity_cost(customer_id)['opportunity_cost_inr']:,} "
                       f"का रिटर्न खो चुके हैं। एक टैप में FD में डालें?"),
            "cta": "Open FD · ₹3,20,000",
            "action_type": "fd_open",
            "urgency": "MEDIUM",
        },
        "financial_stress": {
            "title_en": "Salary delayed — let's protect your record",
            "title_hi": "सैलरी में देरी — आपका रिकॉर्ड सुरक्षित रखें",
            "msg_en": (f"{name} ji, we noticed your salary hasn't come in for 2 months and "
                       f"you have ₹5,300 in dues this week against a ₹9,800 balance. "
                       f"We can pause one EMI penalty-free or set a flexible mini-repayment. "
                       f"Shall I show your options? No charges to talk."),
            "msg_hi": (f"{name} जी, हमने देखा कि 2 महीने से सैलरी नहीं आई और इस हफ्ते ₹5,300 "
                       f"के भुगतान बाकी हैं, जबकि बैलेंस ₹9,800 है। हम एक EMI बिना पेनल्टी "
                       f"रोक सकते हैं या एक लचीला छोटा भुगतान सेट कर सकते हैं। विकल्प "
                       f"दिखाऊँ? बात करने का कोई शुल्क नहीं।"),
            "cta": "See relief options",
            "action_type": "hardship_support",
            "urgency": "HIGH",
        },
    }

    n = nudges.get(scenario, nudges["emi_shortfall"])
    return {
        "ok": True,
        "customer_id": customer_id,
        "scenario": scenario,
        "title": n["title_hi"] if lang == "hi" else n["title_en"],
        "message": n["msg_hi"] if lang == "hi" else n["msg_en"],
        "cta": n["cta"],
        "action_type": n["action_type"],
        "urgency": n["urgency"],
        "language": lang,
    }


def execute_nudge(customer_id: str, action_type: str) -> dict:
    """Queue the proactive nudge for delivery via the customer's preferred channel."""
    time.sleep(0.10)
    c = _CUSTOMERS.get(customer_id, {})
    return {
        "ok": True,
        "customer_id": customer_id,
        "action_type": action_type,
        "channel": "YONO push notification" + (" (Hindi)" if c.get("preferred_lang") == "hi" else ""),
        "delivery": "QUEUED",
        "consent_checked": True,
        "explainable": True,
        "nudge_id": f"SAARTHI-{customer_id}-{random.randint(1000, 9999)}",
    }


def get_engagement_metrics() -> dict:
    """Aggregate SAARTHI engagement metrics for the dashboard."""
    time.sleep(0.10)
    return {
        "ok": True,
        "customers_monitored": 41200000,
        "proactive_nudges_7d": 2840000,
        "acted_on_7d": 1050000,
        "act_rate_pct": 37,
        "emi_bounces_prevented_7d": 18400,
        "idle_balance_activated_inr": 940000000,
        "avg_response_minutes": 8,
    }


# ---------------------------------------------------------------------------
# Dispatch table + Claude-facing tool schemas.
# ---------------------------------------------------------------------------
TOOL_FUNCS = {
    "get_account_snapshot": get_account_snapshot,
    "scan_transactions": scan_transactions,
    "detect_obligations": detect_obligations,
    "compute_shortfall": compute_shortfall,
    "find_funding_source": find_funding_source,
    "compute_opportunity_cost": compute_opportunity_cost,
    "recommend_action": recommend_action,
    "execute_nudge": execute_nudge,
}

TOOL_SCHEMAS = [
    {
        "name": "get_account_snapshot",
        "description": ("Read the customer's current balance, savings rate, preferred "
                        "language, and UI mode from core banking. Call this first."),
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "scan_transactions",
        "description": ("Scan recent transactions for recurring patterns and behavioural "
                        "signals (EMIs, fees, salary credits, idle balance)."),
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "detect_obligations",
        "description": "Identify upcoming financial obligations (EMIs, fees, bills) and due dates.",
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "compute_shortfall",
        "description": ("Compare the balance against imminent obligations and compute any "
                        "shortfall and whether the customer is at risk of a bounce."),
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "find_funding_source",
        "description": ("Find the least-cost liquid source (e.g. a sweep-in FD) to cover a "
                        "shortfall amount without penalty."),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "amount_inr": {"type": "integer"},
            },
            "required": ["customer_id", "amount_inr"],
        },
    },
    {
        "name": "compute_opportunity_cost",
        "description": ("Compute the returns already lost to an idle balance versus an FD at "
                        "SBI's current rate."),
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "recommend_action",
        "description": ("Craft the proactive nudge: the right help, in the customer's language, "
                        "with a one-tap action and a product CTA. Pass the detected scenario."),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "scenario": {"type": "string",
                             "enum": ["emi_shortfall", "education_planning", "salary_sip",
                                      "idle_balance", "financial_stress"]},
            },
            "required": ["customer_id", "scenario"],
        },
    },
    {
        "name": "execute_nudge",
        "description": ("Queue the proactive nudge for delivery via the customer's preferred "
                        "channel, with consent and explainability checks. Call this last."),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "action_type": {"type": "string"},
            },
            "required": ["customer_id", "action_type"],
        },
    },
]
