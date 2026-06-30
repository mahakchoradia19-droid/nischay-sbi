"""
profiles.py — realistic synthetic customer profiles for FinPulse.

Deliberately shared with the SAARTHI / SCOUT personas so ONE customer flows
across the whole of YONO Nexus: SCOUT acquires them, onboarding opens the
account, FinPulse scores them, SAARTHI acts on the weakest dimension, the
Academy teaches the concept behind it. All amounts in INR.

These are synthetic but internally consistent (income, expense, saving and
balances reconcile), so the computed score is meaningful — not a hand-typed
headline number.
"""

PROFILES = {
    # Ramesh — the narrative's kirana owner; thin buffer, idle cash, underinsured
    "CUST_RAMESH": {
        "id": "CUST_RAMESH", "name": "Ramesh Kumar Verma", "age": 47,
        "location": "Bhagalpur, Bihar", "segment": "Self-employed · Bharat",
        "monthly_income": 42000, "monthly_expense": 31000, "monthly_saving": 4200,
        "liquid_balance": 48000, "invested_balance": 85000, "dependents": 3,
        "life_cover": 200000, "health_cover": 0,
        "card_utilisation": 0.0, "emi_to_income": 0.12, "missed_payments_12m": 0,
        "has_fd": True, "has_sip": False, "has_ppf": False,
        "has_insurance": False, "has_rd": False,
        "goal_progress_pct": 25,
    },
    # Sunita — salaried-adjacent, building, has RD habit, no protection
    "CUST_SUNITA": {
        "id": "CUST_SUNITA", "name": "Sunita Devi", "age": 38,
        "location": "Kanpur, UP", "segment": "Homemaker · saver",
        "monthly_income": 35000, "monthly_expense": 24000, "monthly_saving": 8000,
        "liquid_balance": 61000, "invested_balance": 140000, "dependents": 2,
        "life_cover": 0, "health_cover": 300000,
        "card_utilisation": 0.0, "emi_to_income": 0.0, "missed_payments_12m": 0,
        "has_fd": True, "has_sip": False, "has_ppf": True,
        "has_insurance": False, "has_rd": True,
        "goal_progress_pct": 45,
    },
    # Arjun — urban engineer, high income, disciplined, well diversified
    "CUST_ARJUN": {
        "id": "CUST_ARJUN", "name": "Arjun Mehta", "age": 31,
        "location": "Pune, Maharashtra", "segment": "Salaried · urban",
        "monthly_income": 145000, "monthly_expense": 78000, "monthly_saving": 45000,
        "liquid_balance": 520000, "invested_balance": 1400000, "dependents": 1,
        "life_cover": 15000000, "health_cover": 1000000,
        "card_utilisation": 0.18, "emi_to_income": 0.22, "missed_payments_12m": 0,
        "has_fd": True, "has_sip": True, "has_ppf": True,
        "has_insurance": True, "has_rd": False,
        "goal_progress_pct": 68,
    },
    # Kavita — high idle cash, no investing, underutilised wealth
    "CUST_KAVITA": {
        "id": "CUST_KAVITA", "name": "Kavita Nair", "age": 44,
        "location": "Kochi, Kerala", "segment": "Salaried · idle-rich",
        "monthly_income": 90000, "monthly_expense": 52000, "monthly_saving": 30000,
        "liquid_balance": 3200000, "invested_balance": 0, "dependents": 2,
        "life_cover": 2000000, "health_cover": 500000,
        "card_utilisation": 0.05, "emi_to_income": 0.0, "missed_payments_12m": 0,
        "has_fd": False, "has_sip": False, "has_ppf": False,
        "has_insurance": True, "has_rd": False,
        "goal_progress_pct": 30,
    },
    # Irfan — financial stress: salary gap, high utilisation, missed payments
    "CUST_MOHAMMED": {
        "id": "CUST_MOHAMMED", "name": "Mohammed Irfan", "age": 35,
        "location": "Hyderabad, Telangana", "segment": "Salaried · stressed",
        "monthly_income": 48000, "monthly_expense": 41000, "monthly_saving": 2000,
        "liquid_balance": 9800, "invested_balance": 12000, "dependents": 2,
        "life_cover": 0, "health_cover": 0,
        "card_utilisation": 0.82, "emi_to_income": 0.46, "missed_payments_12m": 2,
        "has_fd": False, "has_sip": False, "has_ppf": False,
        "has_insurance": False, "has_rd": False,
        "goal_progress_pct": 10,
    },
    # Priya — young professional, just started, thin everything
    "CUST_PRIYA": {
        "id": "CUST_PRIYA", "name": "Priya Sharma", "age": 26,
        "location": "Bengaluru, Karnataka", "segment": "Salaried · starter",
        "monthly_income": 62000, "monthly_expense": 44000, "monthly_saving": 14000,
        "liquid_balance": 95000, "invested_balance": 60000, "dependents": 0,
        "life_cover": 0, "health_cover": 500000,
        "card_utilisation": 0.34, "emi_to_income": 0.10, "missed_payments_12m": 1,
        "has_fd": False, "has_sip": True, "has_ppf": False,
        "has_insurance": False, "has_rd": False,
        "goal_progress_pct": 35,
    },
}

PROFILE_IDS = list(PROFILES.keys())
