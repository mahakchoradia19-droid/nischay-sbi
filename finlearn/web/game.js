// FinSmart Arena — game engine
// All game logic, state, animations, and API calls live here.

// ══════════════════════════════════════════════════════
//  STATE
// ══════════════════════════════════════════════════════
const LEVEL_THRESHOLDS = [0,200,500,1000,2000,3500,5500,8000,12000,18000,25000];
const LEVEL_TITLES = ["Rookie","Saver","Smart Saver","Investor","Wealth Builder",
  "Finance Pro","Money Mentor","Banking Expert","FinSmart Master","YONO Legend","SBI Champion"];
const AVATARS = ["🎮","📚","💡","🌱","💼","📈","🏆","🌟","👑","🔥","⚡"];

let P = loadPlayer();   // persistent player
let G = {};             // ephemeral game state
let cyberTimer = null;
let advisorClaimed = false;

function loadPlayer() {
  try {
    const saved = localStorage.getItem("fimsmart_player");
    if (saved) return JSON.parse(saved);
  } catch(e) {}
  return {
    coins: 0, xp: 0, level: 1, streak: 0, badges: [],
    gamesCompleted: [], highScores: {},
    seenConcepts: [], name: "Player",
  };
}
function savePlayer() {
  localStorage.setItem("fimsmart_player", JSON.stringify(P));
}

// ══════════════════════════════════════════════════════
//  NAVIGATION
// ══════════════════════════════════════════════════════
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById("screen-" + id).classList.add("active");
}

function goHub() {
  if (cyberTimer) { clearInterval(cyberTimer); cyberTimer = null; }
  showScreen("hub");
  renderHub();
}

// ══════════════════════════════════════════════════════
//  HUB
// ══════════════════════════════════════════════════════
function renderHub() {
  // player card
  document.getElementById("player-name").textContent = P.name;
  const lvl = Math.min(P.level - 1, LEVEL_TITLES.length - 1);
  document.getElementById("player-level").textContent = `Level ${P.level} · ${LEVEL_TITLES[lvl]}`;
  document.getElementById("player-avatar").textContent = AVATARS[Math.min(P.level-1, AVATARS.length-1)];
  document.getElementById("coin-count").textContent = P.coins.toLocaleString();

  const lo = LEVEL_THRESHOLDS[P.level - 1] || 0;
  const hi = LEVEL_THRESHOLDS[P.level] || lo + 500;
  const pct = Math.min(100, ((P.xp - lo) / (hi - lo)) * 100);
  document.getElementById("xp-bar").style.width = pct + "%";
  document.getElementById("xp-label").textContent = `${P.xp.toLocaleString()} / ${hi.toLocaleString()} XP`;

  // badges
  const br = document.getElementById("badges-row");
  if (P.badges.length === 0) {
    br.innerHTML = '<span class="badge-empty">Complete games to earn badges</span>';
  } else {
    br.innerHTML = P.badges.map(b =>
      `<span class="badge-chip" style="color:${b.color};border-color:${b.color}20;background:${b.color}12">${b.name}</span>`
    ).join("");
  }

  // game progress bars
  ["interest","cyber","cards"].forEach(g => {
    const hs = P.highScores[g];
    const total = g === "cards" ? 8 : 12;
    const pct = hs ? Math.min(100, (hs.correct / total) * 100) : 0;
    document.getElementById("prog-" + g).style.width = pct + "%";
  });
  document.getElementById("prog-advisor").style.width =
    P.gamesCompleted.includes("advisor") ? "100%" : "0%";

  // status
  fetch("/api/status", {method:"POST",body:"{}"}).then(r=>r.json()).then(s=>{
    const pill = document.getElementById("ai-pill");
    if (s.ai_active) {
      pill.textContent = "⚡ AI Active · Gemini 2.0 Flash";
      pill.className = "ai-pill live";
    } else {
      pill.textContent = "⚡ Offline Mode · Set GEMINI_API_KEY for AI";
      pill.className = "ai-pill offline";
    }
    document.getElementById("status-line").textContent =
      `${s.total_questions} questions · ${s.badges} badges to collect`;
  }).catch(()=>{});
}

// ══════════════════════════════════════════════════════
//  QUIZ GAME (Interest Island + Card Clash)
// ══════════════════════════════════════════════════════
async function startGame(type) {
  G = { type, questions: [], idx: 0, correct: 0, coinsEarned: 0, streak: 0 };

  const endpoint = type === "interest" ? "/api/questions/interest"
    : type === "cards" ? "/api/questions/cards" : null;

  if (type === "cyber") { startCyberGame(); return; }
  if (type === "advisor") { startAdvisor(); return; }

  const data = await api(endpoint, {});
  G.questions = type === "interest" ? data.questions : data.questions;

  document.getElementById("quiz-title").textContent =
    type === "interest" ? "Interest Island 🏝️" : "Card Clash 💳";
  showScreen("quiz");
  renderQuestion();
}

function renderQuestion() {
  const q = G.questions[G.idx];
  if (!q) { endQuiz(); return; }

  const total = G.questions.length;
  document.getElementById("q-counter").textContent = `Q ${G.idx + 1} / ${total}`;
  document.getElementById("quiz-progress-fill").style.width = ((G.idx / total) * 100) + "%";
  document.getElementById("hud-streak").textContent = "🔥 " + G.streak;
  document.getElementById("hud-coins-q").textContent = G.coinsEarned;
  document.getElementById("feedback-box").classList.add("hidden");

  // question card
  document.getElementById("concept-chip").textContent = q.concept || q.scenario?.goal || "Scenario";
  const isCardQ = G.type === "cards";
  if (isCardQ) {
    const s = q.scenario;
    document.getElementById("question-text").innerHTML =
      `<strong>${s.persona}</strong><br><br>${s.situation}<br><br><em>Goal: ${s.goal}</em>`;
  } else {
    document.getElementById("question-text").textContent = q.q;
  }

  // options
  const grid = document.getElementById("options-grid");
  const opts = isCardQ ? q.opts.map(o => `${o.card} — ${o.detail}`) : q.opts;
  grid.innerHTML = opts.map((o, i) =>
    `<button class="opt-btn" onclick="submitAnswer(${i})" id="opt-${i}">
      <span class="opt-letter">${String.fromCharCode(65+i)}</span>
      <span>${o}</span>
    </button>`
  ).join("");
}

async function submitAnswer(chosen) {
  const q = G.questions[G.idx];
  document.querySelectorAll(".opt-btn").forEach(b => b.disabled = true);

  const correct = chosen === q.ans;
  document.getElementById(`opt-${chosen}`).classList.add(correct ? "correct" : "wrong");
  if (!correct) document.getElementById(`opt-${q.ans}`).classList.add("correct");

  // streak + coins
  let baseCoins = G.type === "interest" ? 50 : 75;
  if (correct) {
    G.streak++;
    G.correct++;
    if (G.streak === 5) { awardBadge("streak_5"); }
    const multiplier = Math.min(G.streak, 3);
    const earned = baseCoins * multiplier;
    G.coinsEarned += earned;
    addCoins(earned, multiplier > 1 ? ` (${multiplier}× streak!)` : "");
    addXP(30);
    P.seenConcepts.push(q.concept || "");
  } else {
    G.streak = 0;
  }
  P.streak = G.streak;

  // feedback
  let explain = q.explain;
  if (!correct && Math.random() < 0.4) {
    // try to get AI explanation (silently falls back)
    const opts = G.type === "cards" ? q.opts.map(o=>o.card) : q.opts;
    try {
      const r = await api("/api/explain", {
        question: q.q || q.scenario?.situation || "",
        wrong: opts[chosen] || "",
        correct: opts[q.ans] || "",
        concept: q.concept || "",
      });
      if (r.explanation) explain = r.explanation;
    } catch(e) {}
  }

  const fb = document.getElementById("feedback-box");
  document.getElementById("feedback-result").innerHTML =
    correct ? "✅ Correct! " + (G.streak > 1 ? `🔥 ${G.streak} in a row!` : "")
             : "❌ Not quite";
  document.getElementById("feedback-explain").textContent = explain;
  if (G.type === "cards" && q.watchout) {
    document.getElementById("feedback-explain").textContent += "\n\n⚠️ " + q.watchout;
  }
  fb.classList.remove("hidden");
  document.getElementById("hud-streak").textContent = "🔥 " + G.streak;
}

function nextQuestion() {
  G.idx++;
  renderQuestion();
}

function endQuiz() {
  const total = G.questions.length;
  const acc = Math.round((G.correct / total) * 100);
  const perfect = G.correct === total;

  if (perfect) {
    awardBadge(G.type === "interest" ? "interest_perfect" : "cards_perfect");
  }
  if (!P.gamesCompleted.includes(G.type)) P.gamesCompleted.push(G.type);
  P.highScores[G.type] = { correct: G.correct, total, coins: G.coinsEarned };

  checkAllGames();
  showResults(G.type, G.correct, total, G.coinsEarned, acc);
}

// ══════════════════════════════════════════════════════
//  CYBER SHIELD
// ══════════════════════════════════════════════════════
async function startCyberGame() {
  G = { type: "cyber", scenarios: [], idx: 0, correct: 0, coinsEarned: 0, streak: 0 };
  const data = await api("/api/questions/cyber", {});
  G.scenarios = data.scenarios;

  // try to append 1 AI-generated scenario at the end
  try {
    const ai = await api("/api/scenario/ai", {});
    if (ai.scenario && ai.ai) G.scenarios.push(ai.scenario);
  } catch(e) {}

  showScreen("cyber");
  renderCyber();
}

function renderCyber() {
  const s = G.scenarios[G.idx];
  if (!s) { endCyber(); return; }

  document.getElementById("cyber-progress-fill").style.width =
    ((G.idx / G.scenarios.length) * 100) + "%";
  document.getElementById("cyber-streak").textContent = "🔥 " + G.streak;
  document.getElementById("cyber-coins").textContent = G.coinsEarned;
  document.getElementById("cyber-feedback").classList.add("hidden");
  document.querySelectorAll(".swipe-btn").forEach(b => b.disabled = false);

  document.getElementById("msg-type-tag").textContent =
    (s.type || "message").toUpperCase() + (s.ai_generated ? " · ✨ AI" : "");
  document.getElementById("msg-from").textContent = s.content.from || "Unknown";
  document.getElementById("msg-body").textContent = s.content.body || "";

  startTimer();
}

function startTimer() {
  if (cyberTimer) clearInterval(cyberTimer);
  const bar = document.getElementById("timer-bar");
  const txt = document.getElementById("timer-text");
  let t = 10;
  bar.style.transition = "none";
  bar.style.width = "100%";
  txt.textContent = "10s";
  setTimeout(() => {
    bar.style.transition = `width ${t}s linear`;
    bar.style.width = "0%";
  }, 50);
  cyberTimer = setInterval(() => {
    t--;
    txt.textContent = t + "s";
    if (t <= 3) bar.style.background = "linear-gradient(90deg,var(--red),#fca5a5)";
    else bar.style.background = "linear-gradient(90deg,var(--green),#86efac)";
    if (t <= 0) {
      clearInterval(cyberTimer);
      cyberVerdict("timeout");
    }
  }, 1000);
}

function cyberVerdict(verdict) {
  if (cyberTimer) { clearInterval(cyberTimer); cyberTimer = null; }
  document.querySelectorAll(".swipe-btn").forEach(b => b.disabled = true);

  const s = G.scenarios[G.idx];
  const correct = verdict === s.verdict;
  const timeout = verdict === "timeout";

  if (correct) {
    G.streak++;
    G.correct++;
    if (G.streak === 5) awardBadge("streak_5");
    const multiplier = Math.min(G.streak, 4);
    const earned = 100 * multiplier;
    G.coinsEarned += earned;
    addCoins(earned, multiplier > 1 ? ` (${multiplier}× streak!)` : "");
    addXP(40);
  } else {
    G.streak = 0;
  }

  const fb = document.getElementById("cyber-feedback");
  const cfResult = document.getElementById("cf-result");
  if (timeout) cfResult.innerHTML = "⏰ Time's up! It was a <strong>" + s.verdict.toUpperCase() + "</strong>";
  else if (correct) cfResult.innerHTML = s.verdict === "scam" ? "🛡️ Correct — that was a SCAM!" : "✅ Correct — that was SAFE!";
  else cfResult.innerHTML = s.verdict === "scam" ? "😬 That was a SCAM — don't be caught out!" : "⚠️ That was actually SAFE — learn to recognise the difference!";

  // red flags
  const flagsEl = document.getElementById("cf-flags");
  if (s.red_flags && s.red_flags.length) {
    flagsEl.innerHTML = s.red_flags.map(f => `<span class="flag-chip">⚑ ${f}</span>`).join("");
  } else {
    flagsEl.innerHTML = '<span class="flag-chip" style="background:rgba(34,197,94,.1);color:#86efac;border-color:rgba(34,197,94,.2)">✓ No red flags — genuine message</span>';
  }
  document.getElementById("cf-explain").textContent = s.explain || "";
  document.getElementById("cf-tip").textContent = "💡 " + (s.tip || "Always verify through official SBI channels.");

  fb.classList.remove("hidden");
  document.getElementById("cyber-streak").textContent = "🔥 " + G.streak;
}

function nextCyber() {
  G.idx++;
  renderCyber();
}

function endCyber() {
  const total = G.scenarios.length;
  const acc = Math.round((G.correct / total) * 100);
  if (G.correct === total) awardBadge("cyber_perfect");
  if (!P.gamesCompleted.includes("cyber")) P.gamesCompleted.push("cyber");
  P.highScores.cyber = { correct: G.correct, total, coins: G.coinsEarned };
  checkAllGames();
  showResults("cyber", G.correct, total, G.coinsEarned, acc);
}

// ══════════════════════════════════════════════════════
//  WEALTH WIZARD (Advisor)
// ══════════════════════════════════════════════════════
function startAdvisor() {
  advisorClaimed = false;
  document.getElementById("advisor-setup").classList.remove("hidden");
  document.getElementById("advisor-results").classList.add("hidden");
  showScreen("advisor");
  updateOppCost();

  document.getElementById("adv-amount").addEventListener("input", updateOppCost);
  document.getElementById("adv-months").addEventListener("input", updateOppCost);
}

function updateOppCost() {
  const amount = parseInt(document.getElementById("adv-amount").value) || 0;
  const months = parseInt(document.getElementById("adv-months").value) || 0;
  const opp = amount * (7.0 - 3.5) / 100 * months / 12;
  document.getElementById("idle-display").textContent = amount.toLocaleString("en-IN");
  document.getElementById("opp-counter").textContent = Math.round(opp).toLocaleString("en-IN");
}

async function getAdvice() {
  const profile = {
    age: parseInt(document.getElementById("adv-age").value) || 28,
    amount: parseInt(document.getElementById("adv-amount").value) || 100000,
    months: parseInt(document.getElementById("adv-months").value) || 8,
    rate: 3.5,
    risk: document.getElementById("adv-risk").value,
    goals: [document.getElementById("adv-goal").value],
  };

  document.querySelector(".cta-btn").textContent = "🤖 Thinking…";
  document.querySelector(".cta-btn").disabled = true;

  const result = await api("/api/advisor", profile);

  document.getElementById("adv-opp-val").textContent =
    "₹" + Math.round(result.opp_cost).toLocaleString("en-IN");
  document.getElementById("adv-text").textContent = result.advice;
  document.getElementById("advisor-ai-pill").textContent = result.ai ? "⚡ Gemini AI" : "⚡ Expert System";

  // Render option cards
  const optEl = document.getElementById("options-compare");
  optEl.innerHTML = result.static_options.map((o, i) =>
    `<div class="option-row">
      <div class="option-icon">${o.icon}</div>
      <div class="option-details">
        <div class="option-name">${o.name}</div>
        <div class="option-rate">${o.rate}% p.a.</div>
        <div class="option-lock">${o.lock} · ${o.risk} risk</div>
        <div class="option-why">${o.why}</div>
      </div>
      <div class="option-rank">${["🥇","🥈","🥉","4️⃣"][i] || ""}</div>
    </div>`
  ).join("");

  document.getElementById("advisor-setup").classList.add("hidden");
  document.getElementById("advisor-results").classList.remove("hidden");
  document.querySelector(".cta-btn").textContent = "✅ Claim 200 coins & badge";
  document.querySelector(".cta-btn").disabled = false;
}

function claimAdvisor() {
  if (advisorClaimed) return;
  advisorClaimed = true;
  addCoins(200, " from Wealth Wizard");
  addXP(100);
  awardBadge("advisor_done");
  if (!P.gamesCompleted.includes("advisor")) P.gamesCompleted.push("advisor");
  checkAllGames();
  savePlayer();
  showResults("advisor", 1, 1, 200, 100);
}

function resetAdvisor() {
  document.getElementById("advisor-setup").classList.remove("hidden");
  document.getElementById("advisor-results").classList.add("hidden");
}

// ══════════════════════════════════════════════════════
//  RESULTS
// ══════════════════════════════════════════════════════
function showResults(type, correct, total, coins, acc) {
  savePlayer();
  const emojis = { interest:"🏝️", cyber:"🛡️", cards:"💳", advisor:"💰" };
  const perfect = correct === total;
  document.getElementById("results-emoji").textContent =
    perfect ? "🏆" : acc >= 70 ? emojis[type] || "⭐" : "📚";
  document.getElementById("results-title").textContent =
    perfect ? "Perfect Score!" : acc >= 70 ? "Great job!" : "Keep practising!";
  document.getElementById("results-coins").textContent = coins.toLocaleString();
  document.getElementById("results-accuracy").textContent = acc + "%";

  // new badges earned this session
  const nb = document.getElementById("new-badges");
  nb.innerHTML = P.badges.slice(-3).map(b =>
    `<span class="badge-chip" style="color:${b.color};border-color:${b.color}20;background:${b.color}12">${b.name}</span>`
  ).join("") || "";

  G.lastType = type;
  showScreen("results");
}

function replayGame() { startGame(G.lastType || "interest"); }

// ══════════════════════════════════════════════════════
//  PLAYER ENGINE
// ══════════════════════════════════════════════════════
function addCoins(n, label = "") {
  P.coins += n;
  // toast
  const t = document.getElementById("coin-toast");
  t.textContent = "+" + n + " 🪙" + label;
  t.classList.remove("hidden");
  setTimeout(() => t.classList.add("hidden"), 2200);
}

function addXP(n) {
  const prevLevel = P.level;
  P.xp += n;
  // recompute level
  for (let i = LEVEL_THRESHOLDS.length - 1; i >= 0; i--) {
    if (P.xp >= LEVEL_THRESHOLDS[i]) { P.level = i + 1; break; }
  }
  P.level = Math.max(1, Math.min(P.level, LEVEL_THRESHOLDS.length));
  if (P.level > prevLevel) showLevelUp();
  if (P.level === 1 && prevLevel === 1 && P.xp === n) {
    // first ever XP — award first_play
    awardBadge("first_play");
  }
}

function showLevelUp() {
  const lvl = Math.min(P.level - 1, LEVEL_TITLES.length - 1);
  document.getElementById("lu-text").textContent =
    `Level ${P.level} — ${LEVEL_TITLES[lvl]}`;
  document.getElementById("levelup-overlay").classList.remove("hidden");
}
function closeLevelUp() {
  document.getElementById("levelup-overlay").classList.add("hidden");
}

const BADGE_DEFS = {
  interest_perfect: { name:"Compound King 👑", desc:"Perfect score in Interest Island", color:"#f59e0b" },
  cyber_perfect:    { name:"PhishBuster Pro 🛡️", desc:"Perfect score in Cyber Shield", color:"#3b82f6" },
  cards_perfect:    { name:"Card Wizard 💳", desc:"Perfect score in Card Clash", color:"#8b5cf6" },
  advisor_done:     { name:"Money Grower 🌱", desc:"Completed Wealth Wizard", color:"#22c55e" },
  streak_5:         { name:"On Fire 🔥", desc:"5-answer streak", color:"#ef4444" },
  all_games:        { name:"FinSmart Legend 🏆", desc:"All 4 games completed", color:"#ffd700" },
  first_play:       { name:"Welcome to FinSmart 🎉", desc:"Started your journey", color:"#6366f1" },
  speed_demon:      { name:"Speed Demon ⚡", desc:"Blazing fast answer", color:"#06b6d4" },
};

function awardBadge(id) {
  if (P.badges.some(b => b.id === id)) return;
  const def = BADGE_DEFS[id];
  if (!def) return;
  const badge = { id, ...def };
  P.badges.push(badge);
  savePlayer();

  // popup
  const popup = document.getElementById("badge-popup");
  document.getElementById("bp-inner").innerHTML =
    `<div class="bp-icon">${def.name.split(" ").pop()}</div>
     <div class="bp-name">Badge Unlocked!</div>
     <div class="bp-desc">${def.name}<br><small>${def.desc}</small></div>
     <button onclick="document.getElementById('badge-popup').classList.add('hidden')"
       style="background:${def.color};color:#fff;border:none;border-radius:10px;padding:10px 24px;font-weight:700;cursor:pointer;margin-top:4px">
       Awesome!
     </button>`;
  popup.classList.remove("hidden");
}

function checkAllGames() {
  const required = ["interest", "cyber", "cards", "advisor"];
  if (required.every(g => P.gamesCompleted.includes(g))) {
    awardBadge("all_games");
  }
}

// ══════════════════════════════════════════════════════
//  UTILS
// ══════════════════════════════════════════════════════
async function api(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

function resetProgress() {
  if (!confirm("Reset all progress and badges?")) return;
  localStorage.removeItem("fimsmart_player");
  P = loadPlayer();
  renderHub();
}

// ══════════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════════
renderHub();
// First-play detection
if (P.xp === 0 && P.coins === 0) {
  setTimeout(() => awardBadge("first_play"), 800);
}
