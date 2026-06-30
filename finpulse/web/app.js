// FinPulse — Money Health Score client.
// Renders a transparent, computed score (no hardcoded headline number) plus the
// self-evaluation "Honest Metrics" panel with a real calibration chart.

const $ = (id) => document.getElementById(id);
const api = (path, body) => fetch(path, {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body || {}),
}).then(r => r.json());

const GRADE_COLOR = { A: "#22c55e", B: "#84cc16", C: "#f5a623", D: "#fb923c", E: "#ef4444" };
const ACADEMY = (concept) => `http://localhost:8001/academy.html#${concept}`;
let activeId = null;
let lastResult = null;

// ── boot ──────────────────────────────────────────────────────────
async function boot() {
  const data = await api("/api/cohort", {});
  renderCohort(data.cohort || []);
  loadEvaluation();   // prefetch trust view
}

function renderCohort(cohort) {
  const wrap = $("cohortList"); wrap.innerHTML = "";
  cohort.forEach(c => {
    const el = document.createElement("div");
    el.className = "cohort-card"; el.id = "co-" + c.id;
    el.onclick = () => selectCustomer(c.id);
    el.innerHTML = `<div class="cc-ring" style="background:${GRADE_COLOR[c.grade]}">${c.score}</div>
      <div><div class="cc-name">${c.name}</div><div class="cc-sub">${c.segment}</div></div>`;
    wrap.appendChild(el);
  });
}

// ── score view ────────────────────────────────────────────────────
async function selectCustomer(id) {
  if (activeId) { const p = $("co-" + activeId); if (p) p.classList.remove("active"); }
  activeId = id;
  const card = $("co-" + id); if (card) card.classList.add("active");
  $("scoreEmpty").hidden = true; $("scoreContent").hidden = false;

  const r = await api("/api/score", { profile_id: id });
  lastResult = r;
  renderScore(r);
}

function renderScore(r) {
  const color = GRADE_COLOR[r.grade] || "#00c4c4";
  // gauge ring (circumference for r=84 ≈ 528)
  const C = 2 * Math.PI * 84;
  const fill = $("gFill");
  fill.style.stroke = color;
  fill.style.strokeDasharray = C;
  // animate from empty
  fill.style.strokeDashoffset = C;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    fill.style.strokeDashoffset = C * (1 - r.score / 100);
  }));
  $("gScore").textContent = r.score;
  $("gScore").setAttribute("fill", "#fff");
  $("gGrade").textContent = `${r.grade} · ${r.grade_label}`;

  $("hName").textContent = r.profile.name;
  $("hSub").textContent = `${r.profile.age} · ${r.profile.location} · ${r.profile.segment}`;
  $("hPercentile").textContent = `Healthier than ${r.percentile}% of this cohort`;
  $("hExplain").textContent = r.explanation;

  // dimensions
  const dims = $("dims"); dims.innerHTML = "";
  Object.values(r.dimensions)
    .sort((a, b) => b.weight - a.weight)
    .forEach(d => {
      const el = document.createElement("div");
      el.className = "dim";
      const barColor = d.score >= 70 ? "#22c55e" : d.score >= 45 ? "#f5a623" : "#ef4444";
      el.innerHTML = `
        <div class="dim-top">
          <span class="dim-label">${d.label} <span class="dim-weight">· weight ${Math.round(d.weight*100)}%</span></span>
          <span class="dim-nums">${d.score}/100 → ${d.contribution} of ${d.max_contribution} pts</span>
        </div>
        <div class="dim-bar"><div class="dim-bar-fill" style="background:${barColor}"></div></div>
        <div class="dim-why">${d.why}
          <span class="concept-link" data-concept="${d.concept}">Learn this →</span></div>`;
      dims.appendChild(el);
      requestAnimationFrame(() => { el.querySelector(".dim-bar-fill").style.width = d.score + "%"; });
    });
  dims.querySelectorAll(".concept-link").forEach(l =>
    l.onclick = () => window.open(ACADEMY(l.dataset.concept), "_blank"));

  // actions
  const actions = $("actions"); actions.innerHTML = "";
  r.top_actions.forEach(a => {
    const el = document.createElement("div");
    el.className = "action";
    el.innerHTML = `
      <div class="action-top">
        <span class="action-title">${a.title}</span>
        <span class="action-uplift">+${a.uplift} pts</span>
      </div>
      <div class="action-benefit">${a.benefit}</div>
      <div class="action-foot">
        <span class="action-product">→ ${a.product}</span>
        <span class="action-learn" data-concept="${a.concept}">📘 Learn the concept</span>
      </div>`;
    actions.appendChild(el);
  });
  actions.querySelectorAll(".action-learn").forEach(l =>
    l.onclick = () => window.open(ACADEMY(l.dataset.concept), "_blank"));
}

// ── share card ────────────────────────────────────────────────────
$("shareBtn") && ($("shareBtn").onclick = () => {
  if (!lastResult) return;
  const color = GRADE_COLOR[lastResult.grade];
  $("scRing").style.background = `conic-gradient(${color} ${lastResult.score*3.6}deg, rgba(255,255,255,.15) 0)`;
  $("scRing").innerHTML = `<div style="width:96px;height:96px;border-radius:50%;background:#16275f;display:flex;align-items:center;justify-content:center"></div>`;
  $("scScore").textContent = lastResult.score;
  $("scGrade").textContent = `${lastResult.grade} · ${lastResult.grade_label}`;
  $("scName").textContent = lastResult.profile.name;
  $("shareOverlay").hidden = false;
});
$("shareClose") && ($("shareClose").onclick = () => $("shareOverlay").hidden = true);

// ── trust / honest metrics view ───────────────────────────────────
async function loadEvaluation() {
  const rep = await api("/api/evaluation", {});
  const m = rep.metrics;
  $("honestyNote").textContent = m.honesty_note;
  $("methodology").textContent = rep.methodology;

  const cards = [
    { v: m.base_rate, fmt: pct, lbl: "Base act-rate", cls: "" },
    { v: m.raw_accuracy, fmt: pct, lbl: "Raw accuracy", cls: "flag", note: "misleading — exposed on purpose" },
    { v: m.precision_at_k, fmt: pct, lbl: `Precision@${Math.round(m.k_frac*100)}%`, cls: "good" },
    { v: m.lift_over_base, fmt: (x)=>x+"×", lbl: "Lift over base", cls: "good" },
    { v: m.recall_at_k, fmt: pct, lbl: "Recall@k", cls: "" },
    { v: m.brier_score, fmt: (x)=>x.toFixed(3), lbl: "Brier score ↓", cls: "good" },
    { v: m.calibration_error_ece, fmt: (x)=>x.toFixed(3), lbl: "Calibration err ↓", cls: "good" },
    { v: m.uplift_mae_points, fmt: (x)=>"±"+x, lbl: "Uplift error (pts)", cls: "" },
  ];
  $("metricGrid").innerHTML = cards.map(c =>
    `<div class="metric ${c.cls}"><div class="metric-val">${c.fmt(c.v)}</div>
     <div class="metric-lbl">${c.lbl}</div>${c.note?`<div class="metric-note">${c.note}</div>`:""}</div>`
  ).join("");

  drawCalibration(m.calibration, m.calibration_error_ece);
  $("eceLabel").textContent = `Expected Calibration Error: ${m.calibration_error_ece} (lower = more trustworthy)`;

  const maxRate = Math.max(...rep.per_nudge.map(x => x.act_rate), 0.01);
  $("perNudge").innerHTML = rep.per_nudge.map(x =>
    `<div class="pn-row"><span class="pn-name">${x.nudge_type.replace(/_/g," ")}</span>
     <span class="pn-bar"><span class="pn-fill" style="width:${(x.act_rate/maxRate)*100}%"></span></span>
     <span class="pn-val">${pct(x.act_rate)} · +${x.mean_realized_uplift}pts</span></div>`
  ).join("");
}

function drawCalibration(buckets, ece) {
  const S = 320, pad = 40, W = S - pad * 2;
  const x = (v) => pad + v * W;
  const y = (v) => S - pad - v * W;
  let svg = "";
  // grid
  for (let i = 0; i <= 5; i++) {
    const g = i / 5;
    svg += `<line class="calib-grid" x1="${x(g)}" y1="${y(0)}" x2="${x(g)}" y2="${y(1)}"/>`;
    svg += `<line class="calib-grid" x1="${x(0)}" y1="${y(g)}" x2="${x(1)}" y2="${y(g)}"/>`;
  }
  // axes
  svg += `<line class="calib-axis" x1="${x(0)}" y1="${y(0)}" x2="${x(1)}" y2="${y(0)}"/>`;
  svg += `<line class="calib-axis" x1="${x(0)}" y1="${y(0)}" x2="${x(0)}" y2="${y(1)}"/>`;
  // diagonal (perfect calibration)
  svg += `<line class="calib-diag" x1="${x(0)}" y1="${y(0)}" x2="${x(1)}" y2="${y(1)}"/>`;
  // ticks
  [0, 0.5, 1].forEach(t => {
    svg += `<text class="calib-tick" x="${x(t)-6}" y="${y(0)+16}">${t}</text>`;
    svg += `<text class="calib-tick" x="${x(0)-22}" y="${y(t)+3}">${t}</text>`;
  });
  svg += `<text class="calib-tick" x="${x(.5)-30}" y="${S-6}">predicted</text>`;
  svg += `<text class="calib-tick" transform="rotate(-90 12 ${y(.5)})" x="12" y="${y(.5)}">actual</text>`;
  // model line + points
  const pts = buckets.map(b => [x(b.mean_predicted), y(b.actual_rate)]);
  if (pts.length) {
    svg += `<polyline class="calib-line" points="${pts.map(p => p.join(",")).join(" ")}"/>`;
    pts.forEach(p => svg += `<circle class="calib-pt" cx="${p[0]}" cy="${p[1]}" r="4"/>`);
  }
  $("calibChart").innerHTML = svg;
}

const pct = (x) => Math.round(x * 100) + "%";

// ── tabs ──────────────────────────────────────────────────────────
document.querySelectorAll(".tab").forEach(t => t.onclick = () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active");
  $("viewScore").hidden = t.dataset.view !== "viewScore";
  $("viewTrust").hidden = t.dataset.view !== "viewTrust";
});

boot();
