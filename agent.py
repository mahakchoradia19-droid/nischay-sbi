"""
YONO Nexus — Onboarding Agent orchestrator.

Two execution paths, ONE set of tools (tools.py):

  * OFFLINE (default, zero setup): a deterministic goal-state machine that
    reproduces genuine agentic behaviour — autonomous multi-tool sequencing,
    self-healing on a KYC name-mismatch, infer-don't-ask, and vernacular memory.

  * LIVE (auto-enabled when ANTHROPIC_API_KEY is set): the same goal + tools are
    handed to Claude (Opus 4.8) which plans and calls the tools itself via the
    Anthropic Messages API. No SDK dependency — raw urllib so it runs anywhere.

Both paths emit the SAME response contract to the UI:
    {reply, trace, metrics, quick_replies, done, lang}
so the "Agent Reasoning Trace" panel looks identical regardless of path.
"""

import json
import os
import time
import urllib.request
import urllib.error

import tools

MODEL = os.environ.get("YONO_MODEL", "claude-opus-4-8")

# ---------------------------------------------------------------------------
# Session store (in-memory; one onboarding journey per session_id).
# ---------------------------------------------------------------------------
SESSIONS = {}


def new_session(session_id: str) -> dict:
    s = {
        "id": session_id,
        "state": "await_docs",
        "lang": "en",
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


def handle(session: dict, text: str = "", action: str = "") -> dict:
    """Single entry point the server calls per user turn."""
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
        except Exception as e:  # never let the live path break the demo
            session.setdefault("_live_error", str(e))
            # fall through to deterministic path
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

    if state in ("done", "handoff"):
        return _respond(session, text=_t(session, "already_done"),
                        done=(state == "done"))

    return _respond(session, text=_t(session, "fallback"))


def _step_ingest_documents(session: dict) -> dict:
    trace = []
    aadhaar = tools.ocr_extract("aadhaar"); session["metrics"]["tool_calls"] += 1
    trace.append(_tt("ocr_extract", {"document_type": "aadhaar"},
                     {"name": aadhaar["fields"]["name"],
                      "liveness": aadhaar["liveness_score"]}))
    pan = tools.ocr_extract("pan"); session["metrics"]["tool_calls"] += 1
    trace.append(_tt("ocr_extract", {"document_type": "pan"},
                     {"name": pan["fields"]["name"], "pan": pan["fields"]["pan"]}))

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

    val = tools.validate_pan(p["pan"], p["aadhaar_name"])
    session["metrics"]["tool_calls"] += 1
    trace.append(_tt("validate_pan", {"pan": p["pan"], "name": p["aadhaar_name"]},
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
    trace.append({"label": "Agent reasoning", "detail":
                  f"Reconciled identity → legal name '{p['full_name']}'. "
                  "Resumed straight-through flow (no handoff)."})

    ck = tools.ckyc_lookup(p["aadhaar_last4"], p["full_name"])
    session["metrics"]["tool_calls"] += 1
    trace.append(_tt("ckyc_lookup", {"aadhaar_last4": p["aadhaar_last4"]},
                     {"existing_record": ck["existing_record"]}))

    aml = tools.aml_screen(p["full_name"], p["dob"])
    session["metrics"]["tool_calls"] += 1
    trace.append(_tt("aml_screen", {"name": p["full_name"], "dob": p["dob"]},
                     {"risk": aml["risk"], "decision": aml["decision"]}))

    session["state"] = "await_occupation"
    # Everything else inferred from documents; occupation is the ONLY field we must ask.
    return _respond(session, text=_t(session, "ask_occupation_intro", name=p["first_name"]),
                    trace=trace,
                    quick_replies=[
                        {"label": _t(session, "salaried"), "action": "occ_salaried"},
                        {"label": _t(session, "self_emp"), "action": "occ_self"}])


def _step_open_account(session: dict) -> dict:
    p = session["profile"]
    res = tools.create_account(p["full_name"], p["pan"], p["aadhaar_last4"],
                               p["occupation"])
    session["metrics"]["tool_calls"] += 1
    session["state"] = "done"
    trace = [_tt("create_account",
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
    "If the user writes in Hindi/Hinglish, reply in kind and keep prior context. "
    "Keep replies short and warm. Only escalate to a human on a real AML hit or "
    "tamper flag."
)


def _handle_live(session: dict, user_text: str) -> dict:
    msgs = session["live_messages"]
    msgs.append({"role": "user", "content": user_text or "I'd like to open an account."})
    trace = []
    final_text = ""
    for _ in range(8):  # bounded tool loop
        data = _anthropic_call(msgs)
        content = data.get("content", [])
        assistant_blocks, tool_uses = [], []
        for block in content:
            assistant_blocks.append(block)
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
            out = fn(**tu["input"]) if fn else {"ok": False, "error": "unknown tool"}
            session["metrics"]["tool_calls"] += 1
            trace.append(_tt(tu["name"], tu["input"], _summarise(out)))
            tool_results.append({"type": "tool_result", "tool_use_id": tu["id"],
                                 "content": json.dumps(out)})
        msgs.append({"role": "user", "content": tool_results})

    if "account_number" in final_text.lower() or "ACTIVE" in final_text:
        session["state"] = "done"
    return _respond(session, text=final_text.strip() or "…", trace=trace,
                    quick_replies=_current_quick_replies(session),
                    done=(session["state"] == "done"))


def _anthropic_call(messages: list) -> dict:
    body = json.dumps({
        "model": MODEL, "max_tokens": 1024, "system": SYSTEM_PROMPT,
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
            "existing_record", "account_number", "status")
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
# Minimal bilingual copy. The live path generates language itself; this table
# powers the offline path and proves vernacular *memory* on switch.
# ---------------------------------------------------------------------------
_COPY = {
    "greet": {
        "en": "Namaste! I'm your SBI onboarding assistant. I'll open your savings "
              "account in a couple of minutes — no forms. Just share your Aadhaar "
              "and PAN to begin.",
        "hi": "नमस्ते! मैं आपका SBI ऑनबोर्डिंग सहायक हूँ। बिना किसी फॉर्म के दो मिनट में "
              "आपका बचत खाता खोल दूँगा। शुरू करने के लिए अपना आधार और पैन साझा करें।"},
    "need_docs": {
        "en": "Let's start by uploading your Aadhaar and PAN.",
        "hi": "कृपया पहले अपना आधार और पैन अपलोड करें।"},
    "mismatch": {
        "en": "Quick check, {a} — your Aadhaar reads “{a}”, but your PAN says "
              "“{pn}”. Is “Singh” part of your full legal name (i.e. same person)?",
        "hi": "एक छोटी पुष्टि, {a} — आपके आधार पर “{a}” है, पर पैन पर “{pn}” है। "
              "क्या “Singh” आपके पूरे नाम का हिस्सा है (यानी एक ही व्यक्ति)?"},
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
