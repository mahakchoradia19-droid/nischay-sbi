/* SAARTHI — Proactive Engagement Agent frontend */

const API = '';
let activeId = null;
let customers = [];

// ── Boot ──────────────────────────────────────────────────────────
async function boot() {
  try {
    const res = await fetch(`${API}/api/customers`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}',
    });
    const data = await res.json();
    renderKPIs(data.metrics);
    renderCustomers(data.customers);
    setAIPill(data.ai_active, data.path);
  } catch (e) {
    console.error('Customer load failed', e);
  }
}

function renderKPIs(m) {
  setText('kpiMonitored', fmt(m.customers_monitored));
  setText('kpiNudges',    fmt(m.proactive_nudges_7d));
  setText('kpiActRate',   m.act_rate_pct + '%');
  setText('kpiBounces',   fmt(m.emi_bounces_prevented_7d));
  setText('kpiIdle',      '₹' + fmt(m.idle_balance_activated_inr));
}

function renderCustomers(list) {
  customers = list;
  const wrap = document.getElementById('customerList');
  wrap.innerHTML = '';
  list.forEach(c => {
    const el = document.createElement('div');
    el.className = 'cust-card';
    el.id = 'cust-' + c.id;
    el.onclick = () => selectCustomer(c.id);
    const langLabel = { hi: 'हिंदी', en: 'English', gu: 'ગુજરાતી' }[c.preferred_lang] || c.preferred_lang;
    el.innerHTML = `
      <div class="cc-top">
        <div class="cc-avatar">${c.first_name[0]}</div>
        <div>
          <div class="cc-name">${c.name}</div>
          <div class="cc-sub">${c.age} · ${c.location}</div>
        </div>
      </div>
      <div class="cc-tags">
        <span class="cc-tag scenario">${c.scenario_label}</span>
        <span class="cc-tag lang">${langLabel}</span>
        <span class="cc-tag mode-${c.mode}">${c.mode === 'sahaj' ? 'Sahaj mode' : 'Pro mode'}</span>
      </div>
    `;
    wrap.appendChild(el);
  });
}

// ── Select & Analyse ───────────────────────────────────────────────
async function selectCustomer(id) {
  if (activeId) {
    const prev = document.getElementById('cust-' + activeId);
    if (prev) prev.classList.remove('active');
  }
  activeId = id;
  const card = document.getElementById('cust-' + id);
  if (card) card.classList.add('active');

  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('stageContent').style.display = 'grid';

  // Reset phone to thinking state
  document.getElementById('phoneThinking').style.display = 'flex';
  document.getElementById('notifCard').style.display = 'none';
  document.getElementById('actedCard').style.display = 'none';

  // Customer banner
  const c = customers.find(x => x.id === id) || {};
  setText('cbAvatar', (c.first_name || '?')[0]);
  setText('cbName', c.name || id);
  setText('cbMeta', `${c.age} · ${c.location} · ₹${fmt(c.balance_inr)} balance`);
  const modeEl = document.getElementById('cbMode');
  modeEl.textContent = c.mode === 'sahaj' ? '🟢 Sahaj (simple) mode' : '🟣 Pro (data-rich) mode';
  modeEl.className = 'cb-mode ' + c.mode;

  // Clear trace
  document.getElementById('traceBody').innerHTML =
    '<div class="trace-item reasoning"><div class="trace-item-label">🪔 SAARTHI</div><div class="trace-item-detail">Reading financial rhythms…</div></div>';
  setText('tracePath', '—');

  try {
    const res = await fetch(`${API}/api/analyse`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: id }),
    });
    const data = await res.json();
    renderResult(data);
  } catch (e) {
    document.getElementById('traceBody').innerHTML =
      `<div class="trace-item"><div class="trace-item-label">Error</div><div class="trace-item-detail">${e.message}</div></div>`;
  }
}

function renderResult(d) {
  if (!d.ok) {
    document.getElementById('traceBody').innerHTML =
      `<div class="trace-item"><div class="trace-item-label">Error</div><div class="trace-item-detail">${d.error}</div></div>`;
    return;
  }
  setText('tracePath', d.path || '—');

  // Stream the trace, then drop the notification on the phone
  const body = document.getElementById('traceBody');
  body.innerHTML = '';
  const items = d.trace || [];
  items.forEach((item, i) => setTimeout(() => appendTrace(body, item), i * 90));

  // After the trace finishes streaming, reveal the notification
  const total = items.length * 90 + 350;
  setTimeout(() => showNotification(d.nudge), total);
}

function showNotification(nudge) {
  document.getElementById('phoneThinking').style.display = 'none';
  const card = document.getElementById('notifCard');
  card.style.display = 'block';
  setText('notifTitle', nudge.title);
  setText('notifBody', nudge.message);
  setText('notifCta', nudge.cta);
  const urg = document.getElementById('notifUrg');
  urg.textContent = nudge.urgency;
  urg.className = 'notif-urg ' + nudge.urgency;
  setText('notifMode', nudge.channel || 'now');
  setText('phoneCaption', `Delivered via ${nudge.channel} — in ${langName(nudge.language)}.`);
}

function actOnNudge() {
  const c = customers.find(x => x.id === activeId) || {};
  document.getElementById('notifCard').style.display = 'none';
  const acted = document.getElementById('actedCard');
  acted.style.display = 'flex';

  // Scenario-specific confirmation
  const confirmations = {
    emi_shortfall:      ['₹800 swept from FD.', 'EMI covered. No bounce, no penalty, no branch visit.'],
    education_planning: ['Child Education SIP started.', 'School fees handled — and a higher-studies fund begins compounding.'],
    salary_sip:         ['SIP continued · ₹3,000.', 'Your savings habit kept alive on payday — when it is easiest.'],
    idle_balance:       ['FD opened.', 'Idle money now earning 6.8% instead of 3.5%.'],
    financial_stress:   ['Relief options opened.', 'One EMI paused penalty-free. We protect your record together.'],
  };
  const [title, sub] = confirmations[c.scenario] || ['Done in one tap.', 'No friction. No branch visit.'];
  setText('actedTitle', title);
  setText('actedSub', sub);
}

// ── Helpers ────────────────────────────────────────────────────────
function appendTrace(container, item) {
  const el = document.createElement('div');
  el.className = 'trace-item ' + (item.kind || 'tool');
  const icon = item.kind === 'reasoning' ? '🧠' : '⚙';
  let html = `<div class="trace-item-label">${icon} ${item.label}</div>`;
  if (item.detail) html += `<div class="trace-item-detail">${item.detail}</div>`;
  if (item.kind === 'tool' || !item.kind) {
    const kv = flattenObj(item.result || {});
    if (kv.length) {
      html += `<div class="trace-kv">${kv.map(([k, v]) =>
        `<span class="trace-kv-item">${k}: ${v}</span>`).join('')}</div>`;
    }
  }
  el.innerHTML = html;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
}

function setAIPill(active, path) {
  const pill = document.getElementById('aiPill');
  const text = document.getElementById('aiPillText');
  if (active) { pill.classList.remove('offline'); text.textContent = path || 'AI Active'; }
  else { pill.classList.add('offline'); text.textContent = 'Offline Mode'; }
}

function setText(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }

function fmt(n) {
  if (n >= 10000000) return (n / 10000000).toFixed(1) + ' Cr';
  if (n >= 100000)   return (n / 100000).toFixed(2).replace(/\.00$/, '') + ' L';
  if (n >= 1000)     return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  return String(n);
}

function langName(l) { return { hi: 'Hindi', en: 'English', gu: 'Gujarati' }[l] || l; }

function flattenObj(obj, prefix='', out=[]) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (Array.isArray(v)) continue;
    if (v !== null && typeof v === 'object') flattenObj(v, key, out);
    else out.push([key, String(v).slice(0, 44)]);
  }
  return out.slice(0, 8);
}

boot();
