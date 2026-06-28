"""
YONO Nexus — demo server (Python standard library only; no pip, no build step).

Run:   python3 app.py        →  http://localhost:8000
Live:  ANTHROPIC_API_KEY=sk-... python3 app.py   (auto-switches to real Claude)
"""

import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import agent

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("PORT", "8000"))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".svg": "image/svg+xml"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet console
        pass

    # ---- static files -----------------------------------------------------
    def do_GET(self):
        path = "/web/index.html" if self.path in ("/", "") else self.path
        if path.startswith("/web/"):
            return self._serve_file(path[len("/web/"):])
        self._send(404, {"error": "not found"})

    def _serve_file(self, rel):
        safe = os.path.normpath(rel).lstrip("/.")
        full = os.path.join(WEB, safe)
        if not full.startswith(WEB) or not os.path.isfile(full):
            return self._send(404, {"error": "not found"})
        ext = os.path.splitext(full)[1]
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", _CT.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---- JSON API ---------------------------------------------------------
    def do_POST(self):
        body = self._read_json()
        if self.path == "/api/start":
            sid = str(uuid.uuid4())
            session = agent.new_session(sid)
            out = agent.greeting(session)
            out["session_id"] = sid
            return self._send(200, out)
        if self.path == "/api/message":
            sid = body.get("session_id", "")
            session = agent.SESSIONS.get(sid)
            if not session:
                return self._send(400, {"error": "unknown session; reload"})
            out = agent.handle(session, text=body.get("text", ""),
                               action=body.get("action", ""))
            out["session_id"] = sid
            return self._send(200, out)
        self._send(404, {"error": "not found"})

    # ---- plumbing ---------------------------------------------------------
    def _read_json(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return {}

    def _send(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    mode = ("LIVE · Claude " + agent.MODEL) if os.environ.get("ANTHROPIC_API_KEY") \
        else "OFFLINE · deterministic (set ANTHROPIC_API_KEY for live Claude)"
    print("\n  YONO Nexus — Onboarding Agent demo")
    print(f"  Path : {mode}")
    print(f"  URL  : http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
