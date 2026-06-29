"""
FinSmart Arena — 4 specialized Gemini-powered agents.

All agents degrade gracefully to static offline content if no key is set.
Get a free key (no credit card) at: https://aistudio.google.com/apikey
Set it: export GEMINI_API_KEY=your_key_here

Agent roster:
  QuizAgent    — generates personalised MCQ questions calibrated to player level
  AdvisorAgent — analyses idle money profile, ranks investment options with reasoning
  ExplainerAgent — explains wrong answers in friendly Hindi/English
  ScenarioAgent — generates new cyber-threat scenarios based on current India trends

SECURITY FIX: API key moved from URL query parameter to x-goog-api-key HTTP header.
This prevents the key from leaking into browser history, proxy logs, and CDN edge logs.
"""

import json
import os
import urllib.request
import urllib.error
import game_data

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

# SECURITY FIX: Use header-based auth instead of key-in-URL.
# The key is passed via the x-goog-api-key header, not a query parameter.
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def _gemini(prompt: str, temperature: float = 0.7, max_tokens: int = 1024):
    if not GEMINI_KEY:
        return None
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }).encode()
    try:
        req = urllib.request.Request(
            GEMINI_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_KEY,  # SECURITY: header, not URL param
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        print(f"  [ai_agents] Gemini HTTP error: {e.code} {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"  [ai_agents] Gemini network error: {e.reason}")
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"  [ai_agents] Gemini response parse error: {e}")
        return None


# ---------------------------------------------------------------------------
# Agent 1: QuizAgent
# ---------------------------------------------------------------------------
class QuizAgent:
    """Generates a fresh MCQ question calibrated to the player's level and topic."""

    PROMPT = """You are a financial literacy quiz master for SBI India's FinSmart game.
Generate 1 multiple-choice question on: {topic}
Player level: {level}/10 (1=beginner, 10=expert)
Questions already seen (avoid repeating concepts): {seen}

Rules:
- Exactly 4 options (A, B, C, D)
- Only 1 correct answer
- Use Indian context: rupees, SBI products, Indian regulations
- Level 1-3: basic definitions and simple calculations
- Level 4-6: real scenarios with trade-offs
- Level 7-10: complex tax, regulatory, or edge-case scenarios
- Keep the question under 60 words
- Explanation should be 2-3 sentences max, educational

Respond ONLY with valid JSON in this exact format:
{{
  "q": "question text",
  "opts": ["option A", "option B", "option C", "option D"],
  "ans": 0,
  "explain": "explanation of the correct answer",
  "concept": "concept name"
}}"""

    def generate(self, topic: str, level: int, seen_concepts: list):
        prompt = self.PROMPT.format(
            topic=topic, level=level,
            seen=", ".join(seen_concepts[-5:]) if seen_concepts else "none"
        )
        raw = _gemini(prompt, temperature=0.8, max_tokens=512)
        if not raw:
            return None
        try:
            # Gemini sometimes wraps in markdown code blocks
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            q = json.loads(raw)
            if all(k in q for k in ("q", "opts", "ans", "explain")):
                q["id"] = "ai_gen"
                q["ai_generated"] = True
                return q
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        return None


# ---------------------------------------------------------------------------
# Agent 2: AdvisorAgent
# ---------------------------------------------------------------------------
class AdvisorAgent:
    """Analyses a customer's idle money profile and provides ranked investment advice."""

    PROMPT = """You are a certified financial planner working for SBI India.
A customer's profile:
- Age: {age}
- Idle money: ₹{amount:,} sitting in savings account
- Duration idle: {months} months
- Current savings rate: {rate}% p.a. (very low)
- Risk appetite: {risk}
- Financial goals: {goals}

The opportunity cost so far: ₹{opp_cost:,.0f} in potential additional returns was missed.

Analyse their situation and suggest TOP 3 options from SBI's product range:
[SBI FD, SBI Liquid Fund, SBI ELSS (tax saving MF), PPF, SBI RD, SBI Life Insurance,
SBI Equity Mutual Fund SIP, SBI Gold ETF, SBI Annuity/Pension]

For each option provide:
- Why it fits THIS customer (2 sentences)
- Approximate expected return range
- Key risk and one watch-out

Also give ONE sentence on what to do with the remaining amount (emergency fund advice).
Be warm, encouraging, and use INR amounts. Keep total response under 350 words.
Write in plain English (no markdown headers, just clean paragraphs numbered 1, 2, 3)."""

    def advise(self, profile: dict) -> dict:
        opp_cost = (
            profile["idle_amount"]
            * (7.0 - profile["current_rate"])
            / 100
            * profile["idle_months"]
            / 12
        )
        prompt = self.PROMPT.format(
            age=profile["age"],
            amount=profile["idle_amount"],
            months=profile["idle_months"],
            rate=profile["current_rate"],
            risk=profile["risk"],
            goals=", ".join(profile.get("goals", ["general savings"])),
            opp_cost=opp_cost,
        )
        raw = _gemini(prompt, temperature=0.5, max_tokens=500)
        if raw:
            return {
                "ai": True,
                "opp_cost": opp_cost,
                "advice": raw.strip(),
                "static_options": self._static_options(profile),
            }
        return {
            "ai": False,
            "opp_cost": opp_cost,
            "advice": self._static_advice(profile),
            "static_options": self._static_options(profile),
        }

    def _static_options(self, profile: dict) -> list:
        # Pick the best matching static profile from game_data
        for p in game_data.INVEST_PROFILES:
            if abs(p["age"] - profile["age"]) < 10:
                return p["options"]
        return game_data.INVEST_PROFILES[0]["options"]

    def _static_advice(self, profile: dict) -> str:
        opp = (profile["idle_amount"] * (7.0 - profile["current_rate"]) / 100
               * profile["idle_months"] / 12)
        risk_str = {
            "low": "an FD or Liquid Fund",
            "medium": "a mix of FD and Equity SIP",
            "high": "an Equity Mutual Fund SIP",
        }.get(profile["risk"], "an FD")
        return (
            f"Your ₹{profile['idle_amount']:,} has been earning only "
            f"{profile['current_rate']}% in savings — you've missed out on "
            f"approximately ₹{opp:,.0f} in potential extra returns over "
            f"{profile['idle_months']} months.\n\n"
            f"Given your {profile['risk']} risk appetite and goals "
            f"({', '.join(profile.get('goals', ['general savings']))}), "
            f"I'd recommend starting with {risk_str}. "
            f"SBI offers products that let your money work harder "
            f"while staying accessible. See the options below — "
            f"even moving 60% to an FD today starts compounding immediately."
        )


# ---------------------------------------------------------------------------
# Agent 3: ExplainerAgent
# ---------------------------------------------------------------------------
class ExplainerAgent:
    """Explains why an answer was wrong in a friendly, memorable way."""

    PROMPT = """You are a friendly financial coach helping someone learn via a game.
They just got a quiz question WRONG.

Question: {question}
Their answer: {wrong}
Correct answer: {correct}
Concept: {concept}

Explain in 2-3 SHORT sentences why the correct answer is right.
- Be encouraging, not critical
- Use a simple analogy or real Indian example if possible
- End with one actionable takeaway they can remember
- Maximum 60 words total
- Do NOT use markdown formatting"""

    def explain(self, question: str, wrong: str, correct: str, concept: str) -> str:
        prompt = self.PROMPT.format(
            question=question, wrong=wrong, correct=correct, concept=concept
        )
        raw = _gemini(prompt, temperature=0.6, max_tokens=150)
        return raw.strip() if raw else (
            f"The correct answer is: {correct}. "
            f"This is an important concept about {concept}. "
            "Review the explanation and try again!"
        )


# ---------------------------------------------------------------------------
# Agent 4: ScenarioAgent
# ---------------------------------------------------------------------------
class ScenarioAgent:
    """Generates fresh cyber-threat scenarios based on current India fraud trends."""

    PROMPT = """You are a cybersecurity trainer for SBI India's anti-fraud program.
Generate 1 NEW cyber fraud scenario (different from common phishing/OTP scams).
Focus on a RECENT or EMERGING fraud type in India 2025-2026.

Types to consider: QR code fraud, deepfake video calls, AI voice cloning,
fake UPI collect requests, malicious APK installs, job offer scams,
digital arrest scams, SIM swap attacks.

Respond ONLY with valid JSON:
{{
  "type": "one of: sms/email/call/whatsapp/qr/other",
  "verdict": "scam",
  "content": {{
    "from": "sender identifier",
    "body": "the actual message/scenario description (max 80 words)"
  }},
  "red_flags": ["flag1", "flag2", "flag3"],
  "explain": "why this is fraud and what the criminal gets (2 sentences)",
  "tip": "one actionable protection tip"
}}"""

    def generate_scenario(self):
        raw = _gemini(self.PROMPT, temperature=0.9, max_tokens=400)
        if not raw:
            return None
        try:
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            s = json.loads(raw)
            s["ai_generated"] = True
            return s
        except (json.JSONDecodeError, KeyError, ValueError):
            return None


# Singleton instances for import
quiz_agent = QuizAgent()
advisor_agent = AdvisorAgent()
explainer_agent = ExplainerAgent()
scenario_agent = ScenarioAgent()

AI_ACTIVE = bool(GEMINI_KEY)
