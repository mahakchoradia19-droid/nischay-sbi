"""
FinSmart Arena — game server (stdlib only, port 8001).
Run: python3 app.py
AI mode: GEMINI_API_KEY=your_key python3 app.py
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import game_data
import agents as ag

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("GAME_PORT", "8001"))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".png": "image/png", ".svg": "image/svg+xml"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

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
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        body = self._read()
        p = self.path

        if p == "/api/questions/interest":
            return self._json(200, {"questions": game_data.INTEREST_QUESTIONS, "ai": ag.AI_ACTIVE})

        if p == "/api/questions/cyber":
            return self._json(200, {"scenarios": game_data.CYBER_SCENARIOS, "ai": ag.AI_ACTIVE})

        if p == "/api/questions/cards":
            return self._json(200, {"questions": game_data.CARD_QUESTIONS, "ai": ag.AI_ACTIVE})

        if p == "/api/quiz/ai":
            topic = body.get("topic", "compound interest")
            level = int(body.get("level", 1))
            seen = body.get("seen", [])
            q = ag.quiz_agent.generate(topic, level, seen)
            if q:
                return self._json(200, {"question": q, "ai": True})
            # Fallback to a static question not in seen list
            pool = game_data.INTEREST_QUESTIONS
            fallback = next((q for q in pool if q.get("concept") not in seen), pool[0])
            return self._json(200, {"question": fallback, "ai": False})

        if p == "/api/advisor":
            profile = {
                "age": int(body.get("age", 28)),
                "idle_amount": int(body.get("amount", 100000)),
                "idle_months": int(body.get("months", 8)),
                "current_rate": float(body.get("rate", 3.5)),
                "risk": body.get("risk", "low"),
                "goals": body.get("goals", ["general savings"]),
            }
            result = ag.advisor_agent.advise(profile)
            return self._json(200, result)

        if p == "/api/explain":
            q = body.get("question", "")
            wrong = body.get("wrong", "")
            correct = body.get("correct", "")
            concept = body.get("concept", "")
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

        self._json(404, {"error": "unknown endpoint"})

    def _read(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    mode = f"LIVE · Gemini 2.0 Flash (free tier)" if ag.AI_ACTIVE else \
        "OFFLINE · rich static content (set GEMINI_API_KEY for AI enhancement)"
    print("\n  FinSmart Arena — Financial Literacy Game")
    print(f"  AI   : {mode}")
    print(f"  URL  : http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
