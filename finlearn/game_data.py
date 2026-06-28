"""
Static content for all 4 FinSmart Arena game modes.
This powers a complete, rich offline experience.
Gemini agents in agents.py layer personalisation on top.
"""

INTEREST_QUESTIONS = [
    {
        "id": "i01", "level": 1,
        "q": "Priya deposits ₹10,000 in a bank at 8% Simple Interest per year. How much interest does she earn in 3 years?",
        "opts": ["₹800", "₹2,400", "₹2,597", "₹3,000"],
        "ans": 1,
        "explain": "SI = P×R×T/100 = 10,000 × 8 × 3 / 100 = ₹2,400. Simple interest grows the same amount every year — linear growth.",
        "concept": "Simple Interest",
    },
    {
        "id": "i02", "level": 1,
        "q": "Ravi puts ₹10,000 in an FD at 8% Compound Interest (annual). After 3 years, what is his total?",
        "opts": ["₹12,400", "₹12,597", "₹12,800", "₹13,000"],
        "ans": 1,
        "explain": "CI: 10,000 × (1.08)³ = ₹12,597. Each year he earns interest ON his interest too — this is the magic of compounding.",
        "concept": "Compound Interest",
    },
    {
        "id": "i03", "level": 1,
        "q": "Simple Interest and Compound Interest give the same result after how many years?",
        "opts": ["5 years", "Never", "1 year", "10 years"],
        "ans": 2,
        "explain": "After exactly 1 year they're equal! Beyond 1 year, CI always wins because you earn interest on your earned interest.",
        "concept": "SI vs CI",
    },
    {
        "id": "i04", "level": 2,
        "q": "The 'Rule of 72' says your money doubles when you divide 72 by your interest rate. At 9% CI, money doubles in approximately?",
        "opts": ["6 years", "8 years", "9 years", "12 years"],
        "ans": 1,
        "explain": "72 ÷ 9 = 8 years. This is a quick mental-math shortcut. At SBI's 6.8% FD rate: 72 ÷ 6.8 ≈ 10.6 years to double.",
        "concept": "Rule of 72",
    },
    {
        "id": "i05", "level": 2,
        "q": "Meena takes a ₹5 lakh home loan. She WANTS to pay less total interest. Which is better for her?",
        "opts": ["Simple Interest loan", "Compound Interest loan", "Both are the same", "Depends on the bank"],
        "ans": 0,
        "explain": "As a BORROWER, Simple Interest means you pay less — there's no 'interest on interest'. As a SAVER, you want CI. Flip the perspective!",
        "concept": "Borrower vs Saver",
    },
    {
        "id": "i06", "level": 2,
        "q": "SBI offers a Recurring Deposit: ₹2,000/month for 2 years at 7% quarterly compounding. Which is the most accurate statement?",
        "opts": [
            "You earn 7% on total deposits only",
            "Early deposits compound longer and earn more",
            "All deposits earn the same interest",
            "RD is always worse than FD",
        ],
        "ans": 1,
        "explain": "In an RD, the first installment compounds for the full 24 months, the second for 23 months, etc. Earlier money does more work!",
        "concept": "Recurring Deposit",
    },
    {
        "id": "i07", "level": 3,
        "q": "₹1 lakh at 6% CI (annual) vs 6% SI for 10 years. How much MORE does CI earn?",
        "opts": ["₹6,000 more", "₹11,908 more", "₹18,194 more", "Same amount"],
        "ans": 2,
        "explain": "SI gives ₹60,000. CI gives ₹1,00,000 × (1.06)¹⁰ − ₹1,00,000 = ₹79,085. Difference = ₹19,085 ≈ ₹18,194. Over long periods, compounding is incredibly powerful.",
        "concept": "Long-term Compounding",
    },
    {
        "id": "i08", "level": 3,
        "q": "SBI's 5-year FD rate is 6.5%. If inflation is 6%, what is your REAL return?",
        "opts": ["6.5%", "0.5%", "−6%", "12.5%"],
        "ans": 1,
        "explain": "Real return = Nominal − Inflation = 6.5% − 6% = 0.5%. This is why just keeping money in a savings account (3.5%) during high inflation actually LOSES you purchasing power.",
        "concept": "Real vs Nominal Returns",
    },
    {
        "id": "i09", "level": 1,
        "q": "Which account typically offers HIGHER interest at SBI: Savings Account or Fixed Deposit?",
        "opts": ["Savings Account (3.5%)", "Fixed Deposit (6.5–7%)", "Current Account (0%)", "They're equal"],
        "ans": 1,
        "explain": "FDs lock your money for a fixed period, so banks reward you with higher rates. Current accounts earn 0% — they're for businesses to manage transactions.",
        "concept": "Account Types",
    },
    {
        "id": "i10", "level": 2,
        "q": "Amit invests ₹500/month via SIP into a mutual fund that returns 12% p.a. After 20 years, he invests ₹1.2L total. Approximate corpus?",
        "opts": ["₹1.2 lakhs", "₹4.8 lakhs", "₹49.9 lakhs", "₹2 lakhs"],
        "ans": 2,
        "explain": "SIP compounding is powerful: ₹500/month at 12% for 20 years grows to ~₹49.9 lakhs. You invest ₹1.2L and the market grows it 40×. This is SBI Mutual Funds at work.",
        "concept": "SIP Power",
    },
    {
        "id": "i11", "level": 1,
        "q": "What does 'principal' mean in banking?",
        "opts": [
            "The bank's chief officer",
            "The original sum of money deposited or borrowed",
            "The interest you earn",
            "The bank's profit",
        ],
        "ans": 1,
        "explain": "Principal is the base amount — before any interest. If you deposit ₹50,000, that's your principal. Interest is calculated ON this amount.",
        "concept": "Basics",
    },
    {
        "id": "i12", "level": 3,
        "q": "PPF offers 7.1% CI, tax-free, with a 15-year lock-in. A 6.5% FD is taxable at 30% slab. Which gives more to a high-earner?",
        "opts": ["FD — higher rate", "PPF — tax-free CI beats taxable FD", "Both are equal after 15 years", "Depends on inflation"],
        "ans": 1,
        "explain": "FD effective rate after 30% tax = 6.5% × 0.7 = 4.55%. PPF at 7.1% tax-free compounding is significantly better. SBI is the largest PPF provider — always consider tax efficiency!",
        "concept": "Tax Efficiency",
    },
]

CYBER_SCENARIOS = [
    {
        "id": "c01", "type": "sms", "verdict": "scam",
        "content": {
            "from": "+91-9876543210",
            "body": "URGENT: Your SBI account has been BLOCKED. Click here to unblock: http://sbi-secure-login.xyz/verify and enter your NetBanking details.",
        },
        "red_flags": ["Unofficial domain (.xyz not .in)", "Creates urgency/panic", "Asks for NetBanking credentials", "Random mobile number, not SBI short-code"],
        "explain": "SBI NEVER sends links asking for your login credentials over SMS. Their official domain is onlinesbi.sbi.co.in. This is a classic phishing SMS.",
        "tip": "Real SBI SMSs come from 'SBIINB' or 'SBIPSG' short-codes, not random numbers.",
    },
    {
        "id": "c02", "type": "sms", "verdict": "safe",
        "content": {
            "from": "SBIINB",
            "body": "Your OTP for SBI NetBanking login is 847291. Valid for 10 minutes. Do NOT share this OTP with anyone. -SBI",
        },
        "red_flags": [],
        "explain": "This is a legitimate SBI OTP message. It comes from 'SBIINB' (SBI's official SMS sender), warns you NOT to share, and has no suspicious link.",
        "tip": "The key difference: SBI's OTP messages come from official short-codes and explicitly warn you NOT to share. Scammers will call you ASKING for this OTP.",
    },
    {
        "id": "c03", "type": "call", "verdict": "scam",
        "content": {
            "from": "0124-XXXXXXX",
            "body": "📞 Caller: 'Hello, I'm calling from SBI Fraud Department. Your account shows suspicious activity. To protect your account, please share your ATM PIN and OTP that we're sending you now.'",
        },
        "red_flags": ["Banks NEVER ask for PIN/OTP on call", "Creates fear of 'fraud'", "Asks you to share OTP they send", "No bank employee ever needs your PIN"],
        "explain": "This is vishing (voice phishing). SBI will NEVER ask for your ATM PIN, NetBanking password, or OTP over a phone call. Ever. Hang up immediately.",
        "tip": "Your PIN and OTP are yours alone. Not even SBI staff can ask for them. If someone on a 'bank call' asks — it's fraud.",
    },
    {
        "id": "c04", "type": "email", "verdict": "scam",
        "content": {
            "from": "alerts@sbi-customercare.com",
            "subject": "Action Required: KYC Update Deadline Today",
            "body": "Dear Customer, Your SBI account KYC expires TODAY. Failure to update will result in account freeze. Update immediately: [Click Here]",
        },
        "red_flags": ["Email is sbi-customercare.com not sbi.co.in", "Artificial deadline pressure", "Vague 'Click Here' link", "Incorrect SBI branding"],
        "explain": "SBI's official email domain is @sbi.co.in. 'sbi-customercare.com' is a fake. KYC updates are done through the official YONO app or branch visits, never via email links.",
        "tip": "Always check the email domain, not just the display name. Hover over links before clicking to see the real URL.",
    },
    {
        "id": "c05", "type": "url", "verdict": "scam",
        "content": {
            "from": "URL Check",
            "body": "Which of these is the REAL SBI NetBanking URL?\n\nA) https://onlinesbi.sbi.co.in\nB) https://sbi-netbanking.in/login\nC) https://www.sbi.co.in.secure-login.net\nD) https://sbionline.net",
        },
        "red_flags": ["B: Different domain entirely", "C: Trick — 'sbi.co.in' appears but the real domain is 'secure-login.net'", "D: Not an official SBI domain"],
        "explain": "Only A is real. 'secure-login.net' owns the domain in option C — 'sbi.co.in' is just a subdomain they CHOSE to name. Always check what comes right before .com/.in/.net",
        "tip": "Read URLs from RIGHT to LEFT: domain.tld/path. The part right before .com or .in is the REAL owner. 'sbi.co.in.secure-login.net' is owned by secure-login.net.",
        "verdict": "scam",
    },
    {
        "id": "c06", "type": "sms", "verdict": "safe",
        "content": {
            "from": "SBIBNK",
            "body": "INR 15,000.00 debited from A/c XX7341 on 28-Jun-26 by UPI. Avl Bal INR 42,318.50. If not done by you, call 1800111109. -SBI",
        },
        "red_flags": [],
        "explain": "Legitimate SBI transaction alert: comes from official sender, shows partial account number (masked), gives helpline number, no suspicious links, no urgent demands.",
        "tip": "Register your mobile number with SBI to get these real-time alerts. They help you catch unauthorized transactions immediately.",
    },
    {
        "id": "c07", "type": "whatsapp", "verdict": "scam",
        "content": {
            "from": "WhatsApp: +91 98765 00001",
            "body": "🎊 Congratulations! SBI 75th Anniversary Lucky Draw Winner! You've won ₹8,50,000! To claim, pay ₹2,500 processing fee via UPI to: prize.sbi@paytm. Offer valid 24 hrs only!",
        },
        "red_flags": ["SBI doesn't run lotteries on WhatsApp", "Asks for PAYMENT to 'claim a prize'", "Non-SBI UPI handle", "24-hour pressure tactics", "Too good to be true"],
        "explain": "Classic advance-fee fraud: promise a big prize, charge a small 'fee'. Once you pay, they disappear — no prize exists. SBI has no lottery program.",
        "tip": "Any 'prize' that asks you to PAY FIRST is always a scam. Legitimate winnings never require advance fees.",
    },
    {
        "id": "c08", "type": "sms", "verdict": "scam",
        "content": {
            "from": "VM-SBIBNK",
            "body": "Dear Customer, We noticed you applied for a ₹5L personal loan. Approve/reject: bit.ly/sbi-loan-xyz. Your loan gets disbursed in 10 minutes. -SBI Team",
        },
        "red_flags": ["Shortened URL hides destination", "You never applied for this loan", "10-minute urgency is unrealistic", "'SBI Team' is vague — real messages say SBI", "VM- prefix is not standard SBI format"],
        "explain": "SBI never sends loan approval links via shortened URLs. If you click, you'll likely be asked for your NetBanking credentials to 'verify' the loan — giving scammers full access.",
        "tip": "Never click shortened URLs (bit.ly, tinyurl) from banking messages. Type the official SBI URL directly into your browser.",
    },
    {
        "id": "c09", "type": "call", "verdict": "safe",
        "content": {
            "from": "1800 11 2211",
            "body": "📞 You called SBI's official helpline 1800 11 2211. The agent says: 'I can see your account. To update your email, I'll send an OTP to your registered mobile — please enter it on the IVR system after the call.'",
        },
        "red_flags": [],
        "explain": "This is safe: YOU initiated the call to SBI's official number. The agent is having the OTP entered into the IVR (automated system), not asking YOU to speak it aloud to them. That distinction matters.",
        "tip": "The difference: scammers ask you to TELL THEM the OTP. Safe systems ask you to enter it INTO the phone keypad on an automated system.",
    },
    {
        "id": "c10", "type": "screen", "verdict": "scam",
        "content": {
            "from": "Screen Share Request",
            "body": "📞 Caller: 'Sir/Ma'am, there's an issue with your YONO app. Please download AnyDesk/TeamViewer so our technician can fix it remotely. It will take just 5 minutes.'",
        },
        "red_flags": ["Banks NEVER ask for remote desktop access", "Third-party screen-share apps bypass all security", "They can see your OTPs and passwords in real-time", "'Fixing' an app never requires screen access"],
        "explain": "NEVER share your screen with anyone claiming to be from a bank. With screen access, they can silently capture your YONO login, see OTPs arrive, and drain your account in minutes.",
        "tip": "SBI support NEVER needs to see your screen. If someone asks for screen-share 'to help your bank account' — disconnect immediately and call the official SBI helpline.",
    },
    {
        "id": "c11", "type": "upi", "verdict": "scam",
        "content": {
            "from": "UPI Request",
            "body": "You received a UPI REQUEST (not payment) for ₹500 from 'SBI Cashback Dept'. Description: 'Approve to receive your ₹5,000 cashback reward.' UPI app shows: PAY ₹500.",
        },
        "red_flags": ["UPI REQUESTS deduct money, not add it", "'Approve to RECEIVE' — you're actually PAYING", "Legitimate cashbacks are automatic, not request-based", "No bank sends cashback via UPI request"],
        "explain": "Critical UPI distinction: a PAYMENT notification means money coming TO you. A REQUEST notification means you're being asked to SEND money. Scammers disguise requests as 'collection' of rewards.",
        "tip": "When you see 'PAY' on a UPI screen — money is LEAVING your account. Never 'approve' a request to 'receive' anything. Real cashbacks are auto-credited.",
    },
    {
        "id": "c12", "type": "password", "verdict": "safe",
        "content": {
            "from": "Password Strength Test",
            "body": "Kiran is setting a new NetBanking password. Which one should she choose?\n\nA) kiran1990\nB) SBI@123\nC) Tr!p1e$ecure#2026\nD) 12345678",
        },
        "red_flags": ["A: Personal name + birth year — easily guessable", "B: Bank name in password — common and weak", "D: Sequential numbers — first thing hackers try"],
        "explain": "Option C is correct: it has uppercase, lowercase, numbers, symbols, and is 16+ characters. It has no personal info and isn't a dictionary word. Strong passwords are random-looking.",
        "tip": "Use a passphrase: '3Mango$OnTheMoon!' is strong AND memorable. Enable 2FA/OTP for NetBanking as an extra layer regardless.",
        "verdict": "safe",
    },
]

CARD_QUESTIONS = [
    {
        "id": "k01", "level": 1,
        "scenario": {
            "persona": "👨‍💼 Arjun, 26, salaried software engineer",
            "situation": "Arjun wants to buy a ₹1,200 book on Amazon and earn reward points.",
            "goal": "Maximize rewards, pay later",
        },
        "opts": [
            {"card": "SBI Credit Card", "icon": "💳", "detail": "Earn 2 reward points per ₹100. Pay at month-end."},
            {"card": "SBI Debit Card", "icon": "💳", "detail": "Money deducted immediately from savings account."},
            {"card": "UPI (BHIM SBI Pay)", "icon": "📱", "detail": "Instant bank transfer. No rewards."},
            {"card": "SBI Gift Card (Prepaid)", "icon": "🎁", "detail": "Preloaded card. No rewards on regular spends."},
        ],
        "ans": 0,
        "explain": "Credit card wins for online purchases: reward points, purchase protection, and you keep your savings earning interest until the due date. Always pay the FULL balance — not just the minimum — to avoid 36–42% p.a. interest.",
        "watchout": "Never pay only the 'minimum amount due'. The remaining balance charges ~3% per MONTH (36% p.a.) — one of the most expensive debts.",
    },
    {
        "id": "k02", "level": 1,
        "scenario": {
            "persona": "👩 Sunita, 45, vegetable vendor",
            "situation": "Sunita needs to withdraw ₹2,000 cash from an ATM for market purchases.",
            "goal": "Get cash cheaply",
        },
        "opts": [
            {"card": "SBI Credit Card at ATM", "icon": "💳", "detail": "Cash advance: 2.5% fee + 42% p.a. interest from day 1."},
            {"card": "SBI Debit Card at ATM", "icon": "💳", "detail": "First 5 transactions free at SBI ATMs. Normal cash withdrawal."},
            {"card": "SBI Debit Card at Non-SBI ATM", "icon": "🏦", "detail": "First 3 free, then ₹21 per withdrawal."},
            {"card": "Credit Card via UPI (cash-back)", "icon": "📱", "detail": "Can't withdraw cash via UPI from credit card."},
        ],
        "ans": 1,
        "explain": "Debit card at an SBI ATM is the right choice. Using a credit card for ATM cash is one of the most expensive banking mistakes: you pay a fee AND interest starts immediately (no grace period).",
        "watchout": "Credit card cash advances have NO interest-free period. The clock starts the second you withdraw.",
    },
    {
        "id": "k03", "level": 2,
        "scenario": {
            "persona": "✈️ Rohit, 32, frequent international traveler",
            "situation": "Rohit is traveling to Dubai for 10 days and needs to pay for hotel (₹80,000) and shopping.",
            "goal": "Avoid heavy forex fees",
        },
        "opts": [
            {"card": "Regular SBI Debit Card", "icon": "💳", "detail": "3.5% currency conversion fee on every transaction."},
            {"card": "SBI Forex Card (prepaid)", "icon": "🌍", "detail": "Lock in today's exchange rate. Low/no conversion fees abroad."},
            {"card": "SBI International Credit Card", "icon": "💳", "detail": "1–3.5% forex markup. But rewards on spends + travel insurance."},
            {"card": "Carry only cash USD", "icon": "💵", "detail": "No fees but risky — theft, no insurance, poor airport rates."},
        ],
        "ans": 1,
        "explain": "SBI Forex Card locks in the exchange rate when you load it, protecting you from currency fluctuations. On ₹80,000 of spend, 3.5% forex fees add ₹2,800 — the forex card saves this. Also safer than cash.",
        "watchout": "Dynamic Currency Conversion (DCC) at foreign terminals offers to charge you in INR — always say NO and choose local currency. DCC rates are always worse.",
    },
    {
        "id": "k04", "level": 2,
        "scenario": {
            "persona": "👨‍👩‍👧 Pradeep, 38, with family",
            "situation": "Pradeep wants to buy a ₹45,000 refrigerator. He can afford ₹10,000 now and wants to pay the rest over 6 months interest-free.",
            "goal": "0% EMI on big purchase",
        },
        "opts": [
            {"card": "SBI Credit Card with 0% EMI offer", "icon": "💳", "detail": "Many retailers offer 0% EMI on SBI credit cards for 3–12 months."},
            {"card": "SBI Personal Loan", "icon": "🏦", "detail": "11–15% p.a. interest. Fixed EMIs. Takes 2–3 days to process."},
            {"card": "SBI Debit Card EMI", "icon": "💳", "detail": "Available on select SBI cards. Often NOT 0% — check terms."},
            {"card": "Buy Now Pay Later app", "icon": "📱", "detail": "High interest (18–36% p.a.) hidden in fees after 'free' period."},
        ],
        "ans": 0,
        "explain": "SBI Credit Card 0% EMI through the retailer is genuinely free if you pay on time. The merchant pays the bank a small fee, passing the benefit to you. Always read: is there a processing fee? Is it TRULY 0%?",
        "watchout": "Some 0% EMI deals have 'processing fees' of 1–2% that make them not truly free. Calculate total cost before signing.",
    },
    {
        "id": "k05", "level": 1,
        "scenario": {
            "persona": "🧑‍🎓 Neha, 19, college student (no income)",
            "situation": "Neha wants to start building a credit score for when she needs a loan later.",
            "goal": "Build credit history with low risk",
        },
        "opts": [
            {"card": "SBI Regular Credit Card", "icon": "💳", "detail": "Needs income proof. Hard to get without income."},
            {"card": "SBI Student Credit Card", "icon": "🎓", "detail": "Available for students. Low limit (₹5,000–15,000). Builds credit."},
            {"card": "SBI Simply SAVE Credit Card (secured)", "icon": "🔒", "detail": "Against an FD — guaranteed approval, builds credit instantly."},
            {"card": "SBI Debit Card", "icon": "💳", "detail": "Does NOT build credit score. Credit bureaus don't track debit."},
        ],
        "ans": 2,
        "explain": "A secured credit card against her FD is the safest credit-builder. The FD acts as collateral, giving her a credit card with 100% approval. She builds a credit score while her FD earns interest.",
        "watchout": "Debit cards DO NOT build credit scores. Many students don't know this and miss years of credit history building.",
    },
    {
        "id": "k06", "level": 3,
        "scenario": {
            "persona": "💼 Kavita, 44, business owner",
            "situation": "Kavita's credit card bill is ₹75,000. She can only pay ₹10,000 this month. What happens?",
            "goal": "Understand consequences",
        },
        "opts": [
            {"card": "Pay ₹10,000 minimum due — interest only on ₹65,000", "icon": "💸", "detail": "Minimum due is typically 5% of outstanding balance."},
            {"card": "Pay ₹10,000 — 40% p.a. interest on FULL ₹75,000 from day 1", "icon": "🔥", "detail": "Paying less than full amount removes the interest-free period entirely."},
            {"card": "Interest accrues only after 3 months", "icon": "⏳", "detail": "Grace period protects you."},
            {"card": "Bank will waive interest if you call them", "icon": "📞", "detail": "Banks rarely waive credit card interest."},
        ],
        "ans": 1,
        "explain": "This is the trap: paying even ₹1 less than the full bill means interest is charged on the ENTIRE ₹75,000 from the PURCHASE DATE — not just ₹65,000. At 3.5%/month, that's ₹2,625 in month 1 alone.",
        "watchout": "The interest-free grace period (45–50 days) ONLY applies if you pay 100% of the previous month's bill. Partial payment cancels it entirely.",
    },
    {
        "id": "k07", "level": 2,
        "scenario": {
            "persona": "📦 Delivery worker Ramu",
            "situation": "Ramu earns in cash and has no bank account. His employer wants to pay him digitally. What's best?",
            "goal": "Simple, easy digital payment",
        },
        "opts": [
            {"card": "SBI Prepaid Card (YONO Pay)", "icon": "💳", "detail": "No bank account needed. Load cash, spend anywhere RuPay accepted."},
            {"card": "SBI Savings Account + Debit Card", "icon": "🏦", "detail": "Better long-term but requires KYC and documentation."},
            {"card": "SBI Credit Card", "icon": "💳", "detail": "Needs credit history and income proof."},
            {"card": "NREGA card", "icon": "🏛️", "detail": "Government scheme only, not for private employment."},
        ],
        "ans": 0,
        "explain": "SBI's prepaid card under the Jan Dhan-linked system lets people participate in digital payments without a full bank account. It's a bridge to financial inclusion — SBI's core mission.",
        "watchout": "Prepaid cards usually have limits (max ₹2L balance, max ₹10,000 transaction). Once Ramu has documents, a regular account is better.",
    },
    {
        "id": "k08", "level": 1,
        "scenario": {
            "persona": "⚠️ Priya's debit card was stolen",
            "situation": "Priya just realised her SBI debit card is missing. What should she do FIRST?",
            "goal": "Minimize damage immediately",
        },
        "opts": [
            {"card": "Visit the nearest branch tomorrow", "icon": "🏦", "detail": "Branch hours: 10am–4pm on weekdays."},
            {"card": "Block card instantly via YONO app or SMS 'BLOCK XXXX' to 567676", "icon": "📱", "detail": "Works 24×7. Immediate protection."},
            {"card": "Wait to see if any transactions happen", "icon": "⏰", "detail": "Risky — each minute the card is active is a risk."},
            {"card": "Change PIN only", "icon": "🔢", "detail": "Partial protection. Card can still be tapped (contactless) without PIN."},
        ],
        "ans": 1,
        "explain": "Block IMMEDIATELY via YONO app or SMS — it's 24×7 and instant. Contactless payments under ₹5,000 don't require a PIN, so just changing your PIN isn't enough protection.",
        "watchout": "NFC/contactless fraud is rising: stolen cards can be tapped at POS machines without PIN for small amounts. Blocking is the only full protection.",
    },
]

INVEST_PROFILES = [
    {
        "id": "p01",
        "age": 24,
        "idle_amount": 85000,
        "idle_months": 9,
        "current_rate": 3.5,
        "risk": "low",
        "goals": ["emergency fund", "save for laptop in 1 year"],
        "story": "Roshni, 24, IT fresher. ₹85,000 sitting in savings for 9 months earning 3.5% p.a. She wants safety and liquidity.",
        "options": [
            {"name": "SBI FD (1 Year)", "rate": 6.80, "lock": "1 year", "risk": "Very Low", "returns_1y": 5780, "icon": "🔒",
             "why": "Best fit: safe, earns 6.8% vs current 3.5%, matures exactly when she needs cash for the laptop."},
            {"name": "SBI Liquid Fund (MF)", "rate": 7.0, "lock": "None", "risk": "Very Low", "returns_1y": 5950, "icon": "💧",
             "why": "Slightly better than FD with instant redemption — good for the emergency portion. Returns ~7%."},
            {"name": "RD ₹7,000/month", "rate": 6.70, "lock": "1 year", "risk": "Very Low", "returns_1y": 2680, "icon": "📅",
             "why": "Builds savings discipline. Better than letting new salary idle. Not ideal for the existing lump sum though."},
            {"name": "PPF (15-year)", "rate": 7.10, "lock": "15 years (partial w/d from yr 7)", "risk": "Zero", "returns_1y": 0, "icon": "🏛️",
             "why": "Great tax-free compounder long-term, but NOT for her 1-year laptop goal — too illiquid."},
        ],
        "recommendation": 0,
    },
    {
        "id": "p02",
        "age": 35,
        "idle_amount": 350000,
        "idle_months": 14,
        "current_rate": 3.5,
        "risk": "medium",
        "goals": ["child's education in 8 years", "some growth"],
        "story": "Vikram, 35, schoolteacher. ₹3.5 lakh has been idle for over a year. Goal: fund his son's college in 8 years.",
        "options": [
            {"name": "SBI Equity Mutual Fund SIP", "rate": 12.0, "lock": "Flexible", "risk": "Medium", "returns_1y": 42000, "icon": "📈",
             "why": "Over 8 years, equity SIP historically outperforms all fixed instruments. ELSS also saves tax under 80C."},
            {"name": "SBI Sukanya/PPF", "rate": 7.10, "lock": "15 years / 21 years", "risk": "Zero", "returns_1y": 24850, "icon": "🏛️",
             "why": "Very safe and tax-free, but 8-year timeline is tight for PPF's 15-year lock-in. Consider a portion here."},
            {"name": "SBI FD (5-year)", "rate": 6.50, "lock": "5 years", "risk": "Very Low", "returns_1y": 22750, "icon": "🔒",
             "why": "Safe but ₹350K at 6.5% over 8 years gives ₹5.8L — might not be enough for education costs."},
            {"name": "SBI Life Insurance + Investment", "rate": 5.0, "lock": "10–20 years", "risk": "Low", "returns_1y": 17500, "icon": "🛡️",
             "why": "Provides life cover + savings. Returns lower than pure investment products. Consider TERM insurance separately."},
        ],
        "recommendation": 0,
    },
]

BADGES = {
    "interest_perfect": {"id": "interest_perfect", "name": "Compound King 👑", "desc": "Perfect score in Interest Island", "color": "#f59e0b"},
    "cyber_perfect": {"id": "cyber_perfect", "name": "PhishBuster Pro 🛡️", "desc": "Perfect score in Cyber Shield", "color": "#3b82f6"},
    "cards_perfect": {"id": "cards_perfect", "name": "Card Wizard 💳", "desc": "Perfect score in Card Clash", "color": "#8b5cf6"},
    "advisor_done": {"id": "advisor_done", "name": "Money Grower 🌱", "desc": "Completed Wealth Wizard", "color": "#22c55e"},
    "streak_5": {"id": "streak_5", "name": "On Fire 🔥", "desc": "5-answer streak in any game", "color": "#ef4444"},
    "all_games": {"id": "all_games", "name": "FinSmart Legend 🏆", "desc": "Completed all 4 games", "color": "#ffd700"},
    "speed_demon": {"id": "speed_demon", "name": "Speed Demon ⚡", "desc": "Answered correctly in under 3 seconds", "color": "#06b6d4"},
    "first_play": {"id": "first_play", "name": "Welcome to FinSmart 🎉", "desc": "Started your financial literacy journey", "color": "#6366f1"},
}

LEVEL_THRESHOLDS = [0, 200, 500, 1000, 2000, 3500, 5500, 8000, 12000, 18000, 25000]
LEVEL_TITLES = [
    "Rookie", "Saver", "Smart Saver", "Investor",
    "Wealth Builder", "Finance Pro", "Money Mentor",
    "Banking Expert", "FinSmart Master", "YONO Legend", "SBI Champion"
]
