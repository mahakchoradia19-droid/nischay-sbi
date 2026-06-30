"""
DBT Gap Agent — community-scale financial intelligence server (stdlib, port 8005).
Run: python3 app.py

The uncopyable moat layer: detects, diagnoses, acts on, and honestly measures
government credits at risk of bouncing back to PFMS unclaimed — at village,
district, and cohort scale. Helps citizens RECEIVE money they are owed (not a
cross-sell). No API key needed; everything is computed.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import dbt_engine as e

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("COMMUNITY_PORT", "8005"))

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

        if p == "/api/overview":
            districts = []
            for d in e.DISTRICTS:
                r = e.detect(d)
                districts.append({
                    "id": d["id"], "name": r["district"], "state": r["state"],
                    "eligible": r["eligible"], "at_risk_accounts": r["at_risk_accounts"],
                    "at_risk_pct": r["at_risk_pct"], "at_risk_amount_inr": r["at_risk_amount_inr"],
                    "villages": d["villages"],
                })
            districts.sort(key=lambda x: -x["at_risk_amount_inr"])
            return self._json(200, {
                "districts": districts,
                "national": e.national_rollup(),
                "measure": e.measure(),
            })

        if p == "/api/district":
            did = body.get("district_id", "")
            d = next((x for x in e.DISTRICTS if x["id"] == did), None)
            if not d:
                return self._json(404, {"error": f"unknown district '{did}'"})
            det = e.detect(d)
            dg = e.diagnose(det)
            interventions = e.act(d, dg)
            return self._json(200, {
                "detect": {k: det[k] for k in
                           ("district", "state", "eligible", "at_risk_accounts",
                            "at_risk_pct", "at_risk_amount_inr", "total_cycle_amount_inr")},
                "diagnose": dg,
                "act": interventions,
                "villages": d["villages"],
            })

        if p == "/api/measure":
            return self._json(200, e.measure())

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
    print("\n  DBT Gap Agent — community-scale financial intelligence")
    print("  The uncopyable moat: detect → diagnose → act → measure, at cohort scale")
    print(f"  URL  : http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
