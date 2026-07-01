"""
FinSmart Arena — game server (stdlib only, port 8001).
Run: python3 game_server.py
AI mode: GEMINI_API_KEY=your_key python3 game_server.py

SECURITY: CORS, rate limiting, input validation.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Add parent dir to path so we can import the shared security module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from security import add_cors_headers, check_rate_limit, validate_json_body

import game_data
import ai_agents as ag
import curriculum
import question_engine as qe

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("FINLEARN_PORT", os.environ.get("GAME_PORT", "8001")))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".png": "image/png", ".svg": "image/svg+xml"}


def _load_env_file():
    """Load .env file from project root if it exists."""
    env_path = os.path.join(HERE, "..", ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    # ---- CORS preflight -------------------------------------------------------
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        add_cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = "/index.html" if self.path in ("/", "") else self.path
        # serve from web/
        safe = os.path.normpath(path.lstrip("/"))
        full = os.path.join(WEB, safe)
        if not full.startswith(WEB) or not os.path.isfile(full):
            return self._json(404, {"error": "not found"})
        ext = os.path.splitext(full)[1]
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", _CT.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        # Rate limit check
        if not check_rate_limit(self):
            return

        # Input validation
        body, error = validate_json_body(self)
        if error:
            return self._json(400, {"error": error})

        p = self.path

        if p == "/api/questions/interest":
            return self._json(200, {"questions": game_data.INTEREST_QUESTIONS, "ai": ag.AI_ACTIVE})

        if p == "/api/questions/cyber":
            return self._json(200, {"scenarios": game_data.CYBER_SCENARIOS, "ai": ag.AI_ACTIVE})

        if p == "/api/questions/cards":
            return self._json(200, {"questions": game_data.CARD_QUESTIONS, "ai": ag.AI_ACTIVE})

        if p == "/api/quiz/ai":
            topic = body.get("topic", "compound interest")
            try:
                level = int(body.get("level", 1))
                level = max(1, min(10, level))  # clamp to valid range
            except (ValueError, TypeError):
                level = 1
            seen = body.get("seen", [])
            if not isinstance(seen, list):
                seen = []
            q = ag.quiz_agent.generate(topic, level, seen)
            if q:
                return self._json(200, {"question": q, "ai": True})
            # Fallback to a static question not in seen list
            pool = game_data.INTEREST_QUESTIONS
            fallback = next((q for q in pool if q.get("concept") not in seen), pool[0])
            return self._json(200, {"question": fallback, "ai": False})

        if p == "/api/advisor":
            try:
                profile = {
                    "age": max(18, min(80, int(body.get("age", 28)))),
                    "idle_amount": max(0, int(body.get("amount", 100000))),
                    "idle_months": max(0, min(120, int(body.get("months", 8)))),
                    "current_rate": float(body.get("rate", 3.5)),
                    "risk": body.get("risk", "low") if body.get("risk") in ("low", "medium", "high") else "low",
                    "goals": body.get("goals", ["general savings"]),
                }
            except (ValueError, TypeError):
                return self._json(400, {"error": "Invalid profile data. Please check your inputs."})
            result = ag.advisor_agent.advise(profile)
            return self._json(200, result)

        if p == "/api/explain":
            q = body.get("question", "")
            wrong = body.get("wrong", "")
            correct = body.get("correct", "")
            concept = body.get("concept", "")
            if not any([q, wrong, correct]):
                return self._json(400, {"error": "At least 'question', 'wrong', or 'correct' is required."})
            text = ag.explainer_agent.explain(q, wrong, correct, concept)
            return self._json(200, {"explanation": text, "ai": ag.AI_ACTIVE})

        if p == "/api/scenario/ai":
            s = ag.scenario_agent.generate_scenario()
            if s:
                return self._json(200, {"scenario": s, "ai": True})
            # fallback: random static scenario not served yet
            import random
            return self._json(200, {
                "scenario": random.choice(game_data.CYBER_SCENARIOS),
                "ai": False,
            })

        if p == "/api/status":
            return self._json(200, {
                "ai_active": ag.AI_ACTIVE,
                "model": "gemini-2.0-flash" if ag.AI_ACTIVE else "offline",
                "games": ["interest", "cyber", "cards", "advisor"],
                "total_questions": (
                    len(game_data.INTEREST_QUESTIONS)
                    + len(game_data.CYBER_SCENARIOS)
                    + len(game_data.CARD_QUESTIONS)
                ),
                "badges": len(game_data.BADGES),
            })

        # ── FinSmart Academy — curriculum, voice tutor, agentic quiz ──────
        if p == "/api/academy/curriculum":
            return self._json(200, {
                "modules": curriculum.curriculum_outline(),
                "concepts": qe.ALL_CONCEPTS,
                "ai_active": ag.AI_ACTIVE,
            })

        if p == "/api/academy/lesson":
            lid = body.get("lesson_id", "")
            lesson = curriculum.get_lesson(lid)
            if not lesson:
                return self._json(404, {"error": f"unknown lesson '{lid}'"})
            tutor = ag.tutor_agent.teach(lesson, body.get("lang", "en"))
            view = {k: lesson[k] for k in
                    ("id", "module", "title", "icon", "minutes", "summary",
                     "key_points", "worked_example", "concepts")}
            return self._json(200, {"lesson": view, "tutor": tutor})

        if p == "/api/academy/tutor":
            lid = body.get("lesson_id", "")
            lesson = curriculum.get_lesson(lid)
            if not lesson:
                return self._json(404, {"error": f"unknown lesson '{lid}'"})
            return self._json(200, {"tutor": ag.tutor_agent.teach(lesson, body.get("lang", "en"))})

        if p == "/api/academy/quiz":
            module = body.get("module") or None
            try:
                n = max(1, min(10, int(body.get("n", 5))))
            except (ValueError, TypeError):
                n = 5
            concept = body.get("concept") or None
            if concept:
                questions = [qe.generate(concept) for _ in range(n)]
            else:
                questions = qe.generate_set(n, module=module)
            return self._json(200, {"questions": questions, "ai": ag.AI_ACTIVE,
                                    "source": "procedural-engine"})

        if p == "/api/academy/generate":
            # One fresh question; if a live key is set, occasionally serve a novel
            # LLM scenario, else the always-correct procedural engine.
            concept = body.get("concept") or None
            if ag.AI_ACTIVE and concept:
                novel = ag.academy_question_agent.novel(concept, body.get("lang", "en"))
                if novel:
                    novel["id"] = f"ai-{concept}"
                    return self._json(200, {"question": novel, "ai": True})
            return self._json(200, {"question": qe.generate(concept), "ai": False})

        self._json(404, {"error": "unknown endpoint"})

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(data)


def main():
    _load_env_file()
    # Reload AI state after env is loaded
    ag.GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
    ag.AI_ACTIVE = bool(ag.GEMINI_KEY)

    mode = f"LIVE · Gemini 2.0 Flash (free tier)" if ag.AI_ACTIVE else \
        "OFFLINE · rich static content (set GEMINI_API_KEY for AI enhancement)"
    print("\n  FinSmart Arena — Financial Literacy Game")
    print(f"  AI   : {mode}")
    print(f"  URL  : http://localhost:{PORT}")
    print(f"  Security: CORS ✓ | Rate limiting ✓ | Input validation ✓\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
