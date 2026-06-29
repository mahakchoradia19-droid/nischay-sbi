"""
YONO Nexus — shared security middleware.

Provides CORS, rate limiting, input validation, session cleanup, and PII masking.
Used by all four servers (onboarding, finlearn, scout, engage) to address security
vulnerabilities identified during audit.

Design: stdlib-only (no pip), deterministic, no external dependencies.
"""

import hashlib
import re
import threading
import time

# ---------------------------------------------------------------------------
# Configuration — override via environment or constructor.
# ---------------------------------------------------------------------------
DEFAULT_ALLOWED_ORIGINS = ["http://localhost:8000", "http://localhost:8001",
                           "http://localhost:8002", "http://localhost:8003",
                           "http://127.0.0.1:8000", "http://127.0.0.1:8001",
                           "http://127.0.0.1:8002", "http://127.0.0.1:8003"]
MAX_BODY_BYTES = 64 * 1024       # 64 KB max JSON body
SESSION_TTL_SECONDS = 30 * 60    # 30-minute session expiry
RATE_LIMIT_WINDOW = 60           # 1-minute window
RATE_LIMIT_MAX_REQUESTS = 60     # 60 requests per window per IP


# ---------------------------------------------------------------------------
# CORS helper — sets headers on any BaseHTTPRequestHandler response.
# ---------------------------------------------------------------------------
def add_cors_headers(handler, allowed_origins=None):
    """Add CORS headers to the response. Call before end_headers()."""
    origins = allowed_origins or DEFAULT_ALLOWED_ORIGINS
    origin = handler.headers.get("Origin", "")

    if origin in origins:
        handler.send_header("Access-Control-Allow-Origin", origin)
    else:
        # In demo/hackathon mode, allow localhost broadly
        handler.send_header("Access-Control-Allow-Origin", "http://localhost:8000")

    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, X-Session-ID")
    handler.send_header("Access-Control-Max-Age", "3600")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("X-Frame-Options", "DENY")
    handler.send_header("Referrer-Policy", "strict-origin-when-cross-origin")


# ---------------------------------------------------------------------------
# Rate limiter — in-memory token bucket, keyed by client IP.
# ---------------------------------------------------------------------------
class RateLimiter:
    """Simple in-memory rate limiter. Thread-safe."""

    def __init__(self, window_seconds=RATE_LIMIT_WINDOW,
                 max_requests=RATE_LIMIT_MAX_REQUESTS):
        self._window = window_seconds
        self._max = max_requests
        self._buckets = {}  # ip → (count, window_start)
        self._lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        """Return True if the request is within rate limits."""
        now = time.time()
        with self._lock:
            count, start = self._buckets.get(client_ip, (0, now))
            if now - start > self._window:
                # New window
                self._buckets[client_ip] = (1, now)
                return True
            if count >= self._max:
                return False
            self._buckets[client_ip] = (count + 1, start)
            return True

    def cleanup(self):
        """Remove expired entries."""
        now = time.time()
        with self._lock:
            expired = [ip for ip, (_, start) in self._buckets.items()
                       if now - start > self._window * 2]
            for ip in expired:
                del self._buckets[ip]


# Global rate limiter instance
rate_limiter = RateLimiter()


# ---------------------------------------------------------------------------
# Input validation helpers.
# ---------------------------------------------------------------------------
def validate_json_body(handler) -> tuple:
    """
    Read and validate a JSON body from the request.

    Returns: (parsed_dict, error_string)
    - On success: (dict, None)
    - On failure: (None, "error description")
    """
    import json

    content_type = handler.headers.get("Content-Type", "")
    if content_type and "application/json" not in content_type:
        return None, "Content-Type must be application/json"

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        return None, "Invalid Content-Length header"

    if length > MAX_BODY_BYTES:
        return None, f"Request body too large (max {MAX_BODY_BYTES} bytes)"

    if length == 0:
        return {}, None

    try:
        raw = handler.rfile.read(length)
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None, "Request body must be a JSON object"
        return data, None
    except (json.JSONDecodeError, ValueError):
        return None, "Invalid JSON in request body"


def check_rate_limit(handler) -> bool:
    """
    Check rate limit for the client. Returns True if allowed, False if blocked.
    If blocked, sends a 429 response automatically.
    """
    import json

    client_ip = handler.client_address[0]
    if rate_limiter.is_allowed(client_ip):
        return True

    # Rate limited — send 429
    body = json.dumps({"error": "Too many requests. Please try again later."}).encode()
    handler.send_response(429)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Retry-After", str(RATE_LIMIT_WINDOW))
    add_cors_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)
    return False


# ---------------------------------------------------------------------------
# Session management — expiry and cleanup.
# ---------------------------------------------------------------------------
class SessionManager:
    """Manages session lifecycle with automatic TTL-based cleanup."""

    def __init__(self, ttl_seconds=SESSION_TTL_SECONDS):
        self._ttl = ttl_seconds
        self._cleanup_timer = None

    def start_cleanup_timer(self, sessions_dict: dict, interval=300):
        """Start a background timer that cleans expired sessions every `interval` seconds."""
        def _cleanup():
            self._expire_sessions(sessions_dict)
            self._cleanup_timer = threading.Timer(interval, _cleanup)
            self._cleanup_timer.daemon = True
            self._cleanup_timer.start()

        self._cleanup_timer = threading.Timer(interval, _cleanup)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def _expire_sessions(self, sessions_dict: dict):
        """Remove sessions older than TTL."""
        now = time.time()
        expired = [sid for sid, s in sessions_dict.items()
                   if now - s.get("metrics", {}).get("started_at", now) > self._ttl]
        for sid in expired:
            del sessions_dict[sid]
        if expired:
            print(f"  [security] Cleaned {len(expired)} expired session(s)")

    def is_session_valid(self, session: dict) -> bool:
        """Check if a session is still within its TTL."""
        started = session.get("metrics", {}).get("started_at", 0)
        return (time.time() - started) < self._ttl


# Global session manager instance
session_manager = SessionManager()


# ---------------------------------------------------------------------------
# PII masking — redact Aadhaar and PAN from log output.
# ---------------------------------------------------------------------------
_AADHAAR_RE = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
_PAN_RE = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
_AADHAAR_LAST4_RE = re.compile(r"\b\d{4}\b")  # too broad on its own, use contextually


def mask_pii(text: str) -> str:
    """Redact Aadhaar (12-digit) and PAN numbers from text for safe logging."""
    text = _AADHAAR_RE.sub("XXXX-XXXX-XXXX", text)
    text = _PAN_RE.sub("XXXXX0000X", text)
    return text


def mask_aadhaar_last4(last4: str) -> str:
    """Mask Aadhaar last 4 digits for display: 7731 → XX31."""
    if len(last4) == 4:
        return "XX" + last4[2:]
    return "XXXX"


def mask_pan(pan: str) -> str:
    """Mask PAN for display: ABKPS4416Q → ABKPS****Q."""
    if len(pan) == 10:
        return pan[:5] + "****" + pan[9:]
    return "**********"


# ---------------------------------------------------------------------------
# Request logging with PII protection.
# ---------------------------------------------------------------------------
def log_request(handler, endpoint: str, extra: str = ""):
    """Log an API request with PII redacted."""
    client_ip = handler.client_address[0]
    masked_extra = mask_pii(extra) if extra else ""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"  [{timestamp}] {client_ip} → {endpoint} {masked_extra}")
