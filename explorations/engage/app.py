"""
SAARTHI — Proactive Engagement Agent server (stdlib only, port 8003).
Run:  python3 app.py
Live: ANTHROPIC_API_KEY=sk-ant-... python3 app.py
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import agent
import tools

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("ENGAGE_PORT", "8003"))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".svg": "image/svg+xml"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        path = "/index.html" if self.path in ("/", "") else self.path
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

        if p == "/api/customers":
            metrics = tools.get_engagement_metrics()
            customers = []
            for cid in tools.CUSTOMER_IDS:
                c = tools._CUSTOMERS[cid]
                customers.append({
                    "id": c["id"],
                    "name": c["name"],
                    "first_name": c["first_name"],
                    "age": c["age"],
                    "location": c["location"],
                    "preferred_lang": c["preferred_lang"],
                    "mode": c["mode"],
                    "balance_inr": c["balance_inr"],
                    "scenario": c["scenario"],
                    "scenario_label": _SCENARIO_LABELS.get(c["scenario"], c["scenario"]),
                })
            return self._json(200, {
                "metrics": metrics,
                "customers": customers,
                "ai_active": agent._has_key(),
                "path": ("LIVE · Claude " + agent.MODEL) if agent._has_key()
                        else "OFFLINE · deterministic",
            })

        if p == "/api/analyse":
            cid = body.get("customer_id", "")
            if not cid:
                return self._json(400, {"error": "customer_id required"})
            if agent._has_key():
                try:
                    return self._json(200, agent.analyse_customer_live(cid))
                except Exception:
                    pass  # fall through to offline
            return self._json(200, agent.analyse_customer(cid))

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


_SCENARIO_LABELS = {
    "emi_shortfall": "EMI rescue",
    "education_planning": "Education planning",
    "salary_sip": "Salary → SIP",
    "idle_balance": "Idle balance",
    "financial_stress": "Hardship support",
}


def main():
    mode = ("LIVE · Claude " + agent.MODEL) if agent._has_key() \
        else "OFFLINE · deterministic (set ANTHROPIC_API_KEY for live Claude)"
    print("\n  SAARTHI — Proactive Engagement Agent")
    print(f"  Path : {mode}")
    print(f"  URL  : http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
