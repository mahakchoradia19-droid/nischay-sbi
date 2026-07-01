"""
Arrives — server for the demo (stdlib only, port 8000).
Run:  python3 app.py   →  http://localhost:8000

Serves the single-page experience and a small API. The API is deliberately thin:
the parts that must be REAL — the name reconciliation and the reactivation gate —
run here, on the server, so the front end cannot fake them.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import engine

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("PORT", "8000"))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".svg": "image/svg+xml", ".ico": "image/x-icon"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        path = "/index.html" if self.path in ("/", "") else self.path.split("?")[0]
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

        if p == "/api/person":
            d = engine.diagnose_person(body.get("id", "ramesh"))
            return self._json(200, d or {"error": "unknown person"})

        if p == "/api/verify":
            v = engine.verify_identity(body.get("id", "ramesh"),
                                       body.get("document_name"))
            return self._json(200, v)

        if p == "/api/reactivate":
            r = engine.reactivate(body.get("id", "ramesh"),
                                  body.get("confirmed_name"),
                                  bool(body.get("reconciled")))
            return self._json(200, r)

        if p == "/api/cohort":
            return self._json(200, {
                "cohort": engine.cohort_stats(),
                "metrics": engine.honest_metrics(),
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
    print("\n  Arrives — the bank that makes sure the money arrives")
    print(f"  Open  http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
