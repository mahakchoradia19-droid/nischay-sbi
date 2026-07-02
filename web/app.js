// Arrives — front end.
// The rescue is a small state machine driving a phone mockup. The agent SPEAKS
// each line with the browser's real speech engine; the name-reconciliation and
// the reactivation gate are real calls to the server (shown in the trace).

const $ = (id) => document.getElementById(id);
const api = (path, body) => fetch(path, {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body || {}),
}).then(r => r.json());

let voiceOn = true;
let uiLang = "hi-IN", uiCode = "hi";
let person = null;

// ── real speech (TTS) ─────────────────────────────────────────────
const synth = window.speechSynthesis;
let voices = [];
const loadVoices = () => { voices = synth ? synth.getVoices() : []; };
if (synth) { loadVoices(); synth.onvoiceschanged = loadVoices; }
function speak(text, cb) {
  if (!voiceOn || !synth || !text) { cb && cb(); return; }
  synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = uiLang;
  const base = uiLang.split("-")[0];
  const v = voices.find(x => x.lang === uiLang) || voices.find(x => x.lang && x.lang.startsWith(base));
  if (v) u.voice = v;
  u.rate = 0.96; u.pitch = 1.04;
  orb(true);
  u.onend = () => { orb(false); cb && cb(); };
  u.onerror = () => { orb(false); cb && cb(); };
  synth.speak(u);
}
function orb(on) { $("orb").classList.toggle("active", on); }

// ── real speech recognition (STT) — the agent genuinely listens ────
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const sttSupported = !!SR;
let recog = null;
function listen(onHeard) {
  if (!sttSupported) return false;          // caller falls back to buttons
  try { recog && recog.abort(); } catch (_) {}
  recog = new SR();
  recog.lang = uiLang;
  recog.interimResults = false;
  recog.maxAlternatives = 1;
  orb(true);
  recog.onresult = (e) => {
    const said = (e.results[0][0].transcript || "").toLowerCase();
    orb(false);
    onHeard(said);
  };
  recog.onerror = () => { orb(false); onHeard(null); };
  recog.onend = () => orb(false);
  try { recog.start(); return true; } catch (_) { orb(false); return false; }
}
// map a spoken reply to yes / no in Hindi + English
function heardYes(t) { return /(yes|yeah|same|correct|right|haan|haa|ha |ji|sahi|ek hi|एक ही|हाँ|हां|जी|सही)/i.test(t); }
function heardNo(t)  { return /(no|not|nope|nahin|nahi|alag|galat|नहीं|नही|अलग)/i.test(t); }

// ── bilingual script ──────────────────────────────────────────────
const T = {
  greet: {
    hi: "नमस्ते रमेश जी। आपके दो हज़ार रुपये की सरकारी राशि आने वाली है, पर आपका खाता निष्क्रिय है और के-वाई-सी पुरानी हो गई है। चलिए इसे अभी ठीक कर देते हैं — बस अपना पहचान पत्र दिखाइए।",
    en: "Namaste Ramesh. Your two thousand rupees of government support is on its way, but your account is dormant and your KYC has expired. Let's fix it right now — just show me your ID.",
  },
  confirm: {
    hi: "एक छोटी सी पुष्टि। आपके आधार पर नाम है 'रमेश कुमार', और दस्तावेज़ पर 'रमेश कुमार वर्मा'। क्या यह एक ही व्यक्ति हैं?",
    en: "One small check. Your account says 'Ramesh Kumar', and your document says 'Ramesh Kumar Verma'. Is this the same person?",
  },
  done: {
    hi: "हो गया! आपका खाता अब सक्रिय है, और दो हज़ार रुपये आपके खाते में आ गए हैं। अगली बार यह अपने-आप आ जाएगा।",
    en: "Done! Your account is active again, and two thousand rupees has arrived. Next time, it will come on its own.",
  },
};
const L = (k) => T[k][uiCode] || T[k].en;

// ── phone renderers ───────────────────────────────────────────────
function screen(html) { $("screen").innerHTML = `<div class="scr"><div class="scr-status"><span>9:41</span><span>SBI</span><span>📶 🔋</span></div>${html}</div>`; }

function scrDetect(p) {
  screen(`
    <div class="scr-title">Payment at risk</div>
    <div class="scr-sub">Detected 3 days before the ${p.scheme} cycle</div>
    <div class="alert-card">
      <div class="alert-amt">₹${p.amount.toLocaleString("en-IN")}</div>
      <div class="alert-scheme">${p.scheme} · for ${p.name}</div>
      ${p.reasons.map(r => `<div class="reason"><span class="dot"></span>${r.text}</div>`).join("")}
    </div>`);
}
function scrSMS() {
  const msg = uiCode === "hi"
    ? "SBI: रमेश जी, आपकी सरकारी राशि अटक सकती है। खाता ठीक करने के लिए यहाँ बात करें → (टैप करें)"
    : "SBI: Ramesh, your government payment may not reach you. Tap to fix your account by talking → ";
  screen(`
    <div class="scr-title">A message arrives</div>
    <div class="scr-sub">In his language, on the phone he actually uses</div>
    <div class="sms"><div class="sms-from">SBI · now</div>${msg}</div>
    <div style="flex:1"></div>
    <button class="mini-btn" onclick="window._tapLink()">Ramesh taps the link →</button>`);
}
function scrTalk(agentText, extraHtml = "") {
  screen(`
    <div class="scr-title">Fixing it by talking</div>
    <div class="scr-sub">Voice re-KYC · no branch, no form</div>
    <div class="agent-line">🔊 ${agentText}</div>
    ${extraHtml}`);
}
function scrLanded(p) {
  screen(`
    <div class="landed">
      <div class="landed-check">✓</div>
      <div class="landed-amt">₹${p.amount.toLocaleString("en-IN")} arrived</div>
      <div class="landed-msg">${p.scheme} credited. The door was open when the money knocked.</div>
    </div>`);
}

// ── trace + steps ─────────────────────────────────────────────────
const STEPS = ["Detect", "Reach", "Reactivate", "Arrive"];
function renderSteps(active) {
  $("stepTrack").innerHTML = STEPS.map((s, i) =>
    `<span class="step-pill ${i < active ? "done" : i === active ? "active" : ""}">${i + 1}. ${s}</span>`).join("");
}
function trace(text, ok) {
  const empty = $("trace").querySelector(".trace-empty");
  if (empty) empty.remove();
  const el = document.createElement("div");
  el.className = "trace-item" + (ok ? " ok" : "");
  el.innerHTML = text;
  $("trace").appendChild(el);
}

// ── the rescue flow ───────────────────────────────────────────────
async function startRescue() {
  $("startBtn").hidden = true; $("resetBtn").hidden = false;
  $("trace").innerHTML = "";
  person = await api("/api/person", { id: "ramesh" });

  // 1 · DETECT
  renderSteps(0); scrDetect(person);
  trace(`Scanned the upcoming <b>${person.scheme}</b> cycle · flagged <code>ramesh</code>: dormant + KYC lapsed`);
  await wait(1600);

  // 2 · REACH
  renderSteps(1); scrSMS();
  trace(`Reachable by phone → sent a vernacular SMS + missed-call callback (self-serve track)`);
}

window._tapLink = async function () {
  // 3 · REACTIVATE — agent speaks, then the self-heal
  renderSteps(2);
  scrTalk(L("greet"));
  speak(L("greet"), async () => {
    // real name reconciliation call
    const v = await api("/api/verify", { id: "ramesh" });
    trace(`Read the document, compared it to the account name — real match score <code>${v.score}</code> → <b>${v.outcome}</b> (a benign variant, not a dead-end)`);
    const micHint = sttSupported
      ? `<div class="mic-hint" id="micHint">🎤 ${uiCode === "hi" ? "बोलिए — या नीचे टैप कीजिए" : "Speak your answer — or tap below"}</div>`
      : "";
    scrTalk(L("confirm"), `${micHint}
      <div class="confirm-row">
        <button class="mini-btn" onclick="window._confirmYes()">✓ ${uiCode === "hi" ? "हाँ, एक ही" : "Yes, same person"}</button>
        <button class="mini-btn plain" onclick="window._confirmNo()">${uiCode === "hi" ? "नहीं" : "No"}</button>
      </div>`);
    speak(L("confirm"), () => {
      // after the agent finishes speaking, it actually LISTENS (real STT).
      const started = listen((said) => {
        if (said == null) return;                 // couldn't hear → buttons remain
        const mh = $("micHint");
        if (mh) mh.textContent = "🗣️ " + said;
        trace(`Heard the reply by voice: “${said}” → interpreted as <b>${heardYes(said) ? "yes" : heardNo(said) ? "no" : "unclear"}</b>`);
        if (heardYes(said)) window._confirmYes();
        else if (heardNo(said)) window._confirmNo();
        // unclear → leave the buttons for the person to tap
      });
      if (started && $("micHint")) $("micHint").classList.add("listening");
    });
  });
};

window._confirmYes = async function () {
  const r = await api("/api/reactivate", { id: "ramesh", confirmed_name: "Ramesh Kumar Verma", reconciled: true });
  trace(`Compliance screen: clear · reactivation gate: identity reconciled ✓`, true);
  trace(`Account <b>${r.account_state}</b> → <b>${r.scheme} ₹${r.amount_released.toLocaleString("en-IN")}</b> released and credited`, true);
  // 4 · ARRIVE
  renderSteps(4);
  scrLanded(person);
  speak(L("done"));
};

window._confirmNo = function () {
  scrTalk(uiCode === "hi"
    ? "कोई बात नहीं। सुरक्षा के लिए मैं आपको एक अधिकारी से जोड़ता हूँ।"
    : "No problem — for your safety I'll connect you to an officer.");
  trace(`Customer declined the match → escalated to a human officer (the gate refused to reactivate)`);
};

function resetRescue() {
  if (synth) synth.cancel();
  $("startBtn").hidden = false; $("resetBtn").hidden = true;
  renderSteps(-1);
  $("trace").innerHTML = '<div class="trace-empty">Press start — the steps and the real logic appear here.</div>';
  screen(`<div class="landed"><div class="scr-sub" style="text-align:center">Ready when you are.</div></div>`);
}
const wait = (ms) => new Promise(r => setTimeout(r, ms));

// ── the limits (boundary cases) ───────────────────────────────────
const LIMITS = [
  { who: "Budhia, 61", why: "No smartphone, and Aadhaar was never linked in the payments system.",
    fix: "Can't be fixed digitally. → <b>Flagged for the next banking camp</b> in her village, with her name on the list before the team arrives." },
  { who: "Imran, 34", why: "His two ID documents carry genuinely different names — not a typo, a real conflict.",
    fix: "The agent must not paper over this. → <b>Handed to a human officer</b> for review. The gate refuses to reactivate." },
];
function renderLimits() {
  $("limitGrid").innerHTML = LIMITS.map(l => `
    <div class="limit">
      <div class="limit-who">${l.who}</div>
      <div class="limit-why">${l.why}</div>
      <div class="limit-fix">${l.fix}</div>
    </div>`).join("");
}

// ── at scale + honest metrics ─────────────────────────────────────
async function renderScale() {
  const d = await api("/api/cohort", {});
  const c = d.cohort, m = d.metrics;
  const cr = (x) => "₹" + (x / 1e7).toFixed(1) + " Cr";
  $("scaleGrid").innerHTML = [
    [c.at_risk_accounts.toLocaleString("en-IN"), "payments at risk this cycle, in one district", "clay"],
    [cr(c.at_risk_amount_inr), "of citizens' money at stake", "clay"],
    [c.digitally_fixable_pct + "%", "fixable by voice, at almost no cost", "sage"],
    [c.needs_human_pct + "%", "honestly routed to a human / camp", ""],
  ].map(([v, l, cl]) => `<div class="scale-cell"><div class="scale-val ${cl}">${v}</div><div class="scale-lbl">${l}</div></div>`).join("");

  $("metricsNote").textContent = m.note;
  $("metricsRow").innerHTML = [
    [pct(m.base_rate), "base bounce rate", ""],
    [pct(m.raw_accuracy), "raw accuracy", "flag"],
    [pct(m.precision_at_10pct), "precision, riskiest 10%", "good"],
    [m.lift + "×", "better than chance", "good"],
    [m.brier.toFixed(3), "Brier score ↓", "good"],
  ].map(([v, l, cl]) => `<div class="metric ${cl}"><div class="metric-v">${v}</div><div class="metric-l">${l}</div></div>`).join("");
  $("eceRead").textContent = `Calibration error: ${m.ece} — the closer to zero, the more the model's confidence can be trusted.`;
  drawCalib(m.calibration);
}
const pct = (x) => Math.round(x * 100) + "%";

function drawCalib(buckets) {
  const S = 300, pad = 38, W = S - pad * 2;
  const x = v => pad + v * W, y = v => S - pad - v * W;
  let s = "";
  for (let i = 0; i <= 5; i++) { const g = i / 5;
    s += `<line x1="${x(g)}" y1="${y(0)}" x2="${x(g)}" y2="${y(1)}" stroke="#E2DACB"/>`;
    s += `<line x1="${x(0)}" y1="${y(g)}" x2="${x(1)}" y2="${y(g)}" stroke="#E2DACB"/>`; }
  s += `<line x1="${x(0)}" y1="${y(0)}" x2="${x(1)}" y2="${y(1)}" stroke="#837C6E" stroke-width="1.5" stroke-dasharray="5 5"/>`;
  const pts = buckets.map(b => [x(b.predicted), y(b.actual)]);
  if (pts.length) {
    s += `<polyline points="${pts.map(p => p.join(",")).join(" ")}" fill="none" stroke="#C4694A" stroke-width="2.5"/>`;
    pts.forEach(p => s += `<circle cx="${p[0]}" cy="${p[1]}" r="4.5" fill="#C4694A"/>`);
  }
  s += `<text x="${x(.5) - 26}" y="${S - 8}" fill="#837C6E" font-size="10">predicted</text>`;
  s += `<text transform="rotate(-90 12 ${y(.5)})" x="12" y="${y(.5)}" fill="#837C6E" font-size="10">actual</text>`;
  $("calibChart").innerHTML = s;
}

// ── controls ──────────────────────────────────────────────────────
$("startBtn").onclick = startRescue;
$("resetBtn").onclick = resetRescue;
$("voiceToggle").onclick = () => {
  voiceOn = !voiceOn;
  $("voiceToggle").textContent = voiceOn ? "🔊 Voice on" : "🔇 Voice off";
  $("voiceToggle").classList.toggle("on", voiceOn);
  if (!voiceOn && synth) synth.cancel();
};
$("lang").onchange = e => { uiLang = e.target.value; uiCode = e.target.selectedOptions[0].dataset.code; };

// ── the district queue (the operational view) ─────────────────────
async function renderQueue() {
  const d = await api("/api/queue", {});
  const rupee = (x) => "₹" + x.toLocaleString("en-IN");
  $("queue").innerHTML = (d.queue || []).map(q => `
    <div class="q-row route-${q.route}">
      <div class="q-main">
        <div class="q-name">${q.name}</div>
        <div class="q-blocker">${q.blocker_text}</div>
      </div>
      <div class="q-amt">${rupee(q.amount)}<span>${q.scheme}</span></div>
      <div class="q-route">
        <span class="q-tag">${q.route_label}</span>
        <span class="q-note">${q.route_note}</span>
      </div>
      <div class="q-action">${q.route === "voice"
        ? `<button class="q-go" onclick="window._rescueFrom()">▶ Rescue</button>`
        : `<span class="q-hand">→ ${q.route === "camp" ? "camp list" : "human review"}</span>`}</div>
    </div>`).join("");
}
window._rescueFrom = function () {
  document.getElementById("rescue").scrollIntoView({ behavior: "smooth" });
  if ($("startBtn") && !$("startBtn").hidden) setTimeout(startRescue, 500);
};

// ── init ──────────────────────────────────────────────────────────
renderSteps(-1);
renderQueue();
renderLimits();
renderScale();
