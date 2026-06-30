"""
FinPulse — Money Health Score server (stdlib only, port 8004).
Run: python3 app.py

The unifying layer of YONO Nexus: one transparent, self-evaluated score that
ties acquisition (SCOUT) → onboarding → engagement (SAARTHI) → literacy (Academy)
into a single product. No API key required; everything is computed.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import finpulse
import profiles as profiles_mod
import evaluation

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("FINPULSE_PORT", "8004"))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".svg": "image/svg+xml"}


def _cohort_scores():
    return [finpulse.score_profile(p)["score"] for p in profiles_mod.PROFILES.values()]


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

        if p == "/api/cohort":
            cohort = []
            for pid, prof in profiles_mod.PROFILES.items():
                r = finpulse.score_profile(prof)
                cohort.append({
                    "id": pid, "name": prof["name"], "age": prof["age"],
                    "location": prof["location"], "segment": prof["segment"],
                    "score": r["score"], "grade": r["grade"],
                    "grade_label": r["grade_label"],
                })
            cohort.sort(key=lambda x: -x["score"])
            return self._json(200, {"cohort": cohort})

        if p == "/api/score":
            pid = body.get("profile_id", "")
            prof = profiles_mod.PROFILES.get(pid)
            if not prof:
                return self._json(404, {"error": f"unknown profile '{pid}'"})
            r = finpulse.score_profile(prof)
            r["percentile"] = finpulse.percentile_vs_cohort(r["score"], _cohort_scores())
            r["profile"] = {k: prof[k] for k in
                            ("id", "name", "age", "location", "segment")}
            return self._json(200, r)

        if p == "/api/evaluation":
            return self._json(200, evaluation.full_report())

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
    print("\n  FinPulse — Money Health Score (the unifying layer)")
    print("  Transparent · computed · self-evaluated — no API key needed")
    print(f"  URL  : http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
