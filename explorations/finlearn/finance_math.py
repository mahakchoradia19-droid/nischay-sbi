"""
finance_math.py — REAL financial calculators.

Every number the FinSmart Academy teaches or quizzes is COMPUTED here, not
hardcoded. This is what makes the learning genuine (the worked examples are
correct by construction) and the question engine agentic (it can generate
infinite fresh, always-correct questions by randomising inputs and computing
the answer). Pure functions, stdlib only, fully testable.

All money is in INR, rounded to whole rupees unless noted.
"""

# ---------------------------------------------------------------------------
# Interest
# ---------------------------------------------------------------------------

def simple_interest(principal: float, rate_pa: float, years: float) -> dict:
    """Simple interest: I = P·r·t. Interest does NOT earn interest."""
    interest = principal * (rate_pa / 100.0) * years
    return {"interest": round(interest), "maturity": round(principal + interest)}


def compound_interest(principal: float, rate_pa: float, years: float,
                      comp_per_year: int = 1) -> dict:
    """Compound interest: A = P(1 + r/n)^(n·t). Interest earns interest."""
    n = comp_per_year
    amount = principal * (1 + (rate_pa / 100.0) / n) ** (n * years)
    return {"maturity": round(amount), "interest": round(amount - principal)}


def rule_of_72(rate_pa: float) -> float:
    """Approx years for money to double at a given annual rate."""
    return round(72.0 / rate_pa, 1) if rate_pa else float("inf")


# ---------------------------------------------------------------------------
# Bank deposits
# ---------------------------------------------------------------------------

def fd_maturity(principal: float, rate_pa: float, years: float,
                comp_per_year: int = 4) -> dict:
    """Fixed Deposit — banks compound quarterly by convention."""
    return compound_interest(principal, rate_pa, years, comp_per_year)


def rd_maturity(monthly: float, rate_pa: float, months: int) -> dict:
    """
    Recurring Deposit maturity (quarterly compounding, the standard bank formula).
    Each instalment earns interest for the remaining months.
    """
    r = (rate_pa / 100.0) / 4.0          # quarterly rate
    total = 0.0
    for k in range(months):
        # instalment k stays invested for (months-k) months = quarters fraction
        quarters = (months - k) / 3.0
        total += monthly * (1 + r) ** quarters
    invested = monthly * months
    return {"maturity": round(total), "invested": round(invested),
            "interest": round(total - invested)}


def ppf_maturity(annual_contribution: float, rate_pa: float = 7.1,
                 years: int = 15) -> dict:
    """PPF — annual compounding, 15-year lock-in, tax-free."""
    total = 0.0
    for k in range(years):
        total = (total + annual_contribution) * (1 + rate_pa / 100.0)
    invested = annual_contribution * years
    return {"maturity": round(total), "invested": round(invested),
            "interest": round(total - invested)}


def sip_future_value(monthly: float, rate_pa: float, months: int) -> dict:
    """SIP future value with monthly compounding (annuity-due-ish, end of month)."""
    r = (rate_pa / 100.0) / 12.0
    if r == 0:
        fv = monthly * months
    else:
        fv = monthly * (((1 + r) ** months - 1) / r)
    invested = monthly * months
    return {"future_value": round(fv), "invested": round(invested),
            "gain": round(fv - invested)}


# ---------------------------------------------------------------------------
# Loans
# ---------------------------------------------------------------------------

def emi_reducing(principal: float, rate_pa: float, months: int) -> dict:
    """EMI on a reducing-balance loan (how real home/personal loans work)."""
    r = (rate_pa / 100.0) / 12.0
    if r == 0:
        emi = principal / months
    else:
        emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    total = emi * months
    return {"emi": round(emi), "total_paid": round(total),
            "total_interest": round(total - principal)}


def flat_vs_reducing(principal: float, flat_rate_pa: float, months: int) -> dict:
    """
    Show why a 'flat' rate is more expensive than the same 'reducing' rate.
    A flat 10% is NOT a 10% loan — its effective reducing rate is much higher.
    """
    years = months / 12.0
    flat_interest = principal * (flat_rate_pa / 100.0) * years
    flat_total = principal + flat_interest
    flat_emi = flat_total / months
    # find the reducing rate that yields the same EMI (binary search)
    lo, hi = 0.0, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2
        e = emi_reducing(principal, mid, months)["emi"]
        if e > flat_emi:
            hi = mid
        else:
            lo = mid
    return {"flat_emi": round(flat_emi), "flat_total_interest": round(flat_interest),
            "effective_reducing_rate": round((lo + hi) / 2, 2)}


# ---------------------------------------------------------------------------
# Time value of money & inflation
# ---------------------------------------------------------------------------

def future_value(pv: float, rate_pa: float, years: float) -> float:
    return round(pv * (1 + rate_pa / 100.0) ** years)


def present_value(fv: float, rate_pa: float, years: float) -> float:
    return round(fv / (1 + rate_pa / 100.0) ** years)


def inflation_adjusted(amount: float, inflation_pa: float, years: float) -> float:
    """What today's `amount` of purchasing power is worth after inflation."""
    return round(amount / (1 + inflation_pa / 100.0) ** years)


def real_return(nominal_pa: float, inflation_pa: float) -> float:
    """Fisher real return: ((1+nom)/(1+inf) - 1). The return that actually matters."""
    real = ((1 + nominal_pa / 100.0) / (1 + inflation_pa / 100.0) - 1) * 100
    return round(real, 2)


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

def credit_card_interest(outstanding: float, monthly_rate: float,
                         days: int = 30) -> dict:
    """
    Credit-card finance charge when you DON'T pay in full. Interest is charged
    daily on the outstanding from the transaction date — paying 'minimum due'
    keeps almost the whole balance accruing at ~36-42% p.a.
    """
    daily = (monthly_rate * 12 / 365.0) / 100.0
    interest = outstanding * daily * days
    apr = round(monthly_rate * 12, 1)
    return {"interest": round(interest), "apr_pa": apr}


def min_due_trap(outstanding: float, monthly_rate: float = 3.5,
                 min_pct: float = 5.0, months: int = 12) -> dict:
    """How long a balance lingers if you only ever pay the minimum due."""
    bal = outstanding
    paid = 0.0
    for _ in range(months):
        interest = bal * (monthly_rate / 100.0)
        bal += interest
        pay = max(bal * min_pct / 100.0, min(bal, 200))
        bal -= pay
        paid += pay
        if bal <= 1:
            break
    return {"balance_after": round(max(bal, 0)), "paid_so_far": round(paid)}
