"""
YONO Nexus — Onboarding Agent demo server (Python standard library only).

Run:   python3 onboarding_server.py        →  http://localhost:8000
Live:  ANTHROPIC_API_KEY=sk-... python3 onboarding_server.py

SECURITY: CORS, rate limiting, input validation, session expiry, PII masking.
"""

import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import onboarding_agent as agent
from security import add_cors_headers, check_rate_limit, validate_json_body, log_request

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
PORT = int(os.environ.get("PORT", "8000"))

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".svg": "image/svg+xml"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet console — we use our own logger
        pass

    # ---- CORS preflight -------------------------------------------------------
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        add_cors_headers(self)
        self.end_headers()

    # ---- static files ---------------------------------------------------------
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
        self.send_header("Cache-Control", "no-cache")
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(data)

    # ---- JSON API -------------------------------------------------------------
    def do_POST(self):
        # Rate limit check
        if not check_rate_limit(self):
            return

        # Input validation
        body, error = validate_json_body(self)
        if error:
            return self._send(400, {"error": error})

        if self.path == "/api/start":
            log_request(self, "/api/start")
            sid = str(uuid.uuid4())
            session = agent.new_session(sid)
            agent.set_ui_language(session, body.get("lang", "en"))
            out = agent.greeting(session)
            out["session_id"] = sid
            return self._send(200, out)

        if self.path == "/api/message":
            sid = body.get("session_id", "")
            session = agent.SESSIONS.get(sid)
            if not session:
                return self._send(400, {"error": "Unknown or expired session. "
                                                  "Please reload to start a new session."})
            log_request(self, "/api/message", f"session={sid[:8]}… action={body.get('action', '')}")
            out = agent.handle(session, text=body.get("text", ""),
                               action=body.get("action", ""),
                               lang=body.get("lang", ""))
            out["session_id"] = sid
            return self._send(200, out)

        self._send(404, {"error": "not found"})

    # ---- plumbing -------------------------------------------------------------
    def _send(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(data)


def _load_env_file():
    """Load .env file if it exists (simple key=value parser)."""
    env_path = os.path.join(HERE, ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value


def main():
    _load_env_file()
    mode = ("LIVE · Claude " + agent.MODEL) if os.environ.get("ANTHROPIC_API_KEY") \
        else "OFFLINE · deterministic (set ANTHROPIC_API_KEY for live Claude)"
    print("\n  YONO Nexus — Onboarding Agent demo")
    print(f"  Path : {mode}")
    print(f"  URL  : http://localhost:{PORT}")
    print(f"  Security: CORS ✓ | Rate limiting ✓ | Session TTL ✓ | PII masking ✓\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
