"""
Landfall — server (stdlib only).
Run:  python3 app.py   (or `python app.py` on Windows)   ->  http://localhost:8000

Zero dependencies, zero setup: this is meant to run identically on any machine
with Python 3.9+ installed — Windows, macOS, Linux, a judge's laptop, a fresh
VM. No pip install, no venv, no config file to edit.

The API is deliberately thin: the parts that must be REAL — the name
reconciliation and the reactivation gate — run here, on the server, so the
front end cannot fake them.

Hardened for a demo that handles identity-shaped data:
  - binds 127.0.0.1 by default (set HOST=0.0.0.0 explicitly to expose it)
  - same-origin only: no CORS header is emitted at all
  - request-body cap (16 KB) and JSON content-type enforcement
  - per-IP rate limiting (in-memory token bucket)
  - security headers on every response (CSP, nosniff, frame-deny, referrer)
  - path traversal defence via realpath containment
  - no server-version disclosure

Portable by construction:
  - PORT/HOST are read from the environment, never hardcoded
  - if the requested port is already taken (very common on a shared laptop —
    8000 is a popular default for other dev tools), it tries the next few
    ports automatically instead of crashing, and prints whichever one it
    actually bound to
  - all paths are derived from this file's own location (__file__), never
    from the current working directory, so `python3 app.py` works no matter
    which folder you launched it from
"""

import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import engine

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.realpath(os.path.join(HERE, "web"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
PORT_RETRIES = 9          # if PORT is busy, try this many ports upward
AUTO_OPEN = os.environ.get("NO_BROWSER", "") == ""

MAX_BODY = 16 * 1024              # 16 KB is generous for these payloads
RATE_WINDOW = 60                  # seconds
RATE_MAX = 120                    # requests per window per IP

_CT = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
       ".css": "text/css", ".svg": "image/svg+xml", ".ico": "image/x-icon"}

_SECURITY_HEADERS = [
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
    ("Content-Security-Policy",
     "default-src 'self'; script-src 'self' 'unsafe-inline'; "
     "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
     "connect-src 'self'; base-uri 'none'; form-action 'self'; "
     "frame-ancestors 'none'"),
    ("Cache-Control", "no-store"),
]


class _RateLimiter:
    """Per-IP fixed-window limiter. In-memory; resets on restart — right-sized
    for a local demo, replaced by the gateway in production."""

    def __init__(self):
        self._hits = {}
        self._lock = threading.Lock()

    def allow(self, ip):
        now = time.time()
        with self._lock:
            count, start = self._hits.get(ip, (0, now))
            if now - start > RATE_WINDOW:
                self._hits[ip] = (1, now)
                return True
            if count >= RATE_MAX:
                return False
            self._hits[ip] = (count + 1, start)
            return True


_limiter = _RateLimiter()


class Handler(BaseHTTPRequestHandler):
    server_version = "Landfall"       # no python/http version disclosure
    sys_version = ""

    def log_message(self, *a):
        pass

    # ---- static files ----------------------------------------------------
    def do_GET(self):
        if not _limiter.allow(self.client_address[0]):
            return self._json(429, {"error": "too many requests"})
        path = "/index.html" if self.path in ("/", "") else self.path.split("?")[0]
        # realpath containment: symlinks and ../ both resolve before the check
        full = os.path.realpath(os.path.join(WEB, path.lstrip("/")))
        if not (full == WEB or full.startswith(WEB + os.sep)) or not os.path.isfile(full):
            return self._json(404, {"error": "not found"})
        ext = os.path.splitext(full)[1]
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", _CT.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        for k, v in _SECURITY_HEADERS:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    # ---- JSON API ----------------------------------------------------------
    def do_POST(self):
        if not _limiter.allow(self.client_address[0]):
            return self._json(429, {"error": "too many requests"})
        body, err = self._read()
        if err:
            return self._json(400, {"error": err})
        p = self.path

        if p == "/api/queue":
            return self._json(200, {"queue": engine.queue()})

        if p == "/api/person":
            d = engine.diagnose_person(_s(body.get("id"), "ramesh"))
            return self._json(200, d or {"error": "unknown person"})

        if p == "/api/verify":
            v = engine.verify_identity(_s(body.get("id"), "ramesh"),
                                       _s(body.get("document_name")))
            return self._json(200, v)

        if p == "/api/reactivate":
            r = engine.reactivate(_s(body.get("id"), "ramesh"),
                                  _s(body.get("confirmed_name")),
                                  bool(body.get("reconciled")),
                                  request_id=_s(body.get("request_id"), maxlen=64))
            return self._json(200, r)

        if p == "/api/audit":
            return self._json(200, {"audit": engine.audit_log()})

        if p == "/api/journey":
            return self._json(200, engine.journey_get(_s(body.get("id"), "ramesh")))

        if p == "/api/journey/reset":
            return self._json(200, engine.journey_reset(_s(body.get("id"), "ramesh")))

        if p == "/api/cohort":
            return self._json(200, {
                "cohort": engine.cohort_stats(),
                "metrics": engine.honest_metrics(),
            })

        self._json(404, {"error": "unknown endpoint"})

    # ---- plumbing ----------------------------------------------------------
    def _read(self):
        """Validated JSON body: content-type, size cap, object shape."""
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip()
        if ctype and ctype != "application/json":
            return None, "content-type must be application/json"
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None, "bad content-length"
        if n > MAX_BODY:
            return None, "request body too large"
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except (json.JSONDecodeError, ValueError):
            return None, "invalid JSON"
        if not isinstance(data, dict):
            return None, "body must be a JSON object"
        return data, None

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for k, v in _SECURITY_HEADERS:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)


def _s(v, default=None, maxlen=200):
    """Coerce an incoming value to a bounded string (or default)."""
    if v is None:
        return default
    return str(v)[:maxlen]


def _bind(host, first_port, retries):
    """Try first_port, then first_port+1, +2, ... so a busy port (very common
    on a shared laptop — other tools love 8000/8080) never crashes the demo."""
    last_err = None
    for offset in range(retries + 1):
        port = first_port + offset
        try:
            return ThreadingHTTPServer((host, port), Handler), port
        except OSError as e:
            last_err = e
            continue
    raise SystemExit(
        f"\n  Could not bind any port from {first_port} to {first_port + retries} "
        f"on {host}.\n  Something else on this machine is very busy. Try:\n"
        f"    PORT=9000 python3 app.py\n  (Original error: {last_err})\n"
    )


def main():
    httpd, bound_port = _bind(HOST, PORT, PORT_RETRIES)
    url = f"http://localhost:{bound_port}"
    py = os.path.basename(sys.executable) or "python3"

    print("\n  Landfall - the bank that makes sure the money lands")
    print(f"  Open   {url}")
    print(f"  Film   {url}/film.html")
    if bound_port != PORT:
        print(f"  NOTE   port {PORT} was busy, so this is running on {bound_port} instead")
    if HOST != "127.0.0.1":
        print(f"  NOTE   bound to {HOST} - exposed beyond this machine")
    print(f"  Stop   press Ctrl+C  (relaunch any time with `{py} app.py`)")
    print()

    if AUTO_OPEN:
        try:
            webbrowser.open(url)
        except Exception:
            pass   # headless environment (CI, a remote box) - just skip it

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.\n")


if __name__ == "__main__":
    main()
