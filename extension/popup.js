/**
 * popup.js — Reads the cached scan result for the current tab
 * and renders it in popup.html.
 */

const FRONTEND_URL = 'http://localhost:3000';

function getLevelClass(level) {
  const map = { Low: 'low', Medium: 'medium', High: 'high', Critical: 'critical' };
  return map[level] || 'high';
}

function renderNoData(url) {
  return `
    <div class="no-data">
      <div class="icon">🔍</div>
      <p>No scan data for this page yet.</p>
      <p style="margin-top:6px;">The scanner checks pages automatically on load.</p>
      ${url ? `
        <a class="full-report-link" style="margin-top:14px;display:block;"
           href="${FRONTEND_URL}?url=${encodeURIComponent(url)}" target="_blank">
          🔍 Scan This Page
        </a>` : ''}
    </div>
  `;
}

function renderResult(data) {
  const lvl = getLevelClass(data.risk_level);
  const topAlerts = [...(data.issues || []), ...(data.warnings || [])].slice(0, 3);
  const reportUrl = data.scan_id
    ? `http://localhost:5000/api/report/${data.scan_id}`
    : `${FRONTEND_URL}?url=${encodeURIComponent(data.url)}`;
  const frontendUrl = `${FRONTEND_URL}?url=${encodeURIComponent(data.url)}`;
  const scannedAt = data.scanned_at
    ? new Date(data.scanned_at).toLocaleTimeString()
    : '';

  return `
    <div class="risk-card ${lvl}">
      <div class="risk-row">
        <span class="risk-score-text">${data.risk_score}<small style="font-size:1rem">%</small></span>
        <span class="risk-level-badge">${data.risk_level}</span>
      </div>
      <div class="risk-url">${data.url}</div>
    </div>

    ${topAlerts.length > 0 ? `
      <div class="warnings-section">
        <div class="warnings-title">⚠️ TOP WARNINGS</div>
        ${topAlerts.map(w => `
          <div class="warning-item">${w.description || w.type || ''}</div>
        `).join('')}
      </div>
    ` : ''}

    <a class="full-report-link" href="${frontendUrl}" target="_blank">
      🔍 Full Report in Dashboard
    </a>
    ${scannedAt ? `<div class="scan-time">Last scanned at ${scannedAt}</div>` : ''}
  `;
}

// ── Main ───────────────────────────────────────────────────────────────────

async function init() {
  const contentEl = document.getElementById('popup-content');

  try {
    // Get the active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      contentEl.innerHTML = renderNoData('');
      return;
    }

    const tabUrl = tab.url || '';
    const key = `tab_${tab.id}`;

    // Read cached result from session storage
    const stored = await chrome.storage.session.get(key);
    const data = stored[key];

    if (!data) {
      contentEl.innerHTML = renderNoData(tabUrl);
      return;
    }

    contentEl.innerHTML = renderResult(data);
  } catch (e) {
    contentEl.innerHTML = `
      <div class="no-data">
        <div class="icon">⚠️</div>
        <p>Error loading data: ${e.message}</p>
      </div>
    `;
  }
}

init();
