// DBT Gap Agent — community intelligence client.
// Renders the computed detect → diagnose → act → measure loop at cohort scale.

const $ = (id) => document.getElementById(id);
const api = (path, body) => fetch(path, {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body || {}),
}).then(r => r.json());

const cr = (x) => "₹" + (x / 1e7).toFixed(x >= 1e8 ? 0 : 1) + " Cr";
const num = (x) => x.toLocaleString("en-IN");
let districts = [];
let activeId = null;

async function boot() {
  const o = await api("/api/overview", {});
  districts = o.districts || [];
  // national hero
  $("natAtRisk").textContent = cr(o.national.extrapolated_at_risk_inr);
  $("natDemoRisk").textContent = cr(o.national.demo_at_risk_inr);
  $("natRescue").textContent = Math.round(o.measure.rescue_rate_when_acted * 100) + "%";
  // ROI: compute a representative one from the largest district later; show placeholder
  $("natRoi").textContent = "—";
  renderDistricts();
  // prime ROI from the top district
  if (districts[0]) primeRoi(districts[0].id);
}

async function primeRoi(id) {
  const d = await api("/api/district", { district_id: id });
  $("natRoi").textContent = d.diagnose.roi_x + "×";
}

function renderDistricts() {
  const max = Math.max(...districts.map(d => d.at_risk_amount_inr), 1);
  $("districtList").innerHTML = "";
  districts.forEach(d => {
    const el = document.createElement("div");
    el.className = "dist-card"; el.id = "d-" + d.id;
    el.onclick = () => selectDistrict(d.id);
    el.innerHTML = `<div class="dc-name">${d.name}</div>
      <div class="dc-state">${d.state} · ${num(d.eligible)} eligible</div>
      <div class="dc-bar"><div class="dc-fill" style="width:${(d.at_risk_amount_inr/max)*100}%"></div></div>
      <div class="dc-risk">${cr(d.at_risk_amount_inr)} at risk · ${d.at_risk_pct}%</div>`;
    $("districtList").appendChild(el);
  });
}

async function selectDistrict(id) {
  if (activeId) { const p = $("d-" + activeId); if (p) p.classList.remove("active"); }
  activeId = id;
  const card = $("d-" + id); if (card) card.classList.add("active");
  $("empty").hidden = true; $("loopContent").hidden = false;

  const r = await api("/api/district", { district_id: id });
  const det = r.detect;
  $("loopHead").innerHTML = `${det.district}, ${det.state} <span>· ${num(det.eligible)} DBT-eligible accounts this cycle</span>`;

  // DETECT
  $("detectGrid").innerHTML = [
    [num(det.at_risk_accounts), "accounts at risk", "risk"],
    [det.at_risk_pct + "%", "of eligible", "risk"],
    [cr(det.at_risk_amount_inr), "₹ at risk this cycle", "risk"],
    [cr(det.total_cycle_amount_inr), "total cycle disbursement", ""],
  ].map(([v, l, c]) => `<div class="detect-cell"><div class="dv ${c}">${v}</div><div class="dl">${l}</div></div>`).join("");

  // DIAGNOSE
  $("segments").innerHTML = r.diagnose.segments.map(s => `
    <div class="seg ${s.tier}">
      <div class="seg-top">
        <span class="seg-cause">${s.cause}</span>
        <span class="seg-resc">→ rescue ${Math.round(s.rescue_rate*100)}% = ${cr(s.projected_rescued_inr)}</span>
      </div>
      <div class="seg-action">${s.action}</div>
      <div class="seg-foot">
        <span><b>${num(s.accounts)}</b> accounts</span>
        <span><b>${cr(s.amount_inr)}</b> at risk</span>
        <span>channel: ${s.channel}</span>
        ${s.no_mobile_share_pct ? `<span><b>${s.no_mobile_share_pct}%</b> no mobile → IVR/camp</span>` : ""}
      </div>
    </div>`).join("");
  $("diagTotal").innerHTML = `Acting on all segments rescues an estimated
    <b>${num(r.diagnose.projected_rescued_accounts)} accounts · ${cr(r.diagnose.projected_rescued_inr)}</b>
    for ₹${num(r.diagnose.intervention_cost_inr)} of intervention — a <b>${r.diagnose.roi_x}× ROI</b>,
    and not a rupee of cross-sell.`;

  // ACT
  $("interventions").innerHTML = r.act.map(a => `
    <div class="intv">
      <div class="intv-top">
        <span class="intv-title">${a.title}</span>
        <span class="intv-targets">${num(a.targets)} targets</span>
      </div>
      ${a.message_hi ? `<div class="intv-msg">${a.message_hi}</div>` : ""}
      <div class="intv-ops">⚙ ${a.ops}</div>
      ${a.deploy_villages ? `<div class="intv-villages">📍 Deploy camps to: ${a.deploy_villages.join(", ")}</div>` : ""}
    </div>`).join("");

  // MEASURE
  loadMeasure();
}

async function loadMeasure() {
  const m = await api("/api/measure", {});
  $("measureNote").textContent = m.honesty_note;
  $("measureGrid").innerHTML = [
    [pct(m.base_rate), "bounce base rate", ""],
    [pct(m.raw_accuracy), "raw accuracy", "flag"],
    [pct(m.precision_at_10pct), "precision@10%", "good"],
    [m.lift_over_base + "×", "lift over base", "good"],
    [m.brier_score.toFixed(3), "Brier ↓", "good"],
    [m.calibration_error_ece.toFixed(3), "calib. err ↓", "good"],
    [pct(m.rescue_rate_when_acted), "rescued when acted", "good"],
  ].map(([v, l, c]) => `<div class="m-cell ${c}"><div class="m-val">${v}</div><div class="m-lbl">${l}</div></div>`).join("");
}

const pct = (x) => Math.round(x * 100) + "%";

boot();
