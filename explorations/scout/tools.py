"""
SCOUT Agent — simulated prospect intelligence tool layer.

In production each function is a call to SBI's data warehouse, partner APIs,
or a real-time feature store. Here they are deterministic stubs so the demo
runs with zero setup and zero network.

Three acquisition channels:
  1. Dormant Jan Dhan reactivation  — 48 crore PMJDY accounts, 15% zero-balance
  2. Employer partnership pipeline  — salary credit network analysis
  3. Life event detection           — transaction pattern → life moment → product fit

The schemas at the bottom (TOOL_SCHEMAS) are handed to Claude when a key is set,
so the live and offline paths call exactly the same tools.
"""

import random
import time

# ---------------------------------------------------------------------------
# Prospect corpus — 9 realistic SBI prospects across three channels.
# Each entry mirrors what a feature store would expose to the agent.
# ---------------------------------------------------------------------------
_PROSPECTS = {
    # ── Dormant Jan Dhan ──────────────────────────────────────────────────
    "JD_001": {
        "id": "JD_001",
        "name": "Priya Devi Sharma",
        "age": 34,
        "location": "Varanasi, UP",
        "segment": "dormant_jan_dhan",
        "balance_inr": 2400,
        "last_txn_days_ago": 214,
        "yono_installed": False,
        "dbt_eligible": True,
        "preferred_lang": "hi",
        "signals": ["dbt_pending_2000", "no_digital_touch", "zero_product_diversity"],
        "trigger_summary": "DBT credit of ₹2,000 pending — account needs reactivation first",
        "recommended_product": "YONO onboarding + PM Kisan DBT activation",
        "channel": "SMS (Hindi) → missed-call callback",
    },
    "JD_002": {
        "id": "JD_002",
        "name": "Mohammed Irfan Shaikh",
        "age": 52,
        "location": "Lucknow, UP",
        "segment": "dormant_jan_dhan",
        "balance_inr": 8750,
        "last_txn_days_ago": 308,
        "yono_installed": False,
        "dbt_eligible": False,
        "preferred_lang": "hi",
        "signals": ["idle_balance_high", "no_yono_login_ever", "branch_distance_far"],
        "trigger_summary": "₹8,750 idle for 10 months — at 3.5% savings, ₹306 opportunity cost",
        "recommended_product": "Doorstep FD + YONO activation via video call",
        "channel": "Outbound call (Hindi) → WhatsApp deeplink",
    },
    "JD_003": {
        "id": "JD_003",
        "name": "Sunita Kumari",
        "age": 27,
        "location": "Patna, Bihar",
        "segment": "dormant_jan_dhan",
        "balance_inr": 500,
        "last_txn_days_ago": 45,
        "yono_installed": False,
        "dbt_eligible": True,
        "preferred_lang": "hi",
        "signals": ["first_salary_credit_3_months_ago", "anganwadi_worker_profile", "dbt_eligible"],
        "trigger_summary": "Started receiving ₹6,000/month salary 3 months ago — newly employed",
        "recommended_product": "RD ₹500/month + accidental insurance ₹12/year",
        "channel": "YONO Lite onboarding (2G-compatible) + SHG referral",
    },

    # ── Employer Partnership ───────────────────────────────────────────────
    "EP_001": {
        "id": "EP_001",
        "name": "TCS Pune — Salary Banking Opportunity",
        "age": None,
        "location": "Pune, Maharashtra",
        "segment": "employer_partnership",
        "employees_total": 4200,
        "employees_non_sbi": 1847,
        "avg_salary_inr": 82000,
        "current_sbi_penetration_pct": 56,
        "preferred_lang": "en",
        "signals": ["payroll_visible_in_sbi_network", "low_sbi_penetration", "it_sector_high_fds"],
        "trigger_summary": "1,847 employees route salary to competitor banks — ₹15.1 Cr monthly outflow",
        "recommended_product": "SBI Corporate Salary Package + 0.25% FD rate sweetener for joiners",
        "channel": "HR partnership email + YONO onboarding QR at office",
    },
    "EP_002": {
        "id": "EP_002",
        "name": "Surat Diamond MSME Cluster",
        "age": None,
        "location": "Surat, Gujarat",
        "segment": "employer_partnership",
        "employees_total": 680,
        "employees_non_sbi": 412,
        "avg_salary_inr": 24000,
        "current_sbi_penetration_pct": 39,
        "preferred_lang": "gu",
        "signals": ["cash_heavy_sector", "low_digital_banking", "gstn_registered_msme"],
        "trigger_summary": "412 workers paid in cash — SBI account + UPI would formalize their income",
        "recommended_product": "Jan Dhan Plus + SBI MUDRA loan pre-approval for employers",
        "channel": "Cluster camp banking + Gujarati-language YONO demo",
    },
    "EP_003": {
        "id": "EP_003",
        "name": "Delhi NCR Govt School Teachers",
        "age": None,
        "location": "Delhi NCR",
        "segment": "employer_partnership",
        "employees_total": 3100,
        "employees_non_sbi": 940,
        "avg_salary_inr": 55000,
        "current_sbi_penetration_pct": 70,
        "preferred_lang": "hi",
        "signals": ["govt_employee_pension_eligible", "sbi_already_trusted_here", "30pct_gap_closeable"],
        "trigger_summary": "940 teachers on other banks — all eligible for SBI Govt Employee pension scheme",
        "recommended_product": "SBI Pension Sahyog + NPS through SBI",
        "channel": "School principal partnership + Hindi letter + YONO demo at school",
    },

    # ── Life Event Detection ───────────────────────────────────────────────
    "LE_001": {
        "id": "LE_001",
        "name": "Rahul Verma",
        "age": 29,
        "location": "Bengaluru, Karnataka",
        "segment": "life_event",
        "life_event": "new_parent",
        "confidence_pct": 91,
        "signals": [
            "baby_care_merchant_cluster_6wk",
            "hospital_maternity_payment_72k",
            "pharmacy_spend_3x_baseline",
            "sleep_pattern_shift_in_upi_timestamps",
        ],
        "trigger_summary": "Transaction cluster strongly indicates a newborn in the last 6 weeks",
        "recommended_product": "Child Education SIP ₹2,000/month + Term Insurance ₹1 Cr",
        "channel": "YONO push notification (Kannada/English) → in-app card",
        "preferred_lang": "en",
    },
    "LE_002": {
        "id": "LE_002",
        "name": "Kavita Nair",
        "age": 32,
        "location": "Chennai, Tamil Nadu",
        "segment": "life_event",
        "life_event": "home_purchase_intent",
        "confidence_pct": 87,
        "signals": [
            "rent_payments_stopped_2_months",
            "home_improvement_merchant_spend_up_400pct",
            "stamp_duty_payment_detected",
            "interior_design_consultant_upi",
        ],
        "trigger_summary": "Rent stopped, stamp duty paid, home improvement surge — likely just bought a flat",
        "recommended_product": "Home Loan top-up + SBI Home Insurance + SBI Max Gain OD",
        "channel": "YONO in-app congratulations card → product deeplink",
        "preferred_lang": "en",
    },
    "LE_003": {
        "id": "LE_003",
        "name": "Arjun Singh Rawat",
        "age": 24,
        "location": "Mumbai, Maharashtra",
        "segment": "life_event",
        "life_event": "first_job_new_city",
        "confidence_pct": 95,
        "signals": [
            "first_salary_credit_last_month",
            "address_change_detected_via_upi_merchants",
            "pg_accommodation_rent_started",
            "metro_card_recharge_cluster",
            "food_delivery_heavy_user",
        ],
        "trigger_summary": "First salary 28 days ago, moved to Mumbai from UP — career start, new city",
        "recommended_product": "SBI Simply SAVE Credit Card + RD ₹3,000/month + Term Plan",
        "channel": "WhatsApp onboarding in Hindi → YONO activation → credit card pre-approval",
        "preferred_lang": "hi",
    },
}

PROSPECT_IDS = list(_PROSPECTS.keys())
SEGMENT_LABELS = {
    "dormant_jan_dhan": "Dormant Jan Dhan",
    "employer_partnership": "Employer Partnership",
    "life_event": "Life Event",
}


# ---------------------------------------------------------------------------
# Tool functions — each simulates one step in the SCOUT reasoning pipeline.
# ---------------------------------------------------------------------------

def get_prospect_profile(prospect_id: str) -> dict:
    """Retrieve full prospect profile from the customer intelligence feature store."""
    time.sleep(0.15)
    p = _PROSPECTS.get(prospect_id)
    if not p:
        return {"ok": False, "error": f"prospect '{prospect_id}' not found"}
    return {"ok": True, "prospect": dict(p)}


def analyze_signals(prospect_id: str) -> dict:
    """Run signal analysis: weight each signal, identify the primary acquisition trigger."""
    time.sleep(0.2)
    p = _PROSPECTS.get(prospect_id, {})
    signals = p.get("signals", [])
    segment = p.get("segment", "unknown")

    # deterministic signal scoring
    weights = {
        "dbt_pending_2000": 0.92, "no_digital_touch": 0.78, "zero_product_diversity": 0.65,
        "idle_balance_high": 0.85, "no_yono_login_ever": 0.80, "branch_distance_far": 0.60,
        "first_salary_credit_3_months_ago": 0.88, "anganwadi_worker_profile": 0.72,
        "dbt_eligible": 0.84,
        "payroll_visible_in_sbi_network": 0.95, "low_sbi_penetration": 0.90,
        "it_sector_high_fds": 0.75,
        "cash_heavy_sector": 0.82, "low_digital_banking": 0.79, "gstn_registered_msme": 0.70,
        "govt_employee_pension_eligible": 0.93, "sbi_already_trusted_here": 0.88,
        "30pct_gap_closeable": 0.76,
        "baby_care_merchant_cluster_6wk": 0.91, "hospital_maternity_payment_72k": 0.95,
        "pharmacy_spend_3x_baseline": 0.83, "sleep_pattern_shift_in_upi_timestamps": 0.71,
        "rent_payments_stopped_2_months": 0.88, "home_improvement_merchant_spend_up_400pct": 0.86,
        "stamp_duty_payment_detected": 0.97, "interior_design_consultant_upi": 0.79,
        "first_salary_credit_last_month": 0.96, "address_change_detected_via_upi_merchants": 0.89,
        "pg_accommodation_rent_started": 0.85, "metro_card_recharge_cluster": 0.72,
        "food_delivery_heavy_user": 0.63,
    }
    scored = sorted(
        [(s, weights.get(s, 0.5)) for s in signals],
        key=lambda x: -x[1]
    )
    top_signal, top_weight = scored[0] if scored else ("unknown", 0.5)
    composite = round(sum(w for _, w in scored) / max(len(scored), 1), 3)

    return {
        "ok": True,
        "prospect_id": prospect_id,
        "segment": segment,
        "signal_count": len(signals),
        "scored_signals": scored,
        "primary_trigger": top_signal,
        "primary_trigger_weight": top_weight,
        "composite_intent_score": composite,
        "acquisition_urgency": "HIGH" if composite > 0.82 else "MEDIUM" if composite > 0.70 else "LOW",
    }


def score_prospect(prospect_id: str) -> dict:
    """Compute conversion probability using historical cohort data for this segment × trigger pair."""
    time.sleep(0.15)
    p = _PROSPECTS.get(prospect_id, {})
    segment = p.get("segment", "unknown")

    # cohort-based conversion rates from SBI historical data (mock)
    base_rates = {
        "dormant_jan_dhan": 0.31,
        "employer_partnership": 0.58,
        "life_event": 0.47,
    }
    base = base_rates.get(segment, 0.30)
    # nudge by confidence if available
    confidence = p.get("confidence_pct", 80) / 100.0
    adjusted = round(min(base * confidence + 0.05, 0.97), 2)

    clv_map = {
        "dormant_jan_dhan": 4200,
        "employer_partnership": 38000,
        "life_event": 22000,
    }
    return {
        "ok": True,
        "prospect_id": prospect_id,
        "conversion_probability": adjusted,
        "expected_clv_inr": clv_map.get(segment, 10000),
        "payback_months": 4 if segment == "employer_partnership" else 11,
        "cohort_sample_size": random.randint(12000, 48000),
        "recommended_action": "PRIORITISE" if adjusted > 0.50 else "NURTURE",
    }


def generate_offer(prospect_id: str) -> dict:
    """Craft a hyper-personalised offer and outreach message for this prospect."""
    time.sleep(0.20)
    p = _PROSPECTS.get(prospect_id, {})
    lang = p.get("preferred_lang", "en")
    name = p.get("name", "Valued Customer")
    product = p.get("recommended_product", "SBI savings account")
    trigger = p.get("trigger_summary", "")

    templates = {
        "dormant_jan_dhan": {
            "en": (f"Hello {name}, your SBI account has been waiting for you! "
                   f"We've noticed: {trigger}. Activate YONO today — it takes 2 minutes — "
                   f"and unlock {product}. Reply YES for a callback."),
            "hi": (f"नमस्ते {name}, आपका SBI खाता आपका इंतज़ार कर रहा है! "
                   f"हमने देखा: {trigger}। आज YONO चालू करें — सिर्फ 2 मिनट — "
                   f"और {product} का लाभ उठाएं। कॉलबैक के लिए YES लिखें।"),
        },
        "employer_partnership": {
            "en": (f"Dear HR/Finance Team at {name}, "
                   f"SBI has identified a salary-banking opportunity: {trigger}. "
                   f"We offer {product} with dedicated relationship manager support. "
                   f"Schedule a 20-minute demo at your convenience."),
            "gu": (f"પ્રિય {name} ટીમ, SBI એ પગારદાર-બેંકિંગ તક ઓળખી છે: {trigger}. "
                   f"અમે {product} ઓફર કરીએ છીએ. 20 મિનિટના ડેમો માટે સમય નક્કી કરો."),
        },
        "life_event": {
            "en": (f"Hi {name}, congratulations on this new chapter! "
                   f"Based on your recent activity, we noticed: {trigger}. "
                   f"SBI has a personalised offer ready for you: {product}. "
                   f"Open YONO → tap the banner. Takes under 3 minutes."),
            "hi": (f"नमस्ते {name}, इस नई शुरुआत की बधाई! "
                   f"आपकी हाल की गतिविधि से लगा: {trigger}। "
                   f"SBI ने आपके लिए एक व्यक्तिगत ऑफर तैयार किया है: {product}। "
                   f"YONO खोलें → बैनर पर टैप करें। 3 मिनट से कम।"),
        },
    }

    segment = p.get("segment", "life_event")
    lang_map = templates.get(segment, templates["life_event"])
    message = lang_map.get(lang, lang_map.get("en", ""))

    return {
        "ok": True,
        "prospect_id": prospect_id,
        "outreach_message": message,
        "language": lang,
        "channel": p.get("channel", "YONO push notification"),
        "product": product,
        "offer_expires_days": 7,
        "personalisation_tokens": ["name", "trigger", "product", "channel"],
    }


def log_outreach(prospect_id: str, channel: str, message_preview: str) -> dict:
    """Queue the outreach in the CRM campaign manager (audit trail)."""
    time.sleep(0.10)
    campaign_id = f"SCOUT-{prospect_id}-{random.randint(10000, 99999)}"
    return {
        "ok": True,
        "campaign_id": campaign_id,
        "prospect_id": prospect_id,
        "channel": channel,
        "status": "QUEUED",
        "scheduled_at": "next_available_slot",
        "compliance_check": "PASSED",
        "dnd_registry_checked": True,
    }


def get_pipeline_metrics() -> dict:
    """Return aggregate SCOUT pipeline metrics for the dashboard."""
    time.sleep(0.10)
    return {
        "ok": True,
        "prospects_identified_7d": 14820,
        "high_intent_leads": 3241,
        "outreach_sent_7d": 8904,
        "conversions_7d": 1247,
        "conversion_rate_pct": 14.0,
        "revenue_influenced_inr": 28400000,
        "top_segment": "life_event",
        "top_segment_conversion_pct": 47,
        "cost_per_acquisition_inr": 210,
        "traditional_cac_inr": 1450,
        "cac_reduction_pct": 85,
    }


# ---------------------------------------------------------------------------
# Dispatch table + Claude-facing tool schemas.
# ---------------------------------------------------------------------------
TOOL_FUNCS = {
    "get_prospect_profile": get_prospect_profile,
    "analyze_signals": analyze_signals,
    "score_prospect": score_prospect,
    "generate_offer": generate_offer,
    "log_outreach": log_outreach,
}

TOOL_SCHEMAS = [
    {
        "name": "get_prospect_profile",
        "description": (
            "Retrieve the full prospect profile from the SCOUT feature store. "
            "Always call this first to understand who the prospect is."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"prospect_id": {"type": "string"}},
            "required": ["prospect_id"],
        },
    },
    {
        "name": "analyze_signals",
        "description": (
            "Run signal analysis on the prospect: weight each behavioural signal, "
            "identify the primary acquisition trigger, and compute a composite intent score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"prospect_id": {"type": "string"}},
            "required": ["prospect_id"],
        },
    },
    {
        "name": "score_prospect",
        "description": (
            "Compute conversion probability using cohort data for this segment × trigger pair. "
            "Returns conversion_probability, expected CLV, and recommended action."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"prospect_id": {"type": "string"}},
            "required": ["prospect_id"],
        },
    },
    {
        "name": "generate_offer",
        "description": (
            "Generate a hyper-personalised outreach message and product offer for this prospect. "
            "Uses the prospect's preferred language, key trigger, and best-fit SBI product."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"prospect_id": {"type": "string"}},
            "required": ["prospect_id"],
        },
    },
    {
        "name": "log_outreach",
        "description": (
            "Queue the outreach message in the CRM campaign manager for compliance-checked delivery. "
            "Always call this last, after the offer is finalised."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_id": {"type": "string"},
                "channel": {"type": "string"},
                "message_preview": {"type": "string"},
            },
            "required": ["prospect_id", "channel", "message_preview"],
        },
    },
]
