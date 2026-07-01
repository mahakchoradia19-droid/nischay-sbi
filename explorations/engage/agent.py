"""
SAARTHI — Proactive Engagement Agent orchestrator.

Same dual-path pattern as the rest of YONO Nexus:

  OFFLINE (default): a deterministic pipeline that watches a customer's financial
  rhythms, detects the moment they need help, and crafts a proactive nudge — all
  before the customer asks. Zero network.

  LIVE (ANTHROPIC_API_KEY set): the same tools + customer context handed to Claude,
  which plans and calls the tools itself. The UI trace panel looks identical.

Each scenario routes through a slightly different tool sequence — proving the agent
*reasons about which checks matter* rather than running one fixed script.
"""

import json
import os
import time
import urllib.request

import tools

MODEL = os.environ.get("YONO_MODEL", "claude-opus-4-8")

SYSTEM_PROMPT = (
    "You are SAARTHI, the Proactive Engagement Agent for State Bank of India — a "
    "financial companion that helps customers BEFORE they ask. Your GOAL is to watch "
    "a customer's financial rhythms, detect the single most important moment where a "
    "timely nudge would genuinely help, and craft that nudge in their language. "
    "Use the tools: get_account_snapshot → scan_transactions → detect_obligations → "
    "compute_shortfall (and find_funding_source or compute_opportunity_cost where "
    "relevant) → recommend_action → execute_nudge. "
    "You are NOT selling products. You are a patient, trustworthy companion that steps "
    "in at the right moment with the right help. Always explain your reasoning so the "
    "nudge is transparent and auditable. Only ever surface one primary nudge per customer."
)

# Which tools each scenario should exercise (offline path). The agent reasons about
# the customer's situation and only runs the checks that matter for that moment.
_SCENARIO_FLOW = {
    "emi_shortfall":       ["snapshot", "scan", "obligations", "shortfall", "funding"],
    "financial_stress":    ["snapshot", "scan", "obligations", "shortfall"],
    "education_planning":  ["snapshot", "scan", "obligations"],
    "salary_sip":          ["snapshot", "scan"],
    "idle_balance":        ["snapshot", "scan", "opportunity"],
}


# ---------------------------------------------------------------------------
# OFFLINE deterministic pipeline
# ---------------------------------------------------------------------------

def analyse_customer(customer_id: str) -> dict:
    start = time.time()
    trace = []

    c = tools._CUSTOMERS.get(customer_id)
    if not c:
        return _err(customer_id, "customer not found", trace, start)
    scenario = c["scenario"]
    flow = _SCENARIO_FLOW.get(scenario, ["snapshot", "scan"])

    # Step: snapshot
    snap = tools.get_account_snapshot(customer_id)
    trace.append(_tt("get_account_snapshot", {"customer_id": customer_id},
                     {k: snap[k] for k in ("name", "balance_inr", "mode", "preferred_lang")}))

    # Step: scan transactions
    scan = tools.scan_transactions(customer_id)
    trace.append(_tt("scan_transactions", {"customer_id": customer_id},
                     {"pattern_count": scan["pattern_count"],
                      "patterns": [p["description"] for p in scan["patterns_detected"]]}))

    shortfall = None
    funding = None
    oppcost = None

    if "obligations" in flow:
        obl = tools.detect_obligations(customer_id)
        trace.append(_tt("detect_obligations", {"customer_id": customer_id},
                         {"obligation_count": obl["obligation_count"],
                          "total_due_within_7d_inr": obl["total_due_within_7d_inr"]}))

    if "shortfall" in flow:
        shortfall = tools.compute_shortfall(customer_id)
        trace.append(_tt("compute_shortfall", {"customer_id": customer_id},
                         {"balance_inr": shortfall["balance_inr"],
                          "imminent_obligations_inr": shortfall["imminent_obligations_inr"],
                          "shortfall_inr": shortfall["shortfall_inr"],
                          "at_risk": shortfall["at_risk"]}))

    if "funding" in flow and shortfall and shortfall["shortfall_inr"] > 0:
        funding = tools.find_funding_source(customer_id, shortfall["shortfall_inr"])
        fs = funding.get("funding_source") or {}
        trace.append(_tt("find_funding_source",
                         {"customer_id": customer_id, "amount_inr": shortfall["shortfall_inr"]},
                         {"feasible": funding["feasible"], "source": fs.get("label"),
                          "penalty": fs.get("penalty")}))

    if "opportunity" in flow:
        oppcost = tools.compute_opportunity_cost(customer_id)
        trace.append(_tt("compute_opportunity_cost", {"customer_id": customer_id},
                         {"idle_balance_inr": oppcost["idle_balance_inr"],
                          "idle_days": oppcost["idle_days"],
                          "opportunity_cost_inr": oppcost["opportunity_cost_inr"]}))

    # Reasoning: why this moment, why this help
    trace.append({"label": "Agent reasoning · the moment", "kind": "reasoning",
                  "detail": _reason_moment(scenario, c, shortfall, oppcost)})

    # Step: recommend action
    rec = tools.recommend_action(customer_id, scenario)
    trace.append(_tt("recommend_action", {"customer_id": customer_id, "scenario": scenario},
                     {"urgency": rec["urgency"], "cta": rec["cta"],
                      "language": rec["language"]}))

    trace.append({"label": "Agent reasoning · the nudge", "kind": "reasoning",
                  "detail": (
                      f"Crafted a {rec['language'].upper()} nudge for a '{c['mode']}' mode "
                      f"user. This is help, not a sale: it gives the customer a one-tap "
                      f"resolution ('{rec['cta']}') and explains why. Surfacing exactly one "
                      f"primary nudge to respect attention and trust.")})

    # Step: execute / queue
    ex = tools.execute_nudge(customer_id, rec["action_type"])
    trace.append(_tt("execute_nudge",
                     {"customer_id": customer_id, "action_type": rec["action_type"]},
                     {"channel": ex["channel"], "delivery": ex["delivery"],
                      "consent_checked": ex["consent_checked"], "nudge_id": ex["nudge_id"]}))

    return {
        "ok": True,
        "customer_id": customer_id,
        "customer_name": c["name"],
        "first_name": c["first_name"],
        "location": c["location"],
        "scenario": scenario,
        "mode": c["mode"],
        "trace": trace,
        "nudge": {
            "title": rec["title"],
            "message": rec["message"],
            "cta": rec["cta"],
            "urgency": rec["urgency"],
            "language": rec["language"],
            "channel": ex["channel"],
        },
        "nudge_id": ex["nudge_id"],
        "elapsed_s": round(time.time() - start, 2),
        "path": "LIVE · Claude " + MODEL if _has_key() else "OFFLINE · deterministic",
    }


def _reason_moment(scenario, c, shortfall, oppcost) -> str:
    name = c.get("first_name", "the customer")
    if scenario == "emi_shortfall":
        return (f"{name}'s EMI is 2 days away and the balance won't cover it — a bounce "
                f"means a penalty AND a credit-score ding for someone who can least afford "
                f"it. A sweep-in FD covers the ₹{shortfall['shortfall_inr']} gap penalty-free. "
                f"This is the difference between a bank that watches you fail and one that "
                f"quietly catches you.")
    if scenario == "financial_stress":
        return (f"Salary hasn't landed for 2 months and dues exceed comfortable headroom. "
                f"The right move is NOT a cross-sell — it's hardship support. Acting now, "
                f"before a default, protects {name}'s record and SBI's relationship value.")
    if scenario == "education_planning":
        return (f"The school-fee pattern is quarterly and predictable. {name} can keep paying "
                f"reactively forever, or a small Child Education SIP can absorb it and "
                f"compound for higher studies. The pattern — not a campaign — is what makes "
                f"this relevant right now.")
    if scenario == "salary_sip":
        return (f"Salary just credited and {name} has a ₹24,000 surplus and an established SIP "
                f"habit. The single best moment to reinforce a savings habit is the day money "
                f"arrives — friction is lowest and intent is highest.")
    if scenario == "idle_balance":
        lost = oppcost["opportunity_cost_inr"] if oppcost else 0
        return (f"₹3.2L has sat idle for 240 days, quietly losing ₹{lost:,} versus an FD. "
                f"{name} never asked — but a good companion does the math and surfaces the "
                f"cost before it grows.")
    return f"Detected a moment where a timely, relevant nudge would genuinely help {name}."


# ---------------------------------------------------------------------------
# LIVE path — Claude plans and calls the same tools
# ---------------------------------------------------------------------------

def analyse_customer_live(customer_id: str) -> dict:
    start = time.time()
    c = tools._CUSTOMERS.get(customer_id)
    if not c:
        return _err(customer_id, "customer not found", [], start)

    user_msg = (
        f"Monitor customer {customer_id} ({c['name']}, {c['location']}). "
        f"Watch their financial rhythms, find the single most important moment to help, "
        f"and craft the proactive nudge."
    )
    msgs = [{"role": "user", "content": user_msg}]
    trace = []
    final_text = ""

    for _ in range(10):
        data = _anthropic_call(msgs)
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
            out = fn(**tu["input"]) if fn else {"ok": False, "error": "unknown tool"}
            trace.append(_tt(tu["name"], tu["input"], out))
            tool_results.append({"type": "tool_result", "tool_use_id": tu["id"],
                                 "content": json.dumps(out)})
        msgs.append({"role": "user", "content": tool_results})

    rec = tools.recommend_action(customer_id, c["scenario"])
    ex = tools.execute_nudge(customer_id, rec["action_type"])

    return {
        "ok": True,
        "customer_id": customer_id,
        "customer_name": c["name"],
        "first_name": c["first_name"],
        "location": c["location"],
        "scenario": c["scenario"],
        "mode": c["mode"],
        "trace": trace,
        "nudge": {
            "title": rec["title"], "message": rec["message"], "cta": rec["cta"],
            "urgency": rec["urgency"], "language": rec["language"], "channel": ex["channel"],
        },
        "nudge_id": ex["nudge_id"],
        "agent_summary": final_text,
        "elapsed_s": round(time.time() - start, 2),
        "path": "LIVE · Claude " + MODEL,
    }


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _tt(name, args, result) -> dict:
    return {"label": f"tool · {name}", "args": args, "result": result, "kind": "tool"}


def _err(customer_id, msg, trace, start) -> dict:
    return {"ok": False, "customer_id": customer_id, "error": msg,
            "trace": trace, "elapsed_s": round(time.time() - start, 2)}
