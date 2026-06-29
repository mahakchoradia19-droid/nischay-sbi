"""
Simulated SBI tool layer for the YONO Nexus Onboarding Agent.

Each function mimics a real SBI/regulatory integration the agent would call as a
*tool* (never holding credentials itself). In production these are gRPC/REST
calls to TCS BaNCS, CKYC, NSDL, and the AML engine. Here they are deterministic
stubs so the demo runs with zero setup and zero network.

The schemas at the bottom (TOOL_SCHEMAS) are the exact tool definitions handed to
Claude when an ANTHROPIC_API_KEY is present, so the live and offline paths call
the *same* tools.

SECURITY NOTES (vulnerability fixes):
  - PAN and Aadhaar are masked in all return values by default
  - AML screen can return HIGH risk to demonstrate escalation path
  - OCR can fail for unsupported documents
  - PAN validation can fail for expired/invalid PAN
  - CKYC can detect existing records
"""

import random
import re
import time

from security import mask_pan, mask_aadhaar_last4

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

# ---------------------------------------------------------------------------
# Configurable failure modes — set via environment or test harness.
# These allow the demo to showcase error handling and escalation paths.
# ---------------------------------------------------------------------------
_FORCE_AML_HIT = False       # Set True to demo AML escalation
_FORCE_OCR_FAIL = False      # Set True to demo OCR failure recovery
_FORCE_PAN_INVALID = False   # Set True to demo PAN validation failure
_FORCE_CKYC_EXISTS = False   # Set True to demo duplicate detection

import os
if os.environ.get("DEMO_AML_HIT"):
    _FORCE_AML_HIT = True
if os.environ.get("DEMO_OCR_FAIL"):
    _FORCE_OCR_FAIL = True
if os.environ.get("DEMO_PAN_INVALID"):
    _FORCE_PAN_INVALID = True
if os.environ.get("DEMO_CKYC_EXISTS"):
    _FORCE_CKYC_EXISTS = True


def ocr_extract(document_type: str) -> dict:
    """Run OCR + face-liveness on an uploaded ID and return structured fields."""
    time.sleep(0.25)  # simulate inference latency

    # Validate document type
    doc = document_type.lower().strip()
    if doc not in ("aadhaar", "pan"):
        return {
            "ok": False,
            "error": f"Unsupported document type '{document_type}'. "
                     f"Accepted: 'aadhaar', 'pan'.",
            "suggestion": "Please upload an Aadhaar card or PAN card.",
        }

    # Simulate OCR failure (blurry photo, tampered document)
    if _FORCE_OCR_FAIL:
        return {
            "ok": False,
            "error": "OCR extraction failed — document image is too blurry or "
                     "partially obscured. Please re-upload a clear photo.",
            "confidence": 0.21,
            "retry_allowed": True,
        }

    if doc == "aadhaar":
        fields = dict(_MOCK_AADHAAR)
        # Mask Aadhaar in returned fields for security
        fields["aadhaar_last4_display"] = mask_aadhaar_last4(fields["aadhaar_last4"])
        return {"ok": True, "document": "aadhaar", "fields": fields,
                "liveness_score": 0.97, "tamper_detected": False}

    if doc == "pan":
        fields = dict(_MOCK_PAN)
        # Mask PAN in returned fields for security
        fields["pan_display"] = mask_pan(fields["pan"])
        return {"ok": True, "document": "pan", "fields": fields,
                "tamper_detected": False}

    return {"ok": False, "error": f"unsupported document_type '{document_type}'"}


def validate_pan(pan: str, name: str) -> dict:
    """Validate PAN against the NSDL registry and check name congruence."""
    time.sleep(0.2)

    # Input validation
    if not pan or not re.match(r"^[A-Z]{5}\d{4}[A-Z]$", pan.upper()):
        return {
            "ok": False,
            "error": f"Invalid PAN format: '{mask_pan(pan) if pan else '(empty)'}'. "
                     f"PAN must be 10 characters (ABCDE1234F).",
            "pan_status": "INVALID_FORMAT",
            "name_match": False,
        }

    # Simulate PAN expired/invalid
    if _FORCE_PAN_INVALID:
        return {
            "ok": False,
            "pan": mask_pan(pan),
            "pan_status": "DEACTIVATED",
            "error": "This PAN has been deactivated by NSDL. The customer "
                     "must contact the nearest Income Tax office.",
            "name_match": False,
            "name_match_score": 0.0,
        }

    registry_name = _MOCK_PAN["name"]
    name_match = _normalised(name) == _normalised(registry_name)
    return {
        "ok": True,
        "pan": mask_pan(pan),
        "pan_status": _MOCK_PAN["status"],
        "registry_name": registry_name,
        "name_match": name_match,
        # a real adapter returns a fuzzy score; the agent decides what to do with it
        "name_match_score": 0.62 if not name_match else 1.0,
    }


def ckyc_lookup(aadhaar_last4: str, name: str) -> dict:
    """Check the Central KYC Registry for an existing record (dedupe / pre-fill)."""
    time.sleep(0.2)

    # Simulate existing CKYC record (duplicate customer)
    if _FORCE_CKYC_EXISTS:
        return {
            "ok": True,
            "existing_record": True,
            "ckyc_id": "CKYC-2024-8847291",
            "message": "Existing CKYC record found. Customer already has KYC on file. "
                       "Pre-filling verified details from existing record.",
            "existing_account_hint": "Savings account ending XX4421 (opened 2019)",
        }

    return {"ok": True, "existing_record": False, "ckyc_id": None,
            "message": "No existing CKYC record; proceed with fresh KYC."}


def aml_screen(name: str, dob: str) -> dict:
    """Screen the applicant against sanctions / PEP / adverse-media watchlists."""
    time.sleep(0.25)

    # Simulate AML high-risk hit — this is the escalation demo path
    if _FORCE_AML_HIT:
        return {
            "ok": True,
            "risk": "HIGH",
            "sanctions_hit": True,
            "pep": False,
            "decision": "HOLD",
            "reason": "Possible match against OFAC sanctions list (SDN). "
                      "Manual review required by AML compliance officer.",
            "escalation_required": True,
            "escalation_team": "AML Compliance — Level 2 Review",
        }

    return {"ok": True, "risk": "LOW", "sanctions_hit": False, "pep": False,
            "decision": "CLEAR"}


def create_account(full_name: str, pan: str, aadhaar_last4: str,
                   occupation: str) -> dict:
    """Open the account in core banking (TCS BaNCS) and return the account no."""
    time.sleep(0.3)

    # Input validation
    if not all([full_name, pan, aadhaar_last4, occupation]):
        missing = []
        if not full_name: missing.append("full_name")
        if not pan: missing.append("pan")
        if not aadhaar_last4: missing.append("aadhaar_last4")
        if not occupation: missing.append("occupation")
        return {
            "ok": False,
            "error": f"Missing required fields: {', '.join(missing)}",
            "status": "REJECTED",
        }

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
                       "Use for an Aadhaar or PAN image to extract structured fields. "
                       "Returns ok=False if document type is unsupported or image is unreadable.",
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
                       "the supplied name matches the registered name. "
                       "Returns ok=False if PAN format is invalid or PAN is deactivated.",
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
        "description": "Look up the Central KYC Registry for an existing record. "
                       "If existing_record is True, the customer is already known to CKYC.",
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
        "description": "Screen the applicant against sanctions/PEP/adverse-media lists. "
                       "If decision is HOLD, escalation to AML compliance is required — "
                       "do NOT proceed with account opening.",
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
        "description": "Open the savings account in core banking once KYC + AML pass. "
                       "Only call this after all verifications return ok=True and "
                       "AML decision is CLEAR.",
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
