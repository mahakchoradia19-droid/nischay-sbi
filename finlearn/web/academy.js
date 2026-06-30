// FinSmart Academy — voice-led learning client.
// Real teaching content + procedurally-generated fresh questions come from the
// server; the voice tutor (TTS) speaks lessons, questions and explanations in
// the learner's language. Mastery & XP persist in localStorage.

const $ = (id) => document.getElementById(id);
const api = (path, body) => fetch(path, {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body || {}),
}).then(r => r.json());

let uiLang = "en-IN", uiCode = "en", voiceOn = true;
let curriculum = [];
let current = { module: null, lesson: null, quizConcepts: [], q: null };
let score = 0, streak = 0;

// progress persisted locally
const store = JSON.parse(localStorage.getItem("finacademy") || "{}");
store.xp = store.xp || 0;
store.mastery = store.mastery || {};      // concept -> {seen, correct}
store.doneLessons = store.doneLessons || {};
const save = () => localStorage.setItem("finacademy", JSON.stringify(store));

const LEVELS = [0, 100, 250, 500, 900, 1500, 2400, 3600, 5200, 7200];
function levelOf(xp) { let l = 1; for (let i = 0; i < LEVELS.length; i++) if (xp >= LEVELS[i]) l = i + 1; return l; }

// ── voice ─────────────────────────────────────────────────────────
const synth = window.speechSynthesis;
let voices = [];
const loadVoices = () => { voices = synth ? synth.getVoices() : []; };
if (synth) { loadVoices(); synth.onvoiceschanged = loadVoices; }
const _BCP = { en:"en-IN",hi:"hi-IN",ta:"ta-IN",bn:"bn-IN",mr:"mr-IN",te:"te-IN",gu:"gu-IN",kn:"kn-IN",pa:"pa-IN" };
const toBCP = (c) => (c && c.includes("-")) ? c : (_BCP[c] || uiLang);

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
  showTutor(text);
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang || uiLang;
  const v = pickVoice(u.lang); if (v) u.voice = v;
  u.rate = 0.97; u.pitch = 1.05;
  setTutorOrb("speaking");
  u.onend = () => { setTutorOrb("idle"); onDone && onDone(); };
  u.onerror = () => { setTutorOrb("idle"); onDone && onDone(); };
  synth.speak(u);
}
function stopSpeak() { if (synth) synth.cancel(); setTutorOrb("idle"); }

function showTutor(text) {
  $("tutorFab").hidden = false;
  $("tutorSay").textContent = text.length > 140 ? text.slice(0, 140) + "…" : text;
}
function setTutorOrb(state) { $("tutorOrb").className = "tutor-orb " + state; }

// ── navigation ────────────────────────────────────────────────────
function show(viewId) {
  ["viewModules", "viewLessons", "viewLesson", "viewQuiz"].forEach(v => $(v).hidden = (v !== viewId));
  window.scrollTo(0, 0);
}

// ── boot ──────────────────────────────────────────────────────────
async function boot() {
  renderXP();
  const data = await api("/api/academy/curriculum", {});
  curriculum = data.modules || [];
  const pill = $("aiPill");
  if (data.ai_active) { pill.textContent = "AI Active · Gemini"; pill.classList.remove("offline"); }
  else { pill.textContent = "Offline ready"; pill.classList.add("offline"); }
  renderModules();
  maybeDeepLink();   // arrive from a FinPulse dimension → open that exact lesson
}

// Deep-link: #<lesson_id> (e.g. from FinPulse "Learn this") opens & teaches it.
function maybeDeepLink() {
  const lid = (location.hash || "").replace(/^#/, "");
  if (!lid) return;
  const mod = curriculum.find(m => (m.lessons || []).some(l => l.id === lid));
  if (!mod) return;
  current.module = mod;       // so the Back button works
  openLesson(lid);
}
window.addEventListener("hashchange", maybeDeepLink);

function renderModules() {
  const grid = $("moduleGrid"); grid.innerHTML = "";
  curriculum.forEach(m => {
    const el = document.createElement("div");
    el.className = "module";
    el.onclick = () => openModule(m.id);
    el.innerHTML = `<div class="m-ico">${m.icon}</div>
      <div class="m-title">${m.title}</div>
      <div class="m-blurb">${m.blurb}</div>
      <div class="m-count">${m.lesson_count} lessons →</div>`;
    grid.appendChild(el);
  });
  show("viewModules");
}

function openModule(mid) {
  const m = curriculum.find(x => x.id === mid);
  current.module = m;
  $("lessonsHead").innerHTML = `<div class="lh-ico">${m.icon}</div>
    <div><h2>${m.title}</h2><p>${m.blurb}</p></div>`;
  const list = $("lessonList"); list.innerHTML = "";
  m.lessons.forEach(l => {
    const el = document.createElement("div");
    el.className = "lesson-row" + (store.doneLessons[l.id] ? " done" : "");
    el.onclick = () => openLesson(l.id);
    el.innerHTML = `<div class="lr-ico">${l.icon}</div>
      <div><div class="lr-title">${l.title}</div><div class="lr-sum">${l.summary}</div></div>
      <div class="lr-min">${l.minutes} min</div>`;
    list.appendChild(el);
  });
  show("viewLessons");
}

async function openLesson(lid) {
  stopSpeak();
  const data = await api("/api/academy/lesson", { lesson_id: lid, lang: uiCode });
  const l = data.lesson; current.lesson = l; current.tutor = data.tutor;
  current.quizConcepts = l.concepts;
  $("lessonTitle").textContent = `${l.icon}  ${l.title}`;
  $("lessonSummary").textContent = l.summary;
  $("keyPoints").innerHTML = l.key_points.map(k => `<li>${k}</li>`).join("");
  $("worked").textContent = l.worked_example;
  show("viewLesson");
  // auto-offer the voice teaching
  teachCurrent();
}

function teachCurrent() {
  const t = current.tutor;
  if (!t) return;
  $("teachBtn").classList.add("speaking");
  $("teachBtn").textContent = "🔊 Teaching…";
  speak(t.text, toBCP(t.lang), () => {
    $("teachBtn").classList.remove("speaking");
    $("teachBtn").textContent = "🔊 Teach me again";
  });
  // mark lesson visited
  if (!store.doneLessons[current.lesson.id]) {
    store.doneLessons[current.lesson.id] = true; store.xp += 15; renderXP(); save();
  }
}

// ── quiz ──────────────────────────────────────────────────────────
function startQuiz(concepts, label) {
  current.quizConcepts = concepts && concepts.length ? concepts : null;
  $("quizModuleName").textContent = label || "Practice";
  score = 0; streak = 0; updateScore();
  show("viewQuiz");
  nextQuestion();
}

// adaptive: prefer the learner's weakest concept among the set
function pickConcept() {
  const pool = current.quizConcepts;
  if (!pool || !pool.length) return null;
  let worst = pool[0], worstRate = 2;
  pool.forEach(c => {
    const m = store.mastery[c] || { seen: 0, correct: 0 };
    const rate = m.seen ? m.correct / m.seen : 0.0;   // unseen → prioritised
    if (rate < worstRate) { worstRate = rate; worst = c; }
  });
  return worst;
}

async function nextQuestion() {
  stopSpeak();
  $("qFeedback").hidden = true; $("qActions").hidden = true;
  const concept = pickConcept();
  const data = await api("/api/academy/generate", { concept, lang: uiCode });
  const q = data.question; current.q = q;
  $("qConcept").textContent = (q.concept || "").replace(/_/g, " ");
  $("qComputed").textContent = q.computed === false ? "fresh" : "fresh · computed";
  $("qStem").textContent = q.stem;
  const opts = $("qOptions"); opts.innerHTML = "";
  q.options.forEach((o, i) => {
    const b = document.createElement("button");
    b.className = "q-opt"; b.textContent = o;
    b.onclick = () => answer(i, b);
    opts.appendChild(b);
  });
  // tutor reads the question aloud
  speak(q.stem, toBCP(uiCode));
}

function answer(i, btn) {
  const q = current.q;
  const correct = i === q.answer;
  [...$("qOptions").children].forEach((b, idx) => {
    b.disabled = true;
    if (idx === q.answer) b.classList.add("correct");
    else if (idx === i) b.classList.add("wrong");
  });
  // mastery + score
  const m = store.mastery[q.concept] || { seen: 0, correct: 0 };
  m.seen++; if (correct) m.correct++;
  store.mastery[q.concept] = m;
  if (correct) {
    streak++; const gain = 10 + Math.min(streak, 5) * 2;
    score += gain; store.xp += gain;
  } else { streak = 0; }
  save(); updateScore(); renderXP();

  const fb = $("qFeedback");
  fb.hidden = false;
  fb.className = "q-feedback " + (correct ? "good" : "bad");
  fb.innerHTML = (correct ? "✅ <b>Correct!</b> " : "💡 <b>Not quite.</b> ") + q.explanation;
  $("qActions").hidden = false;
  // tutor speaks the explanation — the teachable moment
  speak((correct ? "Correct! " : "Not quite. ") + q.explanation, toBCP(uiCode));
}

function updateScore() { $("quizScore").textContent = score; $("quizStreak").textContent = streak; }
function renderXP() {
  const lvl = levelOf(store.xp);
  $("xpLevel").textContent = "Lvl " + lvl;
  const lo = LEVELS[lvl - 1] || 0, hi = LEVELS[lvl] || (lo + 2000);
  $("xpFill").style.width = Math.min(100, ((store.xp - lo) / (hi - lo)) * 100) + "%";
}

// ── controls ──────────────────────────────────────────────────────
document.querySelectorAll("[data-to]").forEach(b => b.onclick = () => show(b.dataset.to));
$("lessonBack").onclick = () => { stopSpeak(); openModule(current.module.id); };
$("quizBack").onclick = () => { stopSpeak(); current.lesson ? show("viewLesson") : show("viewModules"); };
$("teachBtn").onclick = teachCurrent;
$("practiceBtn").onclick = () => startQuiz(current.quizConcepts, current.lesson.title);
$("qNext").onclick = nextQuestion;
$("qListen").onclick = () => current.q && speak(current.q.stem, toBCP(uiCode));
$("tutorStop").onclick = stopSpeak;

$("langSelect").addEventListener("change", (e) => {
  const opt = e.target.selectedOptions[0];
  uiLang = e.target.value; uiCode = opt.getAttribute("data-code");
  // re-fetch the current lesson's tutor text in the new language
  if (!$("viewLesson").hidden && current.lesson) {
    api("/api/academy/tutor", { lesson_id: current.lesson.id, lang: uiCode })
      .then(d => { current.tutor = d.tutor; teachCurrent(); });
  }
});
$("voiceToggle").onclick = () => {
  voiceOn = !voiceOn;
  $("voiceToggle").textContent = voiceOn ? "🔊 Voice on" : "🔇 Voice off";
  $("voiceToggle").classList.toggle("on", voiceOn);
  $("voiceToggle").classList.toggle("off", !voiceOn);
  if (!voiceOn) stopSpeak();
};

boot();
