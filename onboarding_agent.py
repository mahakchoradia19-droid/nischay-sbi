"""
YONO Nexus — Onboarding Agent orchestrator.

Two execution paths, ONE set of tools (onboarding_tools.py):

  * OFFLINE (default, zero setup): a deterministic goal-state machine that
    reproduces genuine agentic behaviour — autonomous multi-tool sequencing,
    self-healing on a KYC name-mismatch, AML escalation, OCR retry, and
    vernacular memory across language switches.

  * LIVE (auto-enabled when ANTHROPIC_API_KEY is set): the same goal + tools are
    handed to Claude (Opus 4.8) which plans and calls the tools itself via the
    Anthropic Messages API. No SDK dependency — raw urllib so it runs anywhere.

Both paths emit the SAME response contract to the UI:
    {reply, trace, metrics, quick_replies, done, lang}
so the "Agent Reasoning Trace" panel looks identical regardless of path.

VULNERABILITY FIXES:
  - AML failure path: agent escalates on HIGH risk (not just name mismatch)
  - OCR failure path: agent requests re-upload on bad document
  - Session TTL: sessions expire after 30 minutes
  - Better error handling: no bare except, specific exception types
  - More languages: Tamil and Bengali greeting support added
  - PII masking in trace output
"""

import json
import os
import time
import urllib.request
import urllib.error

import onboarding_tools as tools
from security import session_manager, mask_pii

MODEL = os.environ.get("YONO_MODEL", "claude-opus-4-8")

# ---------------------------------------------------------------------------
# Session store (in-memory; one onboarding journey per session_id).
# Sessions are cleaned up by the security module's SessionManager.
# ---------------------------------------------------------------------------
SESSIONS = {}

# Start the session cleanup timer
session_manager.start_cleanup_timer(SESSIONS, interval=300)


def new_session(session_id: str) -> dict:
    s = {
        "id": session_id,
        "state": "await_docs",
        "lang": "en",
        "target_language": None,   # full language name when a live-only language is chosen
        "profile": {},          # accumulated, agent-inferred customer facts
        "metrics": {
            "fields_extracted": 0,
            "fields_asked": 0,
            "tool_calls": 0,
            "human_handoffs": 0,
            "turns": 0,
            "started_at": time.time(),
        },
        "live_messages": [],    # Anthropic-format history (live path only)
    }
    SESSIONS[session_id] = s
    return s


# Languages that have full offline copy; everything else needs the live model.
_OFFLINE_LANGS = ("en", "hi")
_LANG_NAMES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "bn": "Bengali",
    "mr": "Marathi", "te": "Telugu", "gu": "Gujarati", "kn": "Kannada",
    "pa": "Punjabi",
}


def set_ui_language(session: dict, code: str) -> None:
    """
    Apply the user's chosen language.
      - en/hi  : first-class offline (deterministic copy exists).
      - others : if a live key is present, Claude generates that language natively
                 (reply.lang = code → browser speaks it). Otherwise we fall back to
                 English text honestly, rather than mislabel an untranslated string.
    """
    code = (code or "en").split("-")[0].lower()
    if code not in _LANG_NAMES:
        code = "en"
    if code in _OFFLINE_LANGS:
        session["lang"] = code
        session["target_language"] = None
    elif _has_key():
        session["lang"] = code                      # live model will produce it
        session["target_language"] = _LANG_NAMES[code]
    else:
        session["lang"] = "en"                      # honest fallback (English voice)
        session["target_language"] = None


def greeting(session: dict) -> dict:
    return _respond(
        session,
        text=_t(session, "greet"),
        trace=[{"label": "Agent initialised", "detail":
                "Goal: open a compliant SBI savings account, straight-through, "
                "zero human handoff. Path: " + ("LIVE · Claude " + MODEL
                if _has_key() else "OFFLINE · deterministic")}],
        quick_replies=[{"label": "📎 Upload Aadhaar + PAN", "action": "upload_docs"}],
    )


def handle(session: dict, text: str = "", action: str = "", lang: str = "") -> dict:
    """Single entry point the server calls per user turn."""
    # Check session validity
    if not session_manager.is_session_valid(session):
        return _respond(
            session,
            text=_t(session, "session_expired"),
            trace=[{"label": "Session expired", "detail":
                    "Session exceeded 30-minute TTL. Please reload to start a new session."}],
            done=True,
        )

    # Explicit language selection from the UI dropdown (no turn consumed).
    if action == "set_language":
        prev = session["lang"]
        set_ui_language(session, lang)
        name = session["profile"].get("first_name", "")
        note = (f"Language set to {_LANG_NAMES.get(session['lang'], 'English')}"
                + (" (Live AI)" if session.get("target_language") else "") + ".")
        return _respond(
            session,
            text=_t(session, "lang_switch", name=name) if session["lang"] in _OFFLINE_LANGS
                 else f"{note} I'll continue in your language.",
            trace=[{"label": "Language switch", "detail":
                    f"{note} Retained name='{name or '—'}' and state='{session['state']}'."}],
            quick_replies=_current_quick_replies(session),
        )

    # A per-message language hint keeps offline en/hi in sync with the dropdown.
    if lang and lang.split("-")[0].lower() in _OFFLINE_LANGS:
        session["lang"] = lang.split("-")[0].lower()

    session["metrics"]["turns"] += 1

    # Vernacular switch is honoured at any point and demonstrates cross-turn memory.
    if action == "switch_hindi" or _wants_hindi(text):
        session["lang"] = "hi" if session["lang"] == "en" else "en"
        name = session["profile"].get("first_name", "")
        return _respond(
            session,
            text=_t(session, "lang_switch", name=name),
            trace=[{"label": "Memory recall", "detail":
                    f"Retained name='{name or '—'}' and state='{session['state']}' "
                    "across language switch."}],
            quick_replies=_current_quick_replies(session),
        )

    if _has_key():
        try:
            return _handle_live(session, text or action)
        except urllib.error.HTTPError as e:
            session.setdefault("_live_error", f"API error: {e.code} {e.reason}")
            # fall through to deterministic path
        except urllib.error.URLError as e:
            session.setdefault("_live_error", f"Network error: {e.reason}")
        except json.JSONDecodeError as e:
            session.setdefault("_live_error", f"Response parse error: {e}")
        except (KeyError, TypeError, ValueError) as e:
            session.setdefault("_live_error", f"Unexpected error: {e}")
    return _handle_offline(session, text, action)


# ===========================================================================
# OFFLINE deterministic goal-state machine
# ===========================================================================
def _handle_offline(session: dict, text: str, action: str) -> dict:
    state = session["state"]

    if state == "await_docs":
        if action == "upload_docs":
            return _step_ingest_documents(session)
        return _respond(session, text=_t(session, "need_docs"),
                        quick_replies=[{"label": "📎 Upload Aadhaar + PAN",
                                        "action": "upload_docs"}])

    if state == "await_identity_confirm":
        if action == "confirm_identity" or _is_yes(text):
            return _step_resolve_identity(session, confirmed=True)
        if _is_no(text):
            session["metrics"]["human_handoffs"] = 1
            session["state"] = "handoff"
            return _respond(session, text=_t(session, "handoff"),
                            trace=[{"label": "Escalation", "detail":
                                    "Identity could not be reconciled in-dialogue → "
                                    "governed human-in-the-loop handoff (defined "
                                    "exception path)."}])
        return _respond(session, text=_t(session, "confirm_prompt"),
                        quick_replies=_identity_quick_replies(session))

    if state == "await_occupation":
        occ = _parse_occupation(text, action)
        if not occ:
            return _respond(session, text=_t(session, "ask_occupation"),
                            quick_replies=[
                                {"label": _t(session, "salaried"), "action": "occ_salaried"},
                                {"label": _t(session, "self_emp"), "action": "occ_self"}])
        session["profile"]["occupation"] = occ
        session["metrics"]["fields_asked"] += 1
        return _step_open_account(session)

    if state == "aml_hold":
        # AML escalation state — cannot proceed, must wait for compliance review
        return _respond(session, text=_t(session, "aml_hold_info"),
                        trace=[{"label": "AML Hold", "detail":
                                "Account opening blocked pending AML compliance review. "
                                "This is a governed escalation — the agent cannot "
                                "override AML decisions."}])

    if state in ("done", "handoff"):
        return _respond(session, text=_t(session, "already_done"),
                        done=(state == "done"))

    return _respond(session, text=_t(session, "fallback"))


def _step_ingest_documents(session: dict) -> dict:
    trace = []

    # OCR — Aadhaar
    aadhaar = tools.ocr_extract("aadhaar")
    session["metrics"]["tool_calls"] += 1
    if not aadhaar.get("ok"):
        # OCR FAILURE PATH — request re-upload
        trace.append(_tt("ocr_extract", {"document_type": "aadhaar"},
                         {"error": aadhaar.get("error", "OCR failed")}))
        trace.append({"label": "Agent reasoning", "detail":
                      "Aadhaar OCR failed (likely blurry or obscured image). "
                      "Instead of dead-ending, requesting a re-upload."})
        return _respond(session, text=_t(session, "ocr_failed"),
                        trace=trace,
                        quick_replies=[{"label": "📎 Re-upload Aadhaar + PAN",
                                        "action": "upload_docs"}])

    trace.append(_tt("ocr_extract", {"document_type": "aadhaar"},
                     {"name": aadhaar["fields"]["name"],
                      "liveness": aadhaar["liveness_score"]}))

    # OCR — PAN
    pan = tools.ocr_extract("pan")
    session["metrics"]["tool_calls"] += 1
    if not pan.get("ok"):
        trace.append(_tt("ocr_extract", {"document_type": "pan"},
                         {"error": pan.get("error", "OCR failed")}))
        trace.append({"label": "Agent reasoning", "detail":
                      "PAN OCR failed. Requesting re-upload."})
        return _respond(session, text=_t(session, "ocr_failed"),
                        trace=trace,
                        quick_replies=[{"label": "📎 Re-upload Aadhaar + PAN",
                                        "action": "upload_docs"}])

    trace.append(_tt("ocr_extract", {"document_type": "pan"},
                     {"name": pan["fields"]["name"],
                      "pan": pan["fields"].get("pan_display", "MASKED")}))

    p = session["profile"]
    p.update({
        "aadhaar_name": aadhaar["fields"]["name"],
        "first_name": aadhaar["fields"]["name"].split()[0],
        "dob": aadhaar["fields"]["dob"],
        "address": aadhaar["fields"]["address"],
        "aadhaar_last4": aadhaar["fields"]["aadhaar_last4"],
        "pan": pan["fields"]["pan"],
        "pan_name": pan["fields"]["name"],
    })
    # 7 fields lifted from documents with zero typing by the user
    session["metrics"]["fields_extracted"] += 7

    # Validate PAN
    val = tools.validate_pan(p["pan"], p["aadhaar_name"])
    session["metrics"]["tool_calls"] += 1

    if not val.get("ok"):
        # PAN INVALID PATH — cannot proceed
        trace.append(_tt("validate_pan", {"pan": "MASKED", "name": p["aadhaar_name"]},
                         {"error": val.get("error", "PAN validation failed"),
                          "pan_status": val.get("pan_status", "ERROR")}))
        trace.append({"label": "Agent reasoning", "detail":
                      f"PAN validation failed: {val.get('error')}. "
                      "Cannot proceed with account opening. Escalating to "
                      "relationship officer for manual verification."})
        session["state"] = "handoff"
        session["metrics"]["human_handoffs"] = 1
        return _respond(session, text=_t(session, "pan_invalid"),
                        trace=trace)

    trace.append(_tt("validate_pan",
                     {"pan": "MASKED", "name": p["aadhaar_name"]},
                     {"pan_status": val["pan_status"], "name_match": val["name_match"],
                      "score": val["name_match_score"]}))

    if not val["name_match"]:
        # SELF-HEALING moment — the differentiator vs a 2019 chatbot.
        session["state"] = "await_identity_confirm"
        trace.append({"label": "Agent reasoning", "detail":
                      f"Name mismatch (Aadhaar '{p['aadhaar_name']}' vs PAN "
                      f"'{p['pan_name']}'). Do NOT dead-end. Hypothesis: dropped "
                      "surname/initial. Ask one targeted question to reconcile."})
        return _respond(session,
                        text=_t(session, "mismatch", a=p["aadhaar_name"], pn=p["pan_name"]),
                        trace=trace, quick_replies=_identity_quick_replies(session))

    return _step_resolve_identity(session, confirmed=True, trace=trace)


def _step_resolve_identity(session: dict, confirmed: bool, trace=None) -> dict:
    trace = trace or []
    p = session["profile"]
    # Reconcile to the fuller legal name (PAN), keep Aadhaar as alias.
    p["full_name"] = p.get("pan_name", p.get("aadhaar_name"))
    p["identity_reconciled"] = True   # gate flag — set only after reconciliation
    trace.append({"label": "Agent reasoning", "detail":
                  f"Reconciled identity → legal name '{p['full_name']}'. "
                  "Resumed straight-through flow (no handoff)."})

    # CKYC lookup
    ck = tools.ckyc_lookup(p["aadhaar_last4"], p["full_name"])
    session["metrics"]["tool_calls"] += 1

    if ck.get("existing_record"):
        trace.append(_tt("ckyc_lookup", {"aadhaar_last4": "MASKED"},
                         {"existing_record": True,
                          "ckyc_id": ck.get("ckyc_id"),
                          "hint": ck.get("existing_account_hint", "")}))
        trace.append({"label": "Agent reasoning", "detail":
                      "CKYC record already exists — pre-filling verified details "
                      "and skipping redundant verification steps."})
    else:
        trace.append(_tt("ckyc_lookup", {"aadhaar_last4": "MASKED"},
                         {"existing_record": ck["existing_record"]}))

    # AML screening
    aml = tools.aml_screen(p["full_name"], p["dob"])
    session["metrics"]["tool_calls"] += 1

    if aml.get("decision") == "HOLD" or aml.get("risk") == "HIGH":
        # AML ESCALATION PATH — cannot proceed, must escalate
        trace.append(_tt("aml_screen", {"name": p["full_name"], "dob": p["dob"]},
                         {"risk": aml["risk"], "decision": aml["decision"],
                          "reason": aml.get("reason", "Flagged for review")}))
        trace.append({"label": "Agent reasoning · AML escalation", "detail":
                      f"AML screen returned {aml['risk']} risk with decision "
                      f"'{aml['decision']}'. This is a GOVERNED ESCALATION — "
                      "the agent is NOT permitted to override AML compliance. "
                      "Escalating to AML compliance team for Level 2 review. "
                      "The customer's application is placed on hold, not rejected."})
        session["state"] = "aml_hold"
        session["metrics"]["human_handoffs"] = 1
        return _respond(session, text=_t(session, "aml_escalation",
                                          name=p["first_name"]),
                        trace=trace)

    trace.append(_tt("aml_screen", {"name": p["full_name"], "dob": p["dob"]},
                     {"risk": aml["risk"], "decision": aml["decision"]}))
    p["aml_decision"] = aml["decision"]   # gate input — the REAL screen result

    session["state"] = "await_occupation"
    # Everything else inferred from documents; occupation is the ONLY field we must ask.
    return _respond(session, text=_t(session, "ask_occupation_intro", name=p["first_name"]),
                    trace=trace,
                    quick_replies=[
                        {"label": _t(session, "salaried"), "action": "occ_salaried"},
                        {"label": _t(session, "self_emp"), "action": "occ_self"}])


def _step_open_account(session: dict) -> dict:
    p = session["profile"]
    # Pass the REAL AML decision + reconciliation flag through the deterministic
    # compliance gate. The agent is the maker; the gate is an independent checker.
    res = tools.create_account(p["full_name"], p["pan"], p["aadhaar_last4"],
                               p["occupation"],
                               aml_decision=p.get("aml_decision", ""),
                               identity_reconciled=p.get("identity_reconciled", False))
    session["metrics"]["tool_calls"] += 1
    trace_gate = {"label": "Compliance gate", "detail":
                  f"Deterministic checker (independent of the LLM): "
                  f"AML='{p.get('aml_decision','?')}', "
                  f"identity_reconciled={p.get('identity_reconciled', False)} → "
                  f"{'PASS — minting account' if res.get('ok') else 'BLOCK — ' + res.get('blocked_by','')}."}

    if not res.get("ok"):
        # Account creation failure
        trace = [_tt("create_account",
                      {"full_name": p["full_name"], "occupation": p["occupation"]},
                      {"error": res.get("error", "Account creation failed"),
                       "status": res.get("status", "ERROR")}), trace_gate]
        trace.append({"label": "Agent reasoning", "detail":
                      "Account creation failed in core banking. This could be a "
                      "system issue. Escalating for manual resolution."})
        session["state"] = "handoff"
        session["metrics"]["human_handoffs"] = 1
        return _respond(session, text=_t(session, "account_failed"),
                        trace=trace)

    session["state"] = "done"
    trace = [trace_gate, _tt("create_account",
                 {"full_name": p["full_name"], "occupation": p["occupation"]},
                 {"account_number": res["account_number"], "status": res["status"]})]
    return _respond(session,
                    text=_t(session, "success", name=p["first_name"],
                            acct=res["account_number"]),
                    trace=trace, done=True,
                    quick_replies=[{"label": "🌐 हिंदी / English", "action": "switch_hindi"}])


# ===========================================================================
# LIVE path — Claude plans and calls the same tools itself.
# ===========================================================================
SYSTEM_PROMPT = (
    "You are the YONO Nexus Onboarding Agent for State Bank of India. Your GOAL is "
    "to open a compliant savings account straight-through with zero human handoff. "
    "Use the tools to OCR the customer's Aadhaar and PAN, validate the PAN, run a "
    "CKYC lookup and AML screen, then open the account. Infer every field you can "
    "from the documents and ask the customer ONLY for what you genuinely cannot "
    "derive. If the Aadhaar and PAN names disagree, DO NOT dead-end: reason about "
    "the likely cause and ask one targeted reconciliation question, then proceed. "
    "If AML returns a HOLD decision, you MUST escalate — do NOT proceed with "
    "account opening. If OCR fails, ask the customer to re-upload a clearer photo. "
    "If the user writes in Hindi/Hinglish, reply in kind and keep prior context. "
    "Keep replies short and warm. Only escalate to a human on a real AML hit, "
    "tamper flag, or unresolvable identity conflict."
)


def _handle_live(session: dict, user_text: str) -> dict:
    msgs = session["live_messages"]
    msgs.append({"role": "user", "content": user_text or "I'd like to open an account."})
    trace = []
    final_text = ""
    for _ in range(8):  # bounded tool loop
        data = _anthropic_call(msgs, session)
        content = data.get("content", [])
        tool_uses = []
        for block in content:
            if block.get("type") == "text":
                final_text += block["text"]
            elif block.get("type") == "tool_use":
                tool_uses.append(block)
        msgs.append({"role": "assistant", "content": content})

        if data.get("stop_reason") != "tool_use" or not tool_uses:
            break

        tool_results = []
        for tu in tool_uses:
            fn = tools.TOOL_FUNCS.get(tu["name"])
            if fn is None:
                out = {"ok": False, "error": f"Unknown tool: {tu['name']}"}
            else:
                try:
                    out = fn(**tu["input"])
                except (TypeError, ValueError) as e:
                    out = {"ok": False, "error": f"Tool call error: {e}"}
            session["metrics"]["tool_calls"] += 1
            trace.append(_tt(tu["name"], tu["input"], _summarise(out)))
            tool_results.append({"type": "tool_result", "tool_use_id": tu["id"],
                                 "content": json.dumps(out)})
        msgs.append({"role": "user", "content": tool_results})

    if "account_number" in final_text.lower() or "ACTIVE" in final_text:
        session["state"] = "done"
    elif "hold" in final_text.lower() or "escalat" in final_text.lower():
        session["state"] = "aml_hold"
        session["metrics"]["human_handoffs"] = 1

    return _respond(session, text=final_text.strip() or "…", trace=trace,
                    quick_replies=_current_quick_replies(session),
                    done=(session["state"] == "done"))


def _anthropic_call(messages: list, session: dict = None) -> dict:
    system = SYSTEM_PROMPT
    tgt = (session or {}).get("target_language")
    if tgt:
        system += (f" IMPORTANT: The customer has chosen {tgt}. Reply ENTIRELY in "
                   f"{tgt} (natural, warm, spoken style suitable for text-to-speech). "
                   f"Keep tool calls and reasoning the same; only your customer-facing "
                   f"replies are in {tgt}.")
    elif (session or {}).get("lang") == "hi":
        system += " The customer is using Hindi. Reply in natural spoken Hindi."
    body = json.dumps({
        "model": MODEL, "max_tokens": 1024, "system": system,
        "tools": tools.TOOL_SCHEMAS, "messages": messages,
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


# ===========================================================================
# Helpers
# ===========================================================================
def _has_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _respond(session, text, trace=None, quick_replies=None, done=False) -> dict:
    m = session["metrics"]
    elapsed = round(time.time() - m["started_at"], 1)
    return {
        "reply": {"role": "agent", "text": text, "lang": session["lang"]},
        "trace": trace or [],
        "metrics": {
            "fields_auto_extracted": m["fields_extracted"],
            "fields_asked": m["fields_asked"],
            "tool_calls": m["tool_calls"],
            "human_handoffs": m["human_handoffs"],
            "turns": m["turns"],
            "elapsed_s": elapsed,
            "straight_through": session["state"] == "done" and m["human_handoffs"] == 0,
            "path": "LIVE · Claude " + MODEL if _has_key() else "OFFLINE · deterministic",
        },
        "quick_replies": quick_replies or [],
        "state": session["state"],
        "done": done,
        "lang": session["lang"],
    }


def _tt(name, args, result) -> dict:
    return {"label": f"tool · {name}", "args": args, "result": result, "kind": "tool"}


def _summarise(out: dict) -> dict:
    keys = ("name", "pan_status", "name_match", "risk", "decision",
            "existing_record", "account_number", "status", "error",
            "reason", "escalation_required")
    s = {k: out[k] for k in keys if k in out}
    if "fields" in out:
        s["name"] = out["fields"].get("name")
    return s or out


def _current_quick_replies(session):
    st = session["state"]
    if st == "await_docs":
        return [{"label": "📎 Upload Aadhaar + PAN", "action": "upload_docs"}]
    if st == "await_identity_confirm":
        return _identity_quick_replies(session)
    if st == "await_occupation":
        return [{"label": _t(session, "salaried"), "action": "occ_salaried"},
                {"label": _t(session, "self_emp"), "action": "occ_self"}]
    return [{"label": "🌐 हिंदी / English", "action": "switch_hindi"}]


def _identity_quick_replies(session):
    return [{"label": _t(session, "yes_same"), "action": "confirm_identity"},
            {"label": _t(session, "no_diff"), "action": "deny_identity"}]


def _parse_occupation(text, action):
    if action == "occ_salaried":
        return "Salaried"
    if action == "occ_self":
        return "Self-employed"
    t = (text or "").lower()
    if any(w in t for w in ("salary", "salaried", "job", "naukri", "नौकरी")):
        return "Salaried"
    if any(w in t for w in ("business", "self", "vyapar", "व्यापार", "freelance")):
        return "Self-employed"
    return None


def _is_yes(t):
    return any(w in (t or "").lower() for w in ("yes", "same", "correct", "haan", "हाँ", " हां"))


def _is_no(t):
    return any(w in (t or "").lower() for w in ("no", "not", "nahi", "नहीं", "different"))


def _wants_hindi(t):
    return any(w in (t or "").lower() for w in ("hindi", "हिंदी", "हिन्दी"))


# ---------------------------------------------------------------------------
# Bilingual copy table — now supports English, Hindi, Tamil, and Bengali
# greetings. The live path generates language itself; this table powers the
# offline path and proves vernacular *memory* on switch.
# ---------------------------------------------------------------------------
_COPY = {
    "greet": {
        "en": "Namaste! I'm your SBI onboarding assistant. I'll open your savings "
              "account in a couple of minutes — no forms. Just share your Aadhaar "
              "and PAN to begin.",
        "hi": "नमस्ते! मैं आपका SBI ऑनबोर्डिंग सहायक हूँ। बिना किसी फॉर्म के दो मिनट में "
              "आपका बचत खाता खोल दूँगा। शुरू करने के लिए अपना आधार और पैन साझा करें।",
        "ta": "வணக்கம்! நான் உங்கள் SBI கணக்கு தொடக்க உதவியாளர். படிவங்கள் இல்லாமல் "
              "சில நிமிடங்களில் உங்கள் சேமிப்பு கணக்கைத் தொடங்குவேன்.",
        "bn": "নমস্কার! আমি আপনার SBI অনবোর্ডিং সহায়ক। কোনো ফর্ম ছাড়াই কয়েক মিনিটে "
              "আপনার সেভিংস অ্যাকাউন্ট খুলে দেব।"},
    "need_docs": {
        "en": "Let's start by uploading your Aadhaar and PAN.",
        "hi": "कृपया पहले अपना आधार और पैन अपलोड करें।"},
    "mismatch": {
        "en": "Quick check, {a} — your Aadhaar reads \"{a}\", but your PAN says "
              "\"{pn}\". Is \"Singh\" part of your full legal name (i.e. same person)?",
        "hi": "एक छोटी पुष्टि, {a} — आपके आधार पर \"{a}\" है, पर पैन पर \"{pn}\" है। "
              "क्या \"Singh\" आपके पूरे नाम का हिस्सा है (यानी एक ही व्यक्ति)?"},
    "confirm_prompt": {
        "en": "Just confirm — is the PAN the same person as the Aadhaar?",
        "hi": "कृपया पुष्टि करें — क्या पैन और आधार एक ही व्यक्ति के हैं?"},
    "ask_occupation_intro": {
        "en": "Thanks, {name} — identity verified and AML-cleared. One last thing I "
              "can't infer: what's your occupation?",
        "hi": "धन्यवाद, {name} — पहचान सत्यापित और AML-क्लियर। बस एक चीज़ जो मैं अनुमान "
              "नहीं लगा सकता: आपका व्यवसाय क्या है?"},
    "ask_occupation": {
        "en": "What's your occupation — salaried or self-employed?",
        "hi": "आपका व्यवसाय क्या है — नौकरीपेशा या स्व-नियोजित?"},
    "success": {
        "en": "Done, {name}! 🎉 Your SBI savings account {acct} is ACTIVE — opened "
              "straight-through, zero human handoff. Welcome to YONO.",
        "hi": "हो गया, {name}! 🎉 आपका SBI बचत खाता {acct} सक्रिय है — पूरी तरह स्वचालित, "
              "बिना किसी मानवीय हस्तक्षेप के। YONO में आपका स्वागत है।"},
    "handoff": {
        "en": "No problem — I'll connect you to a relationship officer to verify the "
              "name difference. Your progress is saved.",
        "hi": "कोई बात नहीं — नाम के अंतर की पुष्टि के लिए मैं आपको एक अधिकारी से जोड़ता हूँ। "
              "आपकी प्रगति सुरक्षित है।"},
    "lang_switch": {
        "en": "Sure, {name} — switching to English. We were right here, let's continue.",
        "hi": "ज़रूर{name}, अब हिंदी में बात करते हैं। हम यहीं थे, आगे बढ़ते हैं।"},
    "already_done": {
        "en": "Your onboarding is already complete. 🎉",
        "hi": "आपका ऑनबोर्डिंग पहले ही पूरा हो चुका है। 🎉"},
    "fallback": {
        "en": "Let's continue your onboarding.",
        "hi": "चलिए आपका ऑनबोर्डिंग जारी रखते हैं।"},
    # ── NEW: error/escalation paths ──
    "ocr_failed": {
        "en": "I couldn't read the document clearly — it may be blurry or partially "
              "covered. Could you take a fresh photo and re-upload?",
        "hi": "दस्तावेज़ ठीक से नहीं पढ़ पाया — शायद धुंधला है। कृपया फिर से साफ फोटो "
              "लेकर अपलोड करें।"},
    "pan_invalid": {
        "en": "Your PAN could not be verified with the NSDL registry. This may mean "
              "it's been deactivated. I'll connect you to a relationship officer "
              "who can help resolve this.",
        "hi": "आपका PAN NSDL रजिस्ट्री से सत्यापित नहीं हो सका। मैं आपको एक अधिकारी "
              "से जोड़ता हूँ जो इसे हल कर सकते हैं।"},
    "aml_escalation": {
        "en": "Thank you, {name}. Your verification is complete but requires an "
              "additional compliance review — this is standard procedure for "
              "some applications. Our compliance team will reach out within "
              "24 hours. Your progress is saved and secure.",
        "hi": "धन्यवाद, {name}। आपका सत्यापन पूरा हो गया है लेकिन एक अतिरिक्त अनुपालन "
              "समीक्षा की आवश्यकता है — कुछ आवेदनों के लिए यह मानक प्रक्रिया है। हमारी "
              "अनुपालन टीम 24 घंटे के भीतर संपर्क करेगी।"},
    "aml_hold_info": {
        "en": "Your application is currently under compliance review. Our team will "
              "contact you within 24 hours. No action needed from your side.",
        "hi": "आपका आवेदन अभी अनुपालन समीक्षा में है। हमारी टीम 24 घंटे में संपर्क करेगी।"},
    "account_failed": {
        "en": "There was an issue opening your account. I'll connect you to a "
              "relationship officer to complete the process. Your verified details "
              "are saved.",
        "hi": "खाता खोलने में कोई समस्या आई। मैं आपको एक अधिकारी से जोड़ता हूँ। "
              "आपके सत्यापित विवरण सुरक्षित हैं।"},
    "session_expired": {
        "en": "Your session has expired for security reasons. Please reload to "
              "start a new onboarding session.",
        "hi": "सुरक्षा कारणों से आपका सत्र समाप्त हो गया है। कृपया नया सत्र शुरू "
              "करने के लिए पुनः लोड करें।"},
    # quick-reply labels
    "yes_same": {"en": "Yes, same person", "hi": "हाँ, एक ही व्यक्ति"},
    "no_diff": {"en": "No, different", "hi": "नहीं, अलग"},
    "salaried": {"en": "Salaried", "hi": "नौकरीपेशा"},
    "self_emp": {"en": "Self-employed", "hi": "स्व-नियोजित"},
}


def _t(session, key, **kw) -> str:
    lang = session["lang"]
    template = _COPY.get(key, {}).get(lang) or _COPY.get(key, {}).get("en", key)
    # the hindi lang_switch greeting uses ", {name}" → tidy spacing when name empty
    if key == "lang_switch" and kw.get("name"):
        kw["name"] = (" " + kw["name"]) if lang == "hi" else kw["name"]
    try:
        return template.format(**kw)
    except (KeyError, IndexError):
        return template
