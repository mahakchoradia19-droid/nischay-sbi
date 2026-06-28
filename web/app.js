// YONO Nexus demo — thin client. All agentic logic lives server-side (agent.py).
let sessionId = null;

const $ = (id) => document.getElementById(id);
const messagesEl = $("messages"), quickEl = $("quick"), traceEl = $("trace"),
      metricsEl = $("metrics"), stpEl = $("stp"), pathEl = $("path");

async function api(path, body) {
  const r = await fetch(path, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return r.json();
}

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = "msg " + role;
  el.textContent = text;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderQuick(replies) {
  quickEl.innerHTML = "";
  (replies || []).forEach((q) => {
    const b = document.createElement("button");
    b.textContent = q.label;
    b.onclick = () => send({ action: q.action, label: q.label });
    quickEl.appendChild(b);
  });
}

function renderTrace(trace) {
  if (!trace || !trace.length) return;
  trace.forEach((t) => {
    const el = document.createElement("div");
    el.className = "trace-item" + (t.kind === "tool" ? " tool" : "");
    const label = document.createElement("div");
    label.className = "t-label";
    label.textContent = t.label;
    el.appendChild(label);
    if (t.detail) {
      const d = document.createElement("div");
      d.className = "t-detail"; d.textContent = t.detail; el.appendChild(d);
    }
    if (t.kind === "tool") {
      const io = document.createElement("div");
      io.className = "t-io";
      io.textContent = "→ " + JSON.stringify(t.args) + "\n← " + JSON.stringify(t.result);
      el.appendChild(io);
    }
    traceEl.appendChild(el);
  });
  traceEl.scrollTop = traceEl.scrollHeight;
}

function renderMetrics(m) {
  if (!m) return;
  pathEl.textContent = m.path;
  pathEl.classList.toggle("live", m.path.startsWith("LIVE"));
  const cells = [
    [m.fields_auto_extracted, "Fields auto-extracted"],
    [m.fields_asked, "Fields asked of user"],
    [m.tool_calls, "Autonomous tool calls"],
    [m.human_handoffs, "Human handoffs"],
    [m.turns, "Conversation turns"],
    [m.elapsed_s + "s", "Time elapsed"],
  ];
  metricsEl.innerHTML = cells.map(([v, l]) =>
    `<div class="metric"><div class="m-val">${v}</div><div class="m-lbl">${l}</div></div>`
  ).join("");
  if (m.straight_through) {
    stpEl.className = "stp go";
    stpEl.textContent = "✓ STRAIGHT-THROUGH · zero human handoff";
  } else {
    stpEl.className = "stp pending";
    stpEl.textContent = "● Onboarding in progress…";
  }
}

function apply(res) {
  if (res.reply) addMessage("agent", res.reply.text);
  renderTrace(res.trace);
  renderQuick(res.quick_replies);
  renderMetrics(res.metrics);
}

async function send({ text, action, label }) {
  addMessage("user", label || text);
  renderQuick([]);
  const res = await api("/api/message", { session_id: sessionId, text, action });
  apply(res);
}

async function start() {
  messagesEl.innerHTML = ""; traceEl.innerHTML = "";
  const res = await api("/api/start", {});
  sessionId = res.session_id;
  if (!res.trace || !res.trace.length)
    traceEl.innerHTML = '<div class="trace-empty">Tool calls and agent reasoning appear here as the journey runs.</div>';
  apply(res);
}

$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const v = $("input").value.trim();
  if (!v) return;
  $("input").value = "";
  send({ text: v });
});
$("restart").onclick = start;

start();
