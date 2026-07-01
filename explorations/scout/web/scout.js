/* SCOUT — Acquisition Agent frontend */

const API = '';
let activeProspectId = null;
let pipelineData = [];

// ── Boot ──────────────────────────────────────────────────────────
async function boot() {
  try {
    const res = await fetch(`${API}/api/pipeline`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    const data = await res.json();
    renderKPIs(data.metrics);
    renderPipeline(data.prospects);
    setAIPill(data.ai_active, data.path);
  } catch (e) {
    console.error('Pipeline load failed', e);
  }
}

// ── KPIs ──────────────────────────────────────────────────────────
function renderKPIs(m) {
  setText('kpiProspects',    fmt(m.prospects_identified_7d));
  setText('kpiHighIntent',   fmt(m.high_intent_leads));
  setText('kpiConversions',  fmt(m.conversions_7d));
  setText('kpiRate',         m.conversion_rate_pct + '%');
  setText('kpiCAC',          '₹' + fmt(m.cost_per_acquisition_inr));
  setText('kpiCACReduction', m.cac_reduction_pct + '%');
}

// ── Pipeline render ────────────────────────────────────────────────
function renderPipeline(prospects) {
  pipelineData = prospects;
  setText('pipelineCount', prospects.length + ' prospects');

  const groups = { dormant_jan_dhan: 'listJD', employer_partnership: 'listEP', life_event: 'listLE' };
  Object.values(groups).forEach(id => { document.getElementById(id).innerHTML = ''; });

  prospects.forEach(p => {
    const listId = groups[p.segment];
    if (!listId) return;
    const el = document.createElement('div');
    el.className = 'prospect-card';
    el.id = 'card-' + p.id;
    el.onclick = () => selectProspect(p.id);

    // compute urgency for card badge (quick heuristic)
    const urgency = p.confidence_pct >= 90 ? 'HIGH' : p.confidence_pct >= 75 ? 'MEDIUM' : 'MEDIUM';
    const signalChips = (p.signals || []).slice(0, 3)
      .map(s => `<span class="signal-chip">${s.replace(/_/g, ' ')}</span>`).join('');

    let meta = p.location;
    if (p.life_event) meta += ` · ${p.life_event.replace(/_/g, ' ')}`;
    if (p.confidence_pct) meta += ` · ${p.confidence_pct}% confidence`;

    el.innerHTML = `
      <div class="pc-top">
        <div class="pc-name">${p.name}</div>
        <div class="pc-urgency urg-${urgency}">${urgency}</div>
      </div>
      <div class="pc-location">${meta}</div>
      <div class="pc-trigger">${p.trigger_summary}</div>
      <div class="pc-signals">${signalChips}</div>
    `;
    document.getElementById(listId).appendChild(el);
  });
}

// ── Select & Analyse ───────────────────────────────────────────────
async function selectProspect(id) {
  if (activeProspectId) {
    const prev = document.getElementById('card-' + activeProspectId);
    if (prev) prev.classList.remove('active');
  }
  activeProspectId = id;
  const card = document.getElementById('card-' + id);
  if (card) card.classList.add('active');

  // Show panel, hide empty state
  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('analysisContent').style.display = 'flex';
  document.getElementById('analysisContent').style.flexDirection = 'column';
  document.getElementById('analysisContent').style.gap = '16px';

  // Reset outreach + approved state
  document.getElementById('outreachBlock').style.display = 'none';
  document.getElementById('approvedMsg').style.display = 'none';
  document.getElementById('approveBtn').disabled = false;

  // Stub header while loading
  const p = pipelineData.find(x => x.id === id) || {};
  setText('pName', p.name || id);
  setText('pMeta', (p.location || '') + (p.segment ? ' · ' + segLabel(p.segment) : ''));
  setText('pAvatar', avatarChar(p.name || '?'));
  setText('mConvProb', '…');
  setText('mCLV', '…');
  setText('mCampaign', '…');
  setUrgency('pUrgency', '…', '');

  // Show loading spinner in trace
  const traceBody = document.getElementById('traceBody');
  traceBody.innerHTML = '<div class="trace-loading" id="traceLoading"><div class="spinner"></div> Analysing prospect…</div>';
  setText('tracePath', '—');

  // Call API
  try {
    const res = await fetch(`${API}/api/analyse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prospect_id: id }),
    });
    const data = await res.json();
    renderAnalysis(data);
  } catch (e) {
    traceBody.innerHTML = `<div class="trace-item"><div class="trace-item-label">Error</div><div class="trace-item-detail">${e.message}</div></div>`;
  }
}

// ── Render analysis result ─────────────────────────────────────────
function renderAnalysis(d) {
  if (!d.ok) {
    document.getElementById('traceBody').innerHTML =
      `<div class="trace-item"><div class="trace-item-label">Error</div><div class="trace-item-detail">${d.error}</div></div>`;
    return;
  }

  // Header
  setText('pName', d.prospect_name || d.prospect_id);
  const p = pipelineData.find(x => x.id === d.prospect_id) || {};
  setText('pMeta', (p.location || '') + ' · ' + segLabel(d.segment));
  setText('pAvatar', avatarChar(d.prospect_name || '?'));
  setUrgency('pUrgency', d.acquisition_urgency, d.acquisition_urgency);

  // Metrics
  setText('mConvProb', Math.round((d.conversion_probability || 0) * 100) + '%');
  setText('mCLV', '₹' + fmt(d.expected_clv_inr || 0));
  setText('mCampaign', d.campaign_id || '—');

  // Outreach
  if (d.outreach_message) {
    document.getElementById('outreachBlock').style.display = 'flex';
    setText('outreachMessage', d.outreach_message);
    const langMap = { en: '🇬🇧 English', hi: '🇮🇳 Hindi', gu: '🇮🇳 Gujarati' };
    setText('outreachLang', langMap[p.preferred_lang] || p.preferred_lang || '');
    const channelIcon = channelEmoji(d.channel || '');
    setText('outreachChannel', channelIcon + ' ' + (d.channel || 'Channel'));
  }

  // Trace path
  setText('tracePath', d.path || '—');

  // Trace items
  const traceBody = document.getElementById('traceBody');
  traceBody.innerHTML = '';
  (d.trace || []).forEach((item, i) => {
    setTimeout(() => appendTrace(traceBody, item), i * 80);
  });
}

function appendTrace(container, item) {
  const el = document.createElement('div');
  el.className = 'trace-item ' + (item.kind || 'tool');

  const labelIcon = item.kind === 'reasoning' ? '🧠' : '⚙';
  let html = `<div class="trace-item-label">${labelIcon} ${item.label}</div>`;

  if (item.detail) {
    html += `<div class="trace-item-detail">${item.detail}</div>`;
  }

  // For tool items, render args + result as key-value chips
  if (item.kind === 'tool' || !item.kind) {
    const kvPairs = flattenObj(item.result || {});
    if (kvPairs.length) {
      html += `<div class="trace-kv">${kvPairs.map(([k, v]) =>
        `<span class="trace-kv-item">${k}: ${v}</span>`).join('')}</div>`;
    }
  }

  el.innerHTML = html;
  container.appendChild(el);
}

// ── Approve outreach ───────────────────────────────────────────────
function approveOutreach() {
  document.getElementById('approveBtn').disabled = true;
  setTimeout(() => {
    document.getElementById('approvedMsg').style.display = 'block';
  }, 600);
}

// ── AI pill ────────────────────────────────────────────────────────
function setAIPill(active, path) {
  const pill = document.getElementById('aiPill');
  const text = document.getElementById('aiPillText');
  if (active) {
    pill.classList.remove('offline');
    text.textContent = path || 'AI Active';
  } else {
    pill.classList.add('offline');
    text.textContent = 'Offline Mode';
  }
}

// ── Helpers ────────────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setUrgency(id, text, cls) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  el.className = 'urgency-badge ' + cls;
}

function fmt(n) {
  if (n >= 10000000) return (n / 10000000).toFixed(1) + ' Cr';
  if (n >= 100000)   return (n / 100000).toFixed(1) + ' L';
  if (n >= 1000)     return (n / 1000).toFixed(1) + 'K';
  return String(n);
}

function avatarChar(name) {
  return name && name !== '?' ? name[0].toUpperCase() : '?';
}

function segLabel(seg) {
  return { dormant_jan_dhan: 'Dormant Jan Dhan', employer_partnership: 'Employer Partnership', life_event: 'Life Event' }[seg] || seg;
}

function channelEmoji(channel) {
  if (/whatsapp/i.test(channel)) return '💬';
  if (/sms/i.test(channel))      return '📱';
  if (/call|callback/i.test(channel)) return '📞';
  if (/email/i.test(channel))    return '📧';
  if (/yono|push/i.test(channel))return '🔔';
  return '📤';
}

function flattenObj(obj, prefix='', out=[]) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
      flattenObj(v, key, out);
    } else if (!Array.isArray(v)) {
      out.push([key, String(v).slice(0, 40)]);
    }
  }
  return out.slice(0, 8); // cap at 8 chips
}

// ── Start ──────────────────────────────────────────────────────────
boot();
