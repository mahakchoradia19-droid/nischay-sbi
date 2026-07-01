// YONO Nexus — Voice Onboarding client.
// Agentic logic lives server-side (onboarding_agent.py). This client adds a
// real voice layer: Web Speech API for text-to-speech (the agent speaks) and
// speech recognition (it listens), plus real document capture with optional
// in-browser OCR. Degrades gracefully to text on browsers without the APIs.

let sessionId = null;
let voiceOn = true;
let uiLang = "en-IN";       // BCP-47 for TTS/STT
let uiCode = "en";          // backend language code (en/hi/…)
let listening = false;
let lastQuickReplies = [];
let expectingDocUpload = false;

const $ = (id) => document.getElementById(id);
const messagesEl = $("messages"), quickEl = $("quick"), traceEl = $("trace"),
      metricsEl = $("metrics"), stpEl = $("stp"), pathEl = $("path"),
      orbEl = $("orb"), orbStatus = $("orbStatus"), interimEl = $("interim"),
      micBtn = $("micBtn");

// ── Speech synthesis (TTS) ────────────────────────────────────────
const synth = window.speechSynthesis;
let voices = [];
function loadVoices() { voices = synth ? synth.getVoices() : []; }
if (synth) { loadVoices(); synth.onvoiceschanged = loadVoices; }

const _BCP47 = { en: "en-IN", hi: "hi-IN", ta: "ta-IN", bn: "bn-IN", mr: "mr-IN",
                 te: "te-IN", gu: "gu-IN", kn: "kn-IN", pa: "pa-IN" };
function codeToBCP47(code) {
  if (!code) return uiLang;
  if (code.includes("-")) return code;
  return _BCP47[code] || uiLang;
}

function pickVoice(lang) {
  if (!voices.length) loadVoices();
  const base = lang.split("-")[0];
  return voices.find(v => v.lang === lang) ||
         voices.find(v => v.lang && v.lang.startsWith(base)) ||
         voices.find(v => v.lang && v.lang.startsWith("en")) || null;
}

function speak(text, lang, onDone) {
  if (!voiceOn || !synth || !text) { onDone && onDone(); return; }
  synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang || uiLang;
  const v = pickVoice(u.lang);
  if (v) u.voice = v;
  u.rate = 0.98; u.pitch = 1.04;          // warm, unhurried — "airhostess" cadence
  setOrb("speaking", statusFor("speaking"));
  u.onend = () => { setOrb("idle", statusFor("idle")); onDone && onDone(); };
  u.onerror = () => { setOrb("idle", statusFor("idle")); onDone && onDone(); };
  synth.speak(u);
}

// ── Speech recognition (STT) ──────────────────────────────────────
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog = null;
if (SR) {
  recog = new SR();
  recog.interimResults = true;
  recog.maxAlternatives = 1;
  recog.continuous = false;

  recog.onresult = (e) => {
    let interim = "", final = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) final += t; else interim += t;
    }
    interimEl.textContent = interim ? "“" + interim + "…”" : "";
    if (final) {
      interimEl.textContent = "";
      stopListening();
      handleSpoken(final.trim());
    }
  };
  recog.onend = () => { if (listening) stopListening(); };
  recog.onerror = () => { stopListening(); };
} else {
  micBtn.disabled = true;
  micBtn.title = "Voice input not supported in this browser — type instead";
}

function startListening() {
  if (!recog || listening) return;
  if (synth) synth.cancel();
  recog.lang = uiLang;
  try { recog.start(); } catch (_) { return; }
  listening = true;
  micBtn.classList.add("active");
  setOrb("listening", statusFor("listening"));
}
function stopListening() {
  if (!recog) return;
  listening = false;
  micBtn.classList.remove("active");
  try { recog.stop(); } catch (_) {}
  if (orbEl.classList.contains("listening")) setOrb("idle", statusFor("idle"));
}

// When the user speaks, map it to a quick-reply action if it matches, else send as text.
function handleSpoken(text) {
  addMessage("user", text);
  const matched = matchQuickReply(text);
  if (matched) { renderQuick([]); sendAction(matched.action, matched.label); }
  else send({ text });
}

// Fuzzy-ish match of a spoken phrase to a visible quick-reply button.
function matchQuickReply(text) {
  const t = text.toLowerCase();
  for (const q of lastQuickReplies) {
    const label = (q.label || "").toLowerCase().replace(/[^\wऀ-ॿ\s]/g, "").trim();
    const words = label.split(/\s+/).filter(w => w.length > 2);
    if (label && (t.includes(label) || words.some(w => t.includes(w)))) return q;
    if (q.action === "upload_docs" && /(upload|aadhaar|pan|document|aadhar|kyc)/.test(t)) return q;
    if (q.action === "confirm_identity" && /(yes|same|correct|haan|sahi)/.test(t)) return q;
    if (q.action === "occ_salaried" && /(salar|job|naukri|employed)/.test(t)) return q;
    if (q.action === "occ_self" && /(business|self|vyapar|freelanc)/.test(t)) return q;
  }
  return null;
}

// ── Orb state ─────────────────────────────────────────────────────
function setOrb(state, status) {
  orbEl.className = "orb " + state;
  if (status != null) orbStatus.textContent = status;
}
function statusFor(state) {
  const offline = uiCode === "en" || uiCode === "hi";
  if (state === "speaking") return offline ? "🔊 Speaking…" : "🔊 Speaking (Live AI voice)…";
  if (state === "listening") return "🎤 Listening… speak now";
  return "Tap 🎤 to reply, or use the buttons";
}

// ── API ───────────────────────────────────────────────────────────
async function api(path, body) {
  const r = await fetch(path, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return r.json();
}

// ── Rendering ─────────────────────────────────────────────────────
function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = "msg " + role;
  el.textContent = text;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderQuick(replies) {
  lastQuickReplies = replies || [];
  quickEl.innerHTML = "";
  (replies || []).forEach((q) => {
    const b = document.createElement("button");
    b.textContent = q.label;
    b.onclick = () => {
      if (q.action === "upload_docs") return openDocCapture(q);
      renderQuick([]); sendAction(q.action, q.label);
    };
    quickEl.appendChild(b);
  });
}

function renderTrace(trace) {
  if (!trace || !trace.length) return;
  const empty = traceEl.querySelector(".trace-empty");
  if (empty) empty.remove();
  trace.forEach((t) => {
    const el = document.createElement("div");
    el.className = "trace-item" + (t.kind === "tool" ? " tool" : "");
    const label = document.createElement("div");
    label.className = "t-label"; label.textContent = t.label; el.appendChild(label);
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
  pathEl.classList.toggle("live", (m.path || "").startsWith("LIVE"));
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

// Apply a server response: render, then speak, then auto-listen if a reply is expected.
function apply(res, { autoListen = true } = {}) {
  const text = res.reply ? res.reply.text : "";
  if (text) addMessage("agent", text);
  renderTrace(res.trace);
  renderMetrics(res.metrics);
  const replies = res.quick_replies || [];
  expectingDocUpload = replies.some(q => q.action === "upload_docs");

  const speakLang = codeToBCP47((res.reply && res.reply.lang) || uiCode);
  speak(text, speakLang, () => {
    renderQuick(replies);
    // Auto-open the camera for the document step; otherwise auto-listen for a reply.
    if (!res.done && autoListen && replies.length && !expectingDocUpload) {
      setTimeout(startListening, 250);
    } else if (res.done) {
      setOrb("idle", "✓ All done — welcome to SBI!");
    } else {
      setOrb("idle", statusFor("idle"));
    }
  });
}

// ── Sending ───────────────────────────────────────────────────────
async function send({ text }) {
  renderQuick([]);
  const res = await api("/api/message", { session_id: sessionId, text, lang: uiCode });
  apply(res);
}
async function sendAction(action, label) {
  if (label) addMessage("user", label);
  const res = await api("/api/message", { session_id: sessionId, action, lang: uiCode });
  apply(res);
}

// ── Document capture (real camera / file) + optional in-browser OCR ──
function openDocCapture(q) {
  $("docInput").value = "";
  $("docInput").click();
}

$("docInput").addEventListener("change", async (e) => {
  const files = [...e.target.files].slice(0, 2);
  if (!files.length) return;
  const prev = $("docPreview");
  prev.hidden = false; prev.innerHTML = "";
  files.forEach(f => {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(f);
    prev.appendChild(img);
  });
  addMessage("user", "📎 " + files.map(f => f.name).join(", "));
  // Fire the agent step immediately (capture is real even if OCR is best-effort).
  sendAction("upload_docs", "");
  // Best-effort REAL OCR in the background — proves we read the actual image.
  runRealOCR(files[0]);
});

async function runRealOCR(file) {
  if (!file) return;
  try {
    if (!window.Tesseract) {
      await loadScript("https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js");
    }
    if (!window.Tesseract) return;   // offline — skip silently, flow already proceeded
    $("ocrOut").hidden = false;
    $("ocrText").textContent = "Reading the document…";
    const { data } = await window.Tesseract.recognize(file, "eng");
    const text = (data.text || "").trim();
    $("ocrText").textContent = text || "(no machine-readable text found in image)";
  } catch (_) {
    $("ocrOut").hidden = true;       // never let OCR break the demo
  }
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = src; s.onload = resolve; s.onerror = reject;
    document.head.appendChild(s);
    setTimeout(reject, 6000);        // give up fast if offline
  });
}

// ── Controls ──────────────────────────────────────────────────────
micBtn.onclick = () => { listening ? stopListening() : startListening(); };

$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const v = $("input").value.trim();
  if (!v) return;
  $("input").value = "";
  handleSpoken(v);
});

$("langSelect").addEventListener("change", (e) => {
  const opt = e.target.selectedOptions[0];
  uiLang = e.target.value;
  uiCode = opt.getAttribute("data-code");
  // Tell the backend which language to use (offline supports en/hi; live supports all).
  api("/api/message", { session_id: sessionId, action: "set_language", lang: uiCode })
    .then(res => { if (res && res.reply) apply(res, { autoListen: false }); });
});

$("voiceToggle").onclick = () => {
  voiceOn = !voiceOn;
  $("voiceToggle").textContent = voiceOn ? "🔊 Voice on" : "🔇 Voice off";
  $("voiceToggle").classList.toggle("on", voiceOn);
  $("voiceToggle").classList.toggle("off", !voiceOn);
  if (!voiceOn && synth) synth.cancel();
};

$("restart").onclick = start;

// ── Boot ──────────────────────────────────────────────────────────
async function start() {
  if (synth) synth.cancel();
  stopListening();
  messagesEl.innerHTML = "";
  traceEl.innerHTML = '<div class="trace-empty">Tool calls &amp; reasoning appear here as the journey runs.</div>';
  $("docPreview").hidden = true; $("docPreview").innerHTML = "";
  $("ocrOut").hidden = true;
  setOrb("idle", "Starting your onboarding…");
  const res = await api("/api/start", { lang: uiCode });
  sessionId = res.session_id;
  apply(res, { autoListen: false });
}

start();
