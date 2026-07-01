"""
SCOUT — Acquisition Agent server (stdlib only, port 8002).
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
PORT = int(os.environ.get("SCOUT_PORT", "8002"))

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

        if p == "/api/pipeline":
            metrics = tools.get_pipeline_metrics()
            prospects = []
            for pid in tools.PROSPECT_IDS:
                pr = tools.get_prospect_profile(pid)
                if pr.get("ok"):
                    q = pr["prospect"]
                    prospects.append({
                        "id": q["id"],
                        "name": q["name"],
                        "segment": q["segment"],
                        "location": q.get("location", ""),
                        "trigger_summary": q.get("trigger_summary", ""),
                        "recommended_product": q.get("recommended_product", ""),
                        "channel": q.get("channel", ""),
                        "signals": q.get("signals", []),
                        "preferred_lang": q.get("preferred_lang", "en"),
                        "life_event": q.get("life_event", ""),
                        "confidence_pct": q.get("confidence_pct", None),
                    })
            return self._json(200, {
                "metrics": metrics,
                "prospects": prospects,
                "ai_active": agent._has_key(),
                "path": ("LIVE · Claude " + agent.MODEL) if agent._has_key()
                        else "OFFLINE · deterministic",
            })

        if p == "/api/analyse":
            pid = body.get("prospect_id", "")
            if not pid:
                return self._json(400, {"error": "prospect_id required"})
            if agent._has_key():
                try:
                    result = agent.analyse_prospect_live(pid)
                    return self._json(200, result)
                except Exception as e:
                    pass  # fall through to offline
            result = agent.analyse_prospect(pid)
            return self._json(200, result)

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
    mode = ("LIVE · Claude " + agent.MODEL) if agent._has_key() \
        else "OFFLINE · deterministic (set ANTHROPIC_API_KEY for live Claude)"
    print("\n  SCOUT — Acquisition Agent")
    print(f"  Path : {mode}")
    print(f"  URL  : http://localhost:{PORT}\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
