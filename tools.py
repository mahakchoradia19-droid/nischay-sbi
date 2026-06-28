"""
Simulated SBI tool layer for the YONO Nexus Onboarding Agent.

Each function mimics a real SBI/regulatory integration the agent would call as a
*tool* (never holding credentials itself). In production these are gRPC/REST
calls to TCS BaNCS, CKYC, NSDL, and the AML engine. Here they are deterministic
stubs so the demo runs with zero setup and zero network.

The schemas at the bottom (TOOL_SCHEMAS) are the exact tool definitions handed to
Claude when an ANTHROPIC_API_KEY is present, so the live and offline paths call
the *same* tools.
"""

import random
import re
import time

# ---------------------------------------------------------------------------
# Mock document corpus. The Aadhaar name ("Rajesh Kumar") deliberately disagrees
# with the PAN name ("Rajesh K Singh") so the agent must self-heal a real-world
# name-mismatch instead of dead-ending the funnel.
# ---------------------------------------------------------------------------
_MOCK_AADHAAR = {
    "name": "Rajesh Kumar",
    "dob": "1991-08-14",
    "gender": "M",
    "address": "12, Gandhi Marg, Bhagalpur, Bihar 812001",
    "aadhaar_last4": "7731",
}

_MOCK_PAN = {
    "name": "Rajesh K Singh",   # mismatch vs Aadhaar — intentional
    "pan": "ABKPS4416Q",
    "status": "VALID",
}


def ocr_extract(document_type: str) -> dict:
    """Run OCR + face-liveness on an uploaded ID and return structured fields."""
    time.sleep(0.25)  # simulate inference latency
    if document_type.lower() == "aadhaar":
        return {"ok": True, "document": "aadhaar", "fields": dict(_MOCK_AADHAAR),
                "liveness_score": 0.97}
    if document_type.lower() == "pan":
        return {"ok": True, "document": "pan", "fields": dict(_MOCK_PAN)}
    return {"ok": False, "error": f"unsupported document_type '{document_type}'"}


def validate_pan(pan: str, name: str) -> dict:
    """Validate PAN against the NSDL registry and check name congruence."""
    time.sleep(0.2)
    registry_name = _MOCK_PAN["name"]
    name_match = _normalised(name) == _normalised(registry_name)
    return {
        "ok": True,
        "pan": pan,
        "pan_status": _MOCK_PAN["status"],
        "registry_name": registry_name,
        "name_match": name_match,
        # a real adapter returns a fuzzy score; the agent decides what to do with it
        "name_match_score": 0.62 if not name_match else 1.0,
    }


def ckyc_lookup(aadhaar_last4: str, name: str) -> dict:
    """Check the Central KYC Registry for an existing record (dedupe / pre-fill)."""
    time.sleep(0.2)
    return {"ok": True, "existing_record": False, "ckyc_id": None,
            "message": "No existing CKYC record; proceed with fresh KYC."}


def aml_screen(name: str, dob: str) -> dict:
    """Screen the applicant against sanctions / PEP / adverse-media watchlists."""
    time.sleep(0.25)
    return {"ok": True, "risk": "LOW", "sanctions_hit": False, "pep": False,
            "decision": "CLEAR"}


def create_account(full_name: str, pan: str, aadhaar_last4: str,
                   occupation: str) -> dict:
    """Open the account in core banking (TCS BaNCS) and return the account no."""
    time.sleep(0.3)
    acct = "3" + "".join(str(random.randint(0, 9)) for _ in range(10))
    return {"ok": True, "account_number": acct, "account_type": "Savings (YONO)",
            "ifsc": "SBIN0001234", "status": "ACTIVE",
            "channel": "YONO Nexus — straight-through, zero human handoff"}


def _normalised(name: str) -> str:
    """Collapse to comparable form: lowercase, strip single-letter initials/punct."""
    tokens = re.sub(r"[^a-z ]", " ", name.lower()).split()
    return " ".join(t for t in tokens if len(t) > 1)


# ---------------------------------------------------------------------------
# Dispatch table + Claude-facing tool schemas (shared by both execution paths).
# ---------------------------------------------------------------------------
TOOL_FUNCS = {
    "ocr_extract": ocr_extract,
    "validate_pan": validate_pan,
    "ckyc_lookup": ckyc_lookup,
    "aml_screen": aml_screen,
    "create_account": create_account,
}

TOOL_SCHEMAS = [
    {
        "name": "ocr_extract",
        "description": "OCR + face-liveness on an uploaded government ID. "
                       "Use for an Aadhaar or PAN image to extract structured fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_type": {"type": "string", "enum": ["aadhaar", "pan"]}
            },
            "required": ["document_type"],
        },
    },
    {
        "name": "validate_pan",
        "description": "Validate a PAN against the NSDL registry and check whether "
                       "the supplied name matches the registered name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pan": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["pan", "name"],
        },
    },
    {
        "name": "ckyc_lookup",
        "description": "Look up the Central KYC Registry for an existing record.",
        "input_schema": {
            "type": "object",
            "properties": {
                "aadhaar_last4": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["aadhaar_last4", "name"],
        },
    },
    {
        "name": "aml_screen",
        "description": "Screen the applicant against sanctions/PEP/adverse-media lists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "dob": {"type": "string"},
            },
            "required": ["name", "dob"],
        },
    },
    {
        "name": "create_account",
        "description": "Open the savings account in core banking once KYC + AML pass.",
        "input_schema": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "pan": {"type": "string"},
                "aadhaar_last4": {"type": "string"},
                "occupation": {"type": "string"},
            },
            "required": ["full_name", "pan", "aadhaar_last4", "occupation"],
        },
    },
]
