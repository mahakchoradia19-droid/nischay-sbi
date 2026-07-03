"""
test_server.py — the security attack pass, codified.

Boots the real server on a test port and attacks it the way a reviewer would:
path traversal (plain and encoded), wrong content-type, oversized body,
malformed JSON, header checks. Plain asserts, stdlib only:

    python3 test_server.py
"""

import json
import os
import threading
import urllib.error
import urllib.request

os.environ["PORT"] = "8977"          # test port, before app import reads it
import app as server_app             # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402

_passed = 0


def check(name, cond):
    global _passed
    assert cond, f"FAILED: {name}"
    _passed += 1
    print(f"  ok · {name}")


BASE = "http://127.0.0.1:8977"


def req(path, body=None, ctype="application/json", raw=None, method=None):
    """Return (status, headers, parsed-json-or-None)."""
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    r = urllib.request.Request(BASE + path, data=data, method=method or ("POST" if data else "GET"))
    if data is not None:
        r.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            payload = resp.read()
            try:
                return resp.status, dict(resp.headers), json.loads(payload)
            except (json.JSONDecodeError, ValueError):
                return resp.status, dict(resp.headers), None
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), None


# ── boot the real server in a background thread ─────────────────────
httpd = ThreadingHTTPServer(("127.0.0.1", 8977), server_app.Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

# ── the app itself works ────────────────────────────────────────────
s, h, _ = req("/")
check("index serves", s == 200)
s, _, j = req("/api/verify", {"id": "ramesh"})
check("verify API works end to end", s == 200 and j["outcome"] == "variant")
s, _, j = req("/api/queue", {})
check("queue API works", s == 200 and len(j["queue"]) == 4)
req("/api/journey/reset", {"id": "ramesh"})
req("/api/verify", {"id": "ramesh"})
s, _, j = req("/api/journey", {"id": "ramesh"})
check("journey survives across requests (server-side memory)",
      s == 200 and j["stage"] == "identity_confirm" and j["resumable"] is True)

# ── attacks ─────────────────────────────────────────────────────────
s, _, _ = req("/../engine.py")
check("plain path traversal is refused", s == 404)
s, _, _ = req("/%2e%2e/%2e%2e/engine.py")
check("URL-encoded traversal is refused", s == 404)
s, _, _ = req("/api/verify", {"id": "ramesh"}, ctype="text/plain")
check("non-JSON content type is refused", s == 400)
s, _, _ = req("/api/verify", raw=b'{"id":"' + b"x" * 20000 + b'"}')
check("oversized body (20KB) is refused", s == 400)
s, _, _ = req("/api/verify", raw=b"not json at all")
check("malformed JSON is refused", s == 400)
s, _, _ = req("/api/verify", raw=b'["a","list"]')
check("non-object JSON body is refused", s == 400)
s, _, _ = req("/api/nonexistent", {})
check("unknown endpoint is a clean 404", s == 404)

# ── headers ─────────────────────────────────────────────────────────
_, h, _ = req("/")
check("CSP header present", "Content-Security-Policy" in h)
check("nosniff present", h.get("X-Content-Type-Options") == "nosniff")
check("frame-deny present", h.get("X-Frame-Options") == "DENY")
check("no CORS header emitted (same-origin only)",
      not any(k.lower().startswith("access-control") for k in h))
check("no python version disclosure", "Python" not in h.get("Server", ""))

httpd.shutdown()
print(f"\n  {_passed} checks passed.")
