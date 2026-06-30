"""
question_engine.py — the AGENTIC, offline question generator.

Each call produces a FRESH question by randomising inputs and COMPUTING the
correct answer with finance_math. Distractors are built from the actual mistakes
learners make (simple-vs-compound, flat-vs-reducing, ignoring inflation), so a
wrong pick is a teachable moment, not a random foil. Because answers are computed,
the bank never "runs out" and never serves a wrong key — this is what lets the
game give endless fresh practice without an LLM, and stay correct when an LLM is
added on top.
"""

import random

import finance_math as fm

INR = lambda x: "₹" + format(int(round(x)), ",d")


def _mcq(stem, correct, distractors, explanation, concept, module,
         difficulty=1, fmt=INR, computed=True):
    """Assemble a 4-option MCQ; shuffle; return the correct index."""
    opts = [correct] + distractors
    # de-duplicate while keeping the correct value present
    seen, uniq = set(), []
    for o in opts:
        key = round(o, 2) if isinstance(o, (int, float)) else o
        if key in seen:
            continue
        seen.add(key); uniq.append(o)
    while len(uniq) < 4:                       # pad if distractors collided
        jitter = correct * random.uniform(0.6, 1.4) if isinstance(correct, (int, float)) else correct
        k = round(jitter, 2) if isinstance(jitter, (int, float)) else jitter
        if k not in seen:
            seen.add(k); uniq.append(jitter)
    uniq = uniq[:4]
    random.shuffle(uniq)
    rendered = [fmt(o) if (fmt and isinstance(o, (int, float))) else str(o) for o in uniq]
    answer = uniq.index(correct)
    return {"concept": concept, "module": module, "difficulty": difficulty,
            "stem": stem, "options": rendered, "answer": answer,
            "explanation": explanation, "computed": computed}


# ---------------------------------------------------------------------------
# Numeric generators (computed; infinite variety)
# ---------------------------------------------------------------------------

def gen_simple_interest():
    p = random.choice([10000, 20000, 25000, 50000, 75000])
    r = random.choice([6, 7, 8, 9, 10]); t = random.choice([2, 3, 4, 5])
    si = fm.simple_interest(p, r, t)["interest"]
    ci = fm.compound_interest(p, r, t, 1)["interest"]
    return _mcq(
        f"You deposit {INR(p)} at {r}% per year SIMPLE interest for {t} years. "
        f"How much INTEREST do you earn?",
        si, [ci, round(si * 1.2), round(si / t)],
        f"Simple interest = P×r×t = {INR(p)}×{r}%×{t} = {INR(si)}. "
        f"It's a flat amount each year — the interest never earns its own interest.",
        "simple_interest", "money_basics", 1)


def gen_si_vs_ci():
    p = random.choice([50000, 100000, 200000]); r = random.choice([7, 8, 9, 10]); t = random.choice([5, 10])
    si = fm.simple_interest(p, r, t)["maturity"]
    ci = fm.compound_interest(p, r, t, 1)["maturity"]
    return _mcq(
        f"{INR(p)} grows for {t} years at {r}%. What does COMPOUND interest give you "
        f"at maturity (compounded yearly)?",
        ci, [si, round((si + ci) / 2), round(ci * 1.15)],
        f"Compound: A = P(1+r)^t = {INR(ci)}. Simple interest would give only {INR(si)} — "
        f"the gap ({INR(ci - si)}) is interest earning interest. Time is the magic ingredient.",
        "compound_interest", "money_basics", 2)


def gen_rule_72():
    r = random.choice([6, 8, 9, 12]); yrs = fm.rule_of_72(r)
    return _mcq(
        f"At {r}% per year (compounded), roughly how long until your money DOUBLES?",
        f"{yrs} years",
        [f"{round(yrs/2,1)} years", f"{round(yrs*1.5,1)} years", f"{round(100/r,1)} years"],
        f"Rule of 72: 72 ÷ {r} ≈ {yrs} years. A quick mental shortcut for doubling time.",
        "rule_of_72", "money_basics", 1, fmt=None)


def gen_fd():
    p = random.choice([100000, 200000, 500000]); r = random.choice([6.5, 6.8, 7.0, 7.25]); t = random.choice([3, 5])
    mat = fm.fd_maturity(p, r, t)["maturity"]
    si = fm.simple_interest(p, r, t)["maturity"]
    return _mcq(
        f"An SBI Fixed Deposit of {INR(p)} at {r}% for {t} years (compounded quarterly) "
        f"matures to approximately…?",
        mat, [si, round(p + (mat - p) * 0.7), round(mat * 1.1)],
        f"FDs compound quarterly: ≈{INR(mat)}. Quarterly compounding beats a simple-interest "
        f"estimate of {INR(si)}.",
        "fd", "accounts", 2)


def gen_rd():
    m = random.choice([1000, 2000, 3000, 5000]); r = random.choice([6.5, 6.8, 7.0]); months = random.choice([12, 24, 36])
    res = fm.rd_maturity(m, r, months)
    return _mcq(
        f"You save {INR(m)} every month in a Recurring Deposit at {r}% for {months} months. "
        f"Maturity value?",
        res["maturity"], [res["invested"], round(res["maturity"] * 1.08), round(res["invested"] * 1.15)],
        f"RD maturity ≈ {INR(res['maturity'])}. You invested {INR(res['invested'])} and earned "
        f"{INR(res['interest'])} — each instalment compounds for the months it stays in.",
        "rd", "accounts", 2)


def gen_ppf():
    a = random.choice([50000, 100000, 150000])
    res = fm.ppf_maturity(a)
    return _mcq(
        f"You invest {INR(a)} every year in PPF (7.1%, tax-free) for the full 15 years. "
        f"Approx maturity?",
        res["maturity"], [res["invested"], round(res["maturity"] * 0.6), round(res["maturity"] * 1.25)],
        f"PPF compounds annually, tax-free: ≈{INR(res['maturity'])} on {INR(res['invested'])} invested. "
        f"The long 15-year lock-in is what makes the compounding powerful.",
        "ppf", "govt_schemes", 3)


def gen_emi():
    p = random.choice([300000, 500000, 1000000, 2500000]); r = random.choice([8.5, 9, 9.5, 10]); months = random.choice([60, 120, 180, 240])
    res = fm.emi_reducing(p, r, months)
    return _mcq(
        f"A home loan of {INR(p)} at {r}% for {months // 12} years (reducing balance). "
        f"What is the monthly EMI?",
        res["emi"], [round(p / months), round(res["emi"] * 1.2), round(res["emi"] * 0.8)],
        f"EMI ≈ {INR(res['emi'])}. Over the full term you repay {INR(res['total_paid'])} — "
        f"of which {INR(res['total_interest'])} is interest. Longer tenure = lower EMI but far more interest.",
        "emi", "loans", 2)


def gen_flat_vs_reducing():
    p = random.choice([200000, 300000, 500000]); flat = random.choice([8, 9, 10]); months = random.choice([24, 36, 48])
    res = fm.flat_vs_reducing(p, flat, months)
    return _mcq(
        f"A lender offers a '{flat}% flat rate' loan of {INR(p)} for {months} months. "
        f"What is the TRUE (reducing-balance) interest rate you're actually paying?",
        f"{res['effective_reducing_rate']}%",
        [f"{flat}%", f"{round(flat*1.3,1)}%", f"{round(flat+2,1)}%"],
        f"A '{flat}% flat' loan really costs about {res['effective_reducing_rate']}% in reducing terms — "
        f"because flat rate charges interest on the FULL amount even as you repay it. Always ask for the reducing rate.",
        "flat_vs_reducing", "loans", 3, fmt=None)


def gen_inflation():
    a = random.choice([100000, 500000, 1000000]); inf = random.choice([5, 6, 7]); t = random.choice([10, 15, 20])
    val = fm.inflation_adjusted(a, inf, t)
    return _mcq(
        f"{INR(a)} today, at {inf}% inflation, will have the PURCHASING POWER of how much "
        f"in {t} years?",
        val, [a, round(a * (1 - inf * t / 100)), round(val * 0.5)],
        f"Inflation erodes value: {INR(a)} ≈ {INR(val)} of today's purchasing power after {t} years. "
        f"This is why money left idle in a low-interest account quietly loses value.",
        "inflation", "money_basics", 2)


def gen_real_return():
    nom = random.choice([6, 7, 8]); inf = random.choice([5, 6, 7])
    rr = fm.real_return(nom, inf)
    return _mcq(
        f"Your savings earn {nom}% but inflation is {inf}%. What is your REAL return "
        f"(what your money actually gains in buying power)?",
        f"{rr}%", [f"{nom-inf}%", f"{nom}%", f"{round(rr+1.5,2)}%"],
        f"Real return = ((1+{nom}%)/(1+{inf}%) − 1) ≈ {rr}%. A nominal {nom}% can be almost nothing "
        f"after inflation — the number that matters is the real return.",
        "real_return", "money_basics", 3, fmt=None)


def gen_credit_card():
    bal = random.choice([20000, 40000, 60000, 100000]); mr = random.choice([3.0, 3.5, 3.75])
    res = fm.credit_card_interest(bal, mr)
    return _mcq(
        f"You carry {INR(bal)} on your credit card at {mr}% per month. What's the APPROX "
        f"annual interest rate (APR) — and why it hurts?",
        f"{res['apr_pa']}% APR",
        [f"{mr}% APR", f"{round(mr*6,1)}% APR", "0% — it's interest-free"],
        f"{mr}%/month ≈ {res['apr_pa']}% per year. Paying only the 'minimum due' keeps almost the "
        f"whole balance compounding at this rate — credit-card debt is among the most expensive money you can borrow.",
        "credit_card_interest", "cards", 2, fmt=None)


# ---------------------------------------------------------------------------
# Conceptual generators (drawn from a curated concept bank; still rotated)
# ---------------------------------------------------------------------------

_CONCEPT_BANK = {
    "casa": [{
        "stem": "What does CASA mean, and why do banks love a high CASA ratio?",
        "options": ["Current Account + Savings Account — they're low-cost deposits for the bank",
                    "Credit And Securities Account — a type of demat account",
                    "Cash And Salary Account — only for salaried people",
                    "Central Account Settlement Authority — an RBI body"],
        "answer": 0,
        "explanation": "CASA = Current + Savings balances. Banks pay little/no interest on them, "
                       "so a high CASA ratio means cheap funds and better margins."},
        {"stem": "Which account is meant for businesses with very high transaction volume "
                 "and pays NO interest?",
         "options": ["Current account", "Savings account", "Fixed deposit", "PPF account"],
         "answer": 0,
         "explanation": "Current accounts are for businesses — unlimited transactions, no interest. "
                        "Savings accounts pay interest but limit some transactions."}],
    "deposit_insurance": [{
        "stem": "If your bank fails, how much of YOUR deposit is guaranteed by DICGC "
                "(an RBI subsidiary)?",
        "options": ["₹5,00,000 per depositor per bank", "₹1,00,000 only", "The full amount, always",
                    "Nothing — deposits aren't insured"],
        "answer": 0,
        "explanation": "DICGC insures up to ₹5 lakh per depositor per bank (raised from ₹1 lakh in 2020), "
                       "covering principal + interest. Spreading large savings across banks increases coverage."}],
    "neft_imps_rtgs": [{
        "stem": "You need to send ₹3,000 to a friend INSTANTLY at 11 PM on a Sunday. Best rail?",
        "options": ["IMPS / UPI — instant, 24×7", "RTGS — but only for ₹2 lakh and above",
                    "NEFT — settles in half-hourly batches", "Cheque — clears in 2 days"],
        "answer": 0,
        "explanation": "IMPS and UPI are instant and run 24×7. RTGS is for ₹2 lakh+ (real-time but "
                       "bank hours historically); NEFT settles in batches."}],
    "netbanking_safety": [{
        "stem": "An SMS says 'Your SBI account is blocked, click this link to update KYC.' "
                "What's the SAFE action?",
        "options": ["Don't click — banks never ask for KYC via SMS links; open the app yourself",
                    "Click and enter your details quickly before it expires",
                    "Reply with your account number to verify",
                    "Call the number in the SMS and share the OTP"],
        "answer": 0,
        "explanation": "This is phishing. Banks never send KYC/login links by SMS or ask for OTP/PIN. "
                       "Always reach the bank through the official app or printed card number."}],
    "credit_score": [{
        "stem": "Which habit most improves your CIBIL credit score over time?",
        "options": ["Paying every EMI and card bill in full, on time",
                    "Never taking any loan or card at all",
                    "Using 95% of your credit limit every month",
                    "Applying for many loans quickly to build history"],
        "answer": 0,
        "explanation": "On-time payment and low credit utilisation (<30%) build a strong score. "
                       "Maxing out limits or many fresh applications hurt it; zero credit means no history."}],
    "govt_schemes": [{
        "stem": "Which government scheme gives a girl child a high-interest, tax-free savings account?",
        "options": ["Sukanya Samriddhi Yojana", "Atal Pension Yojana",
                    "PM Jan Dhan Yojana", "PMSBY (accident insurance)"],
        "answer": 0,
        "explanation": "Sukanya Samriddhi Yojana is for a girl child — among the highest-interest, "
                       "tax-free small-savings schemes. APY is pension; PMJDY is basic banking; PMSBY is insurance."},
        {"stem": "PMJJBY offers ₹2 lakh life cover for about ₹436/year. Who is it best for?",
         "options": ["Anyone 18–50 wanting cheap term life cover via their bank account",
                     "Only government employees", "Only people above 60",
                     "Only those with a demat account"],
         "answer": 0,
         "explanation": "Pradhan Mantri Jeevan Jyoti Bima Yojana gives ₹2 lakh life cover for a tiny "
                        "annual premium, auto-debited from your bank account — broad, cheap protection."}],
    "debit_vs_credit": [{
        "stem": "What's the core difference between a debit card and a credit card?",
        "options": ["Debit spends YOUR money instantly; credit borrows the BANK's money to repay later",
                    "They're the same, just different colours",
                    "Debit cards charge interest; credit cards never do",
                    "Credit cards can't be used online"],
        "answer": 0,
        "explanation": "Debit pulls from your own balance immediately. Credit is a short-term loan — "
                       "free if you pay in full by the due date, expensive (~36-42% APR) if you don't."}],
}


def gen_concept(concept):
    item = random.choice(_CONCEPT_BANK[concept])
    opts = item["options"][:]
    correct = opts[item["answer"]]
    random.shuffle(opts)
    return {"concept": concept, "module": _CONCEPT_MODULE.get(concept, "money_basics"),
            "difficulty": 1, "stem": item["stem"], "options": opts,
            "answer": opts.index(correct), "explanation": item["explanation"],
            "computed": False}


_CONCEPT_MODULE = {
    "casa": "accounts", "deposit_insurance": "accounts", "neft_imps_rtgs": "payments",
    "netbanking_safety": "payments", "credit_score": "loans", "govt_schemes": "govt_schemes",
    "debit_vs_credit": "cards",
}

# ---------------------------------------------------------------------------
# Registry + dispatch
# ---------------------------------------------------------------------------
_NUMERIC = {
    "simple_interest": gen_simple_interest, "compound_interest": gen_si_vs_ci,
    "rule_of_72": gen_rule_72, "fd": gen_fd, "rd": gen_rd, "ppf": gen_ppf,
    "emi": gen_emi, "flat_vs_reducing": gen_flat_vs_reducing,
    "inflation": gen_inflation, "real_return": gen_real_return,
    "credit_card_interest": gen_credit_card,
}
_CONCEPTUAL = list(_CONCEPT_BANK.keys())

ALL_CONCEPTS = list(_NUMERIC.keys()) + _CONCEPTUAL


def generate(concept: str = None, difficulty: int = None) -> dict:
    """Generate one fresh question. If concept is None, pick one at random."""
    if concept is None:
        concept = random.choice(ALL_CONCEPTS)
    if concept in _NUMERIC:
        q = _NUMERIC[concept]()
    elif concept in _CONCEPT_BANK:
        q = gen_concept(concept)
    else:
        q = _NUMERIC[random.choice(list(_NUMERIC))]()
    q["id"] = f"{q['concept']}-{random.randint(100000, 999999)}"
    return q


def generate_set(n: int = 5, module: str = None, difficulty: int = None) -> list:
    """Generate a fresh quiz set, optionally scoped to a module."""
    concepts = ALL_CONCEPTS
    if module:
        concepts = [c for c in ALL_CONCEPTS
                    if (_CONCEPT_MODULE.get(c) or _module_of_numeric(c)) == module]
    if not concepts:
        concepts = ALL_CONCEPTS
    out = []
    for _ in range(n):
        out.append(generate(random.choice(concepts), difficulty))
    return out


def _module_of_numeric(concept):
    sample = _NUMERIC.get(concept)
    if not sample:
        return None
    return sample().get("module")
