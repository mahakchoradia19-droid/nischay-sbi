"""
curriculum.py — the teaching content behind FinSmart Academy.

Six modules, plain-language and India-specific, each lesson carrying:
  - a short summary and key points (what to learn),
  - a worked_example COMPUTED live by finance_math (correct by construction),
  - a `tutor` script written to be spoken aloud by the voice agent — warm,
    unhurried, reassuring ("airhostess" cadence) — with a Hindi script for the
    flagship lessons so vernacular voice teaching works fully offline.
  - the `concepts` each lesson unlocks for the adaptive quiz.

Genuine value for every calibre: a first-timer learns what an FD is; an
advanced learner sees why a 'flat' loan rate is a trap and what real return means.
"""

import finance_math as fm

INR = lambda x: "₹" + format(int(round(x)), ",d")

MODULES = [
    {"id": "money_basics", "title": "Money & Growth", "icon": "🌱",
     "blurb": "Interest, compounding, time value, inflation — the engine of all money."},
    {"id": "accounts", "title": "Where Your Money Lives", "icon": "🏦",
     "blurb": "Savings vs current (CASA), FD, RD, PPF — and how your deposits are protected."},
    {"id": "cards", "title": "Cards Without Fear", "icon": "💳",
     "blurb": "Debit vs credit, billing cycles, the minimum-due trap, and staying safe."},
    {"id": "payments", "title": "Banking On Your Phone", "icon": "📱",
     "blurb": "Net banking, UPI, NEFT/IMPS/RTGS, OTP discipline, and spotting fraud."},
    {"id": "loans", "title": "Borrowing Smart", "icon": "🏠",
     "blurb": "EMIs, flat vs reducing rates, tenure, prepayment, and your credit score."},
    {"id": "govt_schemes", "title": "Schemes That Have Your Back", "icon": "🇮🇳",
     "blurb": "Jan Dhan, Sukanya, PPF, NPS, Atal Pension, Jan Suraksha insurance."},
]


def _wex(text):
    return text


LESSONS = [
    # ── Money basics ───────────────────────────────────────────────────
    {"id": "what_is_interest", "module": "money_basics", "title": "What interest really is",
     "icon": "💡", "minutes": 3,
     "summary": "Interest is the rent paid for using money. When you save, the bank rents your "
                "money and pays you. When you borrow, you rent the bank's money and pay it.",
     "key_points": [
         "Principal = the original amount. Interest = the extra you earn or pay on it.",
         "Simple interest is paid only on the principal — a flat amount each year.",
         "Compound interest is paid on principal AND past interest — it snowballs."],
     "worked_example": _wex(
         f"Save {INR(10000)} at 8% for 3 years. Simple interest earns "
         f"{INR(fm.simple_interest(10000,8,3)['interest'])}. Compound (yearly) earns "
         f"{INR(fm.compound_interest(10000,8,3,1)['interest'])} — more, because the interest itself earns interest."),
     "concepts": ["simple_interest"],
     "tutor": ("Let's begin with the simplest idea in all of money: interest. Think of money like a "
               "field you can rent out. When you keep money in the bank, you are renting it to the "
               "bank, and the rent they pay you is called interest. The amount you started with has a "
               "name — the principal. Now here is the beautiful part. If the bank pays interest only on "
               "your original amount, that is simple interest. But if it also pays interest on the "
               "interest you already earned, that is compound interest, and over time it grows much, "
               "much faster. Don't worry — we'll see it with real numbers, step by step."),
     "tutor_hi": ("चलिए पैसे की सबसे आसान बात से शुरू करते हैं — ब्याज। पैसे को एक खेत की तरह सोचिए जिसे आप "
                  "किराए पर दे सकते हैं। जब आप बैंक में पैसा रखते हैं, तो आप बैंक को किराए पर दे रहे होते हैं, और "
                  "बदले में जो किराया मिलता है उसे ब्याज कहते हैं। जिस रकम से आपने शुरुआत की उसे मूलधन कहते हैं। "
                  "अगर बैंक सिर्फ़ आपकी मूल रकम पर ब्याज दे, तो वह साधारण ब्याज है। लेकिन अगर वह आपके कमाए हुए "
                  "ब्याज पर भी ब्याज दे, तो वह चक्रवृद्धि ब्याज है — और समय के साथ यह बहुत तेज़ी से बढ़ता है।")},

    {"id": "compounding_magic", "module": "money_basics", "title": "The magic of compounding",
     "icon": "📈", "minutes": 4,
     "summary": "Compounding is interest earning interest. The two ingredients are RATE and TIME — "
                "and time matters even more than the amount.",
     "key_points": [
         "A = P(1 + r)^t. Each year's interest joins the principal and earns again.",
         "Rule of 72: divide 72 by the rate to estimate years to double your money.",
         "Starting early beats starting big — a few extra years dramatically changes the result."],
     "worked_example": _wex(
         f"{INR(100000)} at 8% compounded yearly: doubles in about {fm.rule_of_72(8)} years "
         f"(Rule of 72), reaching {INR(fm.compound_interest(100000,8,9,1)['maturity'])} in 9 years."),
     "concepts": ["compound_interest", "rule_of_72"],
     "tutor": ("Now meet the most powerful force in your financial life: compounding. Imagine a single "
               "drop of water that doubles every day. For a long time it looks like nothing — and then "
               "suddenly it fills the whole lake. Money does the same when interest earns its own "
               "interest. Here's a friendly shortcut called the Rule of 72: take the number seventy-two "
               "and divide it by your interest rate, and that's roughly how many years it takes your "
               "money to double. At eight percent, that's about nine years. The earlier you start, the "
               "more time compounding has to work its quiet magic for you."),
     "tutor_hi": ("अब मिलिए आपके पैसों की सबसे बड़ी ताक़त से — चक्रवृद्धि। सोचिए पानी की एक बूँद जो हर दिन दोगुनी "
                  "होती है। काफ़ी समय तक कुछ नहीं दिखता, और फिर अचानक पूरा तालाब भर जाता है। पैसा भी ऐसे ही बढ़ता "
                  "है जब ब्याज अपने ब्याज पर भी ब्याज कमाता है। एक आसान नियम है — बहत्तर का नियम। बहत्तर को अपनी "
                  "ब्याज दर से भाग दीजिए, उतने साल में आपका पैसा दोगुना हो जाता है। जितनी जल्दी शुरुआत, उतना बड़ा फ़ायदा।")},

    {"id": "inflation_tvm", "module": "money_basics", "title": "Inflation & the value of time",
     "icon": "⏳", "minutes": 4,
     "summary": "₹100 today is not ₹100 in ten years. Inflation slowly shrinks what your money can "
                "buy. The return that matters is the REAL return — after inflation.",
     "key_points": [
         "Money sitting idle at 3.5% while inflation is 6% is actually LOSING value.",
         f"Real return ≈ ((1+nominal)/(1+inflation) − 1). At 8% with 6% inflation, only ~{fm.real_return(8,6)}%.",
         "This is why simply 'saving' isn't enough — your money must out-run inflation."],
     "worked_example": _wex(
         f"{INR(100000)} today, at 6% inflation, has the buying power of only "
         f"{INR(fm.inflation_adjusted(100000,6,10))} in 10 years."),
     "concepts": ["inflation", "real_return"],
     "tutor": ("Here's a gentle truth that protects you for life: the same hundred rupees buys a little "
               "less every year. That slow shrinking is called inflation. So when your money sleeps in "
               "an account earning very little, inflation is quietly nibbling it away. The number to "
               "watch is not the interest rate on the poster — it's the real return, which is what's "
               "left after inflation. Your goal is simple: keep your money working hard enough to stay "
               "ahead of rising prices. I'll always help you find the option that does that."),
     "tutor_hi": ("एक सच्चाई जो आपको ज़िंदगी भर बचाएगी — वही सौ रुपये हर साल थोड़ा कम सामान खरीदते हैं। इस धीमी "
                  "गिरावट को महँगाई कहते हैं। जब आपका पैसा कम ब्याज वाले खाते में सोता है, तो महँगाई उसे चुपचाप कम "
                  "करती रहती है। असली बात ब्याज दर नहीं, बल्कि असली रिटर्न है — यानी महँगाई के बाद जो बचे। लक्ष्य "
                  "सरल है: पैसे को इतना मेहनती बनाइए कि वह बढ़ती कीमतों से आगे रहे।")},

    # ── Accounts ───────────────────────────────────────────────────────
    {"id": "casa", "module": "accounts", "title": "Savings vs Current: CASA explained",
     "icon": "🏦", "minutes": 3,
     "summary": "CASA = Current Account + Savings Account. Savings pays you some interest with light "
                "limits; current is for businesses with heavy transactions and pays no interest.",
     "key_points": [
         "Savings account: earns interest (~2.7-3.5%), for individuals, some transaction limits.",
         "Current account: no interest, unlimited transactions, for businesses.",
         "Banks love CASA because it's low-cost money for them."],
     "worked_example": "₹1,00,000 in savings at 3.5% earns ₹3,500/year; in a current account it earns ₹0.",
     "concepts": ["casa"],
     "tutor": ("Two everyday accounts, two different jobs. A savings account is your personal home for "
               "money — it pays you a little interest and is perfect for daily life. A current account "
               "is built for businesses that make many transactions every day; it pays no interest but "
               "allows unlimited activity. Together, bankers call these CASA. You'll almost always want "
               "a savings account; a current account is for when you run a business.")},

    {"id": "fd_rd", "module": "accounts", "title": "Fixed & Recurring Deposits",
     "icon": "🔒", "minutes": 4,
     "summary": "An FD locks a lump sum for a fixed term at a guaranteed rate. An RD lets you deposit "
                "a fixed amount every month. Both are safe and compound your money.",
     "key_points": [
         "FD: one lump sum, fixed tenure, higher rate than savings, penalty for early break.",
         "RD: save monthly — perfect for building a habit with small amounts.",
         "Banks compound FDs quarterly, so maturity beats a simple-interest guess."],
     "worked_example": _wex(
         f"{INR(100000)} FD at 6.8% for 5 years → {INR(fm.fd_maturity(100000,6.8,5)['maturity'])}. "
         f"Or {INR(2000)}/month RD at 6.8% for 12 months → {INR(fm.rd_maturity(2000,6.8,12)['maturity'])}."),
     "concepts": ["fd", "rd"],
     "tutor": ("When you want safety and a guaranteed return, deposits are your friends. A Fixed Deposit "
               "takes one lump sum and locks it for a chosen time at a rate that won't change — calm and "
               "predictable. A Recurring Deposit is gentler on the wallet: you put in a small fixed "
               "amount every month, and it quietly grows. Both are protected and both compound. If you're "
               "just starting, a recurring deposit is a beautiful way to build the saving habit.")},

    {"id": "deposit_insurance", "module": "accounts", "title": "Are my deposits safe? (DICGC)",
     "icon": "🛡️", "minutes": 3,
     "summary": "Your bank deposits are insured by DICGC, a subsidiary of the RBI, up to ₹5 lakh per "
                "depositor per bank — covering principal and interest.",
     "key_points": [
         "₹5,00,000 guarantee per depositor per bank (raised from ₹1 lakh in 2020).",
         "Covers savings, current, FD and RD together at one bank.",
         "Large savings? Spreading across banks multiplies your coverage."],
     "worked_example": "₹4,00,000 across SBI accounts is fully insured. ₹8,00,000 at one bank is insured "
                       "only up to ₹5,00,000 — splitting across two banks covers it fully.",
     "concepts": ["deposit_insurance"],
     "tutor": ("Let me put your mind at ease about safety. Every rupee you keep in a bank is backed by an "
               "insurance called DICGC, run by the Reserve Bank of India. If anything ever went wrong with "
               "a bank, you are guaranteed up to five lakh rupees per person, per bank — and that includes "
               "the interest. So your savings rest on a strong government-backed safety net. If you ever "
               "hold very large savings, simply spreading them across a couple of banks keeps all of it "
               "protected."),
     "tutor_hi": ("सुरक्षा को लेकर आपका मन हल्का कर दूँ। बैंक में रखा आपका हर रुपया DICGC नाम के बीमे से सुरक्षित है, "
                  "जिसे भारतीय रिज़र्व बैंक चलाता है। अगर कभी किसी बैंक के साथ कुछ ग़लत हो जाए, तो हर व्यक्ति को हर "
                  "बैंक में पाँच लाख रुपये तक की गारंटी मिलती है — और इसमें ब्याज भी शामिल है। तो आपकी बचत एक मज़बूत, "
                  "सरकार-समर्थित सुरक्षा जाल पर टिकी है।")},

    # ── Cards ──────────────────────────────────────────────────────────
    {"id": "debit_vs_credit", "module": "cards", "title": "Debit vs Credit: the real difference",
     "icon": "💳", "minutes": 3,
     "summary": "A debit card spends your own money instantly. A credit card borrows the bank's money "
                "to be repaid later — free if you pay in full, costly if you don't.",
     "key_points": [
         "Debit = your balance, now. Credit = a short-term loan from the bank.",
         "Pay the credit bill in FULL by the due date and you pay zero interest.",
         "Pay only the 'minimum due' and almost the whole balance keeps charging ~36-42% a year."],
     "worked_example": _wex(
         f"Carry {INR(50000)} on a card at 3.5%/month and it costs about "
         f"{fm.credit_card_interest(50000,3.5)['apr_pa']}% per year in interest."),
     "concepts": ["debit_vs_credit", "credit_card_interest"],
     "tutor": ("Cards feel mysterious, so let's make them simple and friendly. A debit card spends money "
               "you already have — it pulls straight from your account. A credit card is different: the "
               "bank lends you money for a few weeks. Here's the golden rule that keeps you safe: if you "
               "pay your credit-card bill in full by the due date, you pay no interest at all — it's free. "
               "But if you pay only the small 'minimum due', almost the entire balance keeps charging "
               "interest at around forty percent a year. So use the credit card freely, but always pay it "
               "in full. Do that, and the card works for you, never against you."),
     "tutor_hi": ("कार्ड को आसान बना देते हैं। डेबिट कार्ड आपका अपना पैसा खर्च करता है — सीधे खाते से। क्रेडिट कार्ड "
                  "अलग है: बैंक आपको कुछ हफ़्तों के लिए उधार देता है। एक सुनहरा नियम याद रखिए — अगर आप पूरा बिल समय "
                  "पर चुका दें, तो कोई ब्याज नहीं लगता, बिल्कुल मुफ़्त। लेकिन अगर सिर्फ़ 'न्यूनतम राशि' चुकाएँ, तो लगभग "
                  "पूरी रकम पर सालाना करीब चालीस प्रतिशत ब्याज लगता रहता है। इसलिए कार्ड ज़रूर इस्तेमाल कीजिए, पर "
                  "हमेशा पूरा बिल चुकाइए।")},

    {"id": "min_due_trap", "module": "cards", "title": "The minimum-due trap",
     "icon": "⚠️", "minutes": 3,
     "summary": "The 'minimum due' is designed to keep you in debt. Paying it feels responsible but the "
                "balance barely moves while interest piles up.",
     "key_points": [
         "Minimum due is usually ~5% of the balance — the rest keeps accruing interest.",
         "It can take years and cost more than the original purchase to clear.",
         "Always aim to pay the FULL statement balance; if not, pay as much as you can."],
     "worked_example": _wex(
         f"Owe {INR(50000)} and pay only the minimum each month? After a year you've paid "
         f"{INR(fm.min_due_trap(50000)['paid_so_far'])} and STILL owe "
         f"{INR(fm.min_due_trap(50000)['balance_after'])}."),
     "concepts": ["credit_card_interest"],
     "tutor": ("Here is a quiet trap to walk around carefully. On your credit-card bill there's a small "
               "number called the minimum due. Paying it feels responsible — but it's designed to keep you "
               "borrowing. Watch what happens: on a fifty-thousand-rupee balance, if you pay only the "
               "minimum for a whole year, you'll have paid out a large amount and still owe almost as much "
               "as you started with, because interest keeps refilling the balance. The way out is simple "
               "and I'll always remind you — pay the full amount whenever you can.")},

    # ── Payments ───────────────────────────────────────────────────────
    {"id": "rails", "module": "payments", "title": "UPI, IMPS, NEFT, RTGS",
     "icon": "🔁", "minutes": 3,
     "summary": "Different ways to move money. UPI and IMPS are instant and 24×7. NEFT settles in "
                "batches. RTGS is for large amounts (₹2 lakh+) in real time.",
     "key_points": [
         "Small, instant, anytime: UPI / IMPS.",
         "NEFT: works in half-hourly batches — fine when not urgent.",
         "RTGS: real-time, for big transfers of ₹2 lakh and above."],
     "worked_example": "Sending ₹3,000 to a friend at 11 PM? Use UPI or IMPS — instant, any time, any day.",
     "concepts": ["neft_imps_rtgs"],
     "tutor": ("Moving money used to mean a queue at the branch. Today your phone does it in seconds. For "
               "everyday amounts, UPI and IMPS are instant and work all day, every day, even at midnight. "
               "NEFT is a calmer option that settles in small batches — perfectly fine when there's no "
               "hurry. And for large transfers, two lakh rupees and above, there's RTGS, which moves the "
               "money in real time. Pick instant for small and urgent, RTGS for big.")},

    {"id": "fraud_safety", "module": "payments", "title": "Spotting fraud & OTP discipline",
     "icon": "🛡️", "minutes": 4,
     "summary": "The bank will NEVER ask for your OTP, PIN, or full card number. Almost every fraud "
                "depends on tricking YOU into sharing one of these or clicking a fake link.",
     "key_points": [
         "Never share OTP/PIN/CVV — not with 'bank staff', not with anyone.",
         "A UPI 'collect request' takes money FROM you — you never enter a PIN to RECEIVE money.",
         "Don't click KYC/'account blocked' links in SMS; open the official app yourself."],
     "worked_example": "An SMS: 'KYC expired, click to update.' That's phishing — banks never do this. "
                       "Delete it and check your account through the official app.",
     "concepts": ["netbanking_safety"],
     "tutor": ("Now let me protect you like family. Remember one sentence and you'll defeat almost every "
               "scam: the bank will never ask for your OTP, your PIN, or your full card number. Anyone who "
               "does — even if they sound official — is a fraudster. Two more gentle reminders. To receive "
               "money, you never enter your PIN; if an app asks for your PIN to 'receive', it's actually "
               "taking money from you. And those scary messages saying your account is blocked, click "
               "here — don't click. Open your bank's real app yourself. Stay calm, and you stay safe."),
     "tutor_hi": ("अब मैं आपको अपने परिवार की तरह बचाऊँगी। एक वाक्य याद रखिए और लगभग हर धोखे से बच जाएँगे: बैंक "
                  "कभी आपका OTP, PIN या पूरा कार्ड नंबर नहीं माँगता। जो भी माँगे — चाहे कितना भी आधिकारिक लगे — वह "
                  "ठग है। दो बातें और। पैसा पाने के लिए कभी PIN नहीं डाला जाता; अगर कोई ऐप 'पैसे पाने' के लिए PIN "
                  "माँगे, तो असल में वह आपसे पैसे ले रहा है। और 'खाता बंद हो गया, यहाँ क्लिक करें' जैसे डरावने संदेश — "
                  "क्लिक मत कीजिए। अपने बैंक का असली ऐप खुद खोलिए।")},

    # ── Loans ──────────────────────────────────────────────────────────
    {"id": "emi_basics", "module": "loans", "title": "How EMIs really work",
     "icon": "🏠", "minutes": 4,
     "summary": "An EMI is a fixed monthly payment that covers interest plus a bit of principal. Early "
                "EMIs are mostly interest; later ones mostly principal.",
     "key_points": [
         "Longer tenure = smaller EMI but much MORE total interest.",
         "Reducing-balance loans charge interest only on what you still owe.",
         "Prepaying early, when the balance is high, saves the most interest."],
     "worked_example": _wex(
         f"{INR(500000)} home loan at 9% for 5 years: EMI {INR(fm.emi_reducing(500000,9,60)['emi'])}, "
         f"total interest {INR(fm.emi_reducing(500000,9,60)['total_interest'])}."),
     "concepts": ["emi"],
     "tutor": ("A loan can feel heavy, so let's understand it together and take the fear out. Every month "
               "you pay a fixed amount called an EMI. In the early months, most of that goes toward "
               "interest and only a little reduces what you owe; later, it flips. Two friendly truths: a "
               "longer tenure lowers your monthly EMI but you end up paying much more interest overall. "
               "And paying a little extra early — when your balance is still big — saves you the most. "
               "Borrow for what truly grows your life, and repay a little faster when you can.")},

    {"id": "flat_vs_reducing", "module": "loans", "title": "The flat-rate trick",
     "icon": "🎯", "minutes": 4,
     "summary": "A 'flat' interest rate sounds lower but costs far more, because it charges interest on "
                "the full amount even as you repay. Always ask for the reducing-balance rate.",
     "key_points": [
         "Flat rate charges interest on the original amount for the whole tenure.",
         "A '10% flat' loan can really cost ~17-18% in reducing-balance terms.",
         "When comparing loans, only compare reducing-balance (effective) rates."],
     "worked_example": _wex(
         f"A '10% flat' loan of {INR(300000)} for 36 months actually costs about "
         f"{fm.flat_vs_reducing(300000,10,36)['effective_reducing_rate']}% in real reducing terms."),
     "concepts": ["flat_vs_reducing"],
     "tutor": ("Let me hand you a shield against a very common trick. Some lenders advertise a 'flat' "
               "interest rate because it sounds small. But a flat rate charges interest on your full "
               "original loan for the entire period — even though you're steadily paying it back. So a "
               "loan sold as ten percent flat can actually cost you around seventeen or eighteen percent "
               "in honest, reducing-balance terms. Whenever someone quotes a flat rate, smile and ask: "
               "'And what is that in reducing-balance terms?' That one question can save you a great deal.")},

    {"id": "credit_score", "module": "loans", "title": "Your credit score (CIBIL)",
     "icon": "⭐", "minutes": 3,
     "summary": "Your credit score is a trust number lenders use. Paying on time and using little of "
                "your limit builds it; missed payments and maxed cards break it.",
     "key_points": [
         "Pay every EMI and card bill on time — this matters most.",
         "Keep credit utilisation under ~30% of your limit.",
         "Don't apply for many loans at once; each hard check dings the score."],
     "worked_example": "Two people borrow the same amount. The one who never misses a payment gets future "
                       "loans cheaper — a better score can mean a lower interest rate.",
     "concepts": ["credit_score"],
     "tutor": ("Think of your credit score as your financial reputation — a number that tells lenders how "
               "trustworthy you are with money. The recipe to build it is wonderfully simple: pay your "
               "EMIs and card bills on time, every time, and don't use up your whole credit limit. Avoid "
               "applying for many loans in a rush. Do this patiently, and one day when you want a home or "
               "a business loan, the bank will offer it to you faster, and often cheaper.")},

    # ── Govt schemes ───────────────────────────────────────────────────
    {"id": "jan_dhan", "module": "govt_schemes", "title": "Jan Dhan & basic banking",
     "icon": "🪙", "minutes": 3,
     "summary": "PM Jan Dhan Yojana gives a zero-balance bank account with a RuPay card, accident cover, "
                "and a gateway to government benefits paid directly into your account.",
     "key_points": [
         "Zero minimum balance — banking for everyone.",
         "Comes with a free RuPay debit card and built-in accident insurance.",
         "Direct Benefit Transfer (DBT) sends subsidies straight to the account — no middlemen."],
     "worked_example": "Government subsidies and pensions land directly in a Jan Dhan account via DBT — "
                       "safe, fast, and fully yours.",
     "concepts": ["govt_schemes"],
     "tutor": ("Banking is for everyone, and Jan Dhan is the proof. It's a bank account you can open with "
               "zero balance — no need to keep a minimum amount. It comes with a free RuPay card and even "
               "built-in accident cover. Best of all, government help — subsidies, pensions, support — "
               "comes straight into your own account, with no one in between. It's the first step into the "
               "financial world, and a proud one.")},

    {"id": "jan_suraksha", "module": "govt_schemes", "title": "Tiny premiums, big protection",
     "icon": "🛟", "minutes": 4,
     "summary": "Through your bank you can get life and accident cover for a few rupees a year: PMJJBY "
                "(life), PMSBY (accident), and Atal Pension for old-age income.",
     "key_points": [
         "PMJJBY: ₹2 lakh life cover for about ₹436/year, auto-debited from your account.",
         "PMSBY: ₹2 lakh accident cover for around ₹20/year.",
         "Atal Pension Yojana: small monthly savings now for a guaranteed pension later."],
     "worked_example": "For under ₹500 a year combined, PMJJBY + PMSBY give ₹4 lakh of protection for "
                       "your family — among the cheapest cover anywhere.",
     "concepts": ["govt_schemes"],
     "tutor": ("Protection shouldn't be only for the wealthy, and these schemes prove it. Through your own "
               "bank account, for just a few rupees a year, you can give your family real security. One "
               "scheme gives two lakh rupees of life cover for around four hundred rupees a year. Another "
               "gives two lakh of accident cover for about twenty rupees. And the Atal Pension plan lets "
               "you set aside a small amount now for a guaranteed pension in old age. Small premiums, big "
               "peace of mind — I'd gently encourage everyone to consider them.")},
]


# ---------------------------------------------------------------------------
# Helpers used by the server.
# ---------------------------------------------------------------------------

def lessons_for(module_id: str) -> list:
    return [l for l in LESSONS if l["module"] == module_id]


def get_lesson(lesson_id: str) -> dict:
    return next((l for l in LESSONS if l["id"] == lesson_id), None)


def curriculum_outline() -> list:
    """Modules with their lessons (no tutor scripts — kept light for the list view)."""
    out = []
    for m in MODULES:
        ls = [{"id": l["id"], "title": l["title"], "icon": l["icon"],
               "minutes": l["minutes"], "summary": l["summary"]}
              for l in lessons_for(m["id"])]
        out.append({**m, "lessons": ls, "lesson_count": len(ls)})
    return out
