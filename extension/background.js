/**
 * background.js — Service worker for Security Scanner extension.
 * On each tab navigation, POSTs the URL to the Flask backend,
 * caches the result, and injects content script if risk > 60.
 */

const API_BASE = 'http://localhost:5000/api';
const RISK_THRESHOLD = 60;

// Track in-flight requests to avoid duplicate calls
const _inFlight = new Set();

/**
 * Analyze a URL via the backend and cache the result.
 * @param {string} url - The URL to analyze
 * @param {number} tabId - The tab to assign the result to
 */
async function analyzeUrl(url, tabId) {
  if (_inFlight.has(url)) return;
  _inFlight.add(url);

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) return;

    const data = await response.json();

    // Cache result keyed by tab id
    const cacheEntry = {
      url,
      risk_score: data.risk_score || 0,
      risk_level: data.risk_level || 'Unknown',
      warnings: data.warnings || [],
      issues: data.issues || [],
      scan_id: data.scan_id || '',
      scanned_at: data.scanned_at || new Date().toISOString(),
    };

    await chrome.storage.session.set({ [`tab_${tabId}`]: cacheEntry });

    // Inject warning banner if high risk
    if (data.risk_score >= RISK_THRESHOLD) {
      try {
        await chrome.scripting.executeScript({
          target: { tabId },
          func: injectWarningBanner,
          args: [data.risk_score, data.risk_level],
        });
      } catch (e) {
        // Tab may no longer exist or may be a chrome:// page
        console.warn('Could not inject script:', e.message);
      }
    }
  } catch (e) {
    // Backend not running — fail silently
    console.warn('Security Scanner: backend unreachable.', e.message);
  } finally {
    _inFlight.delete(url);
  }
}

/**
 * Injected into the page to show a risk warning banner.
 * Must be a standalone function (no closures over extension scope).
 */
function injectWarningBanner(score, level) {
  if (document.getElementById('security-scanner-banner')) return;

  const colors = { Critical: '#7c1e1e', High: '#dc2626', Medium: '#d97706' };
  const bg = colors[level] || '#dc2626';

  const banner = document.createElement('div');
  banner.id = 'security-scanner-banner';
  banner.style.cssText = `
    position: fixed; top: 0; left: 0; right: 0; z-index: 2147483647;
    background: ${bg}; color: #fff;
    padding: 10px 20px; font-family: -apple-system, sans-serif;
    font-size: 14px; font-weight: 600;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  `;

  const msg = document.createElement('span');
  msg.textContent = `⚠️ Security Scanner: This site scored ${score}/100 risk — ${level}`;

  const btn = document.createElement('button');
  btn.textContent = 'Dismiss';
  btn.style.cssText = `
    background: rgba(255,255,255,0.2); color: #fff;
    border: 1px solid rgba(255,255,255,0.4); border-radius: 6px;
    padding: 4px 14px; cursor: pointer; font-size: 12px; font-weight: 600;
  `;
  btn.onclick = () => banner.remove();

  banner.appendChild(msg);
  banner.appendChild(btn);
  document.body.prepend(banner);

  // Offset page content
  document.body.style.paddingTop =
    (parseInt(document.body.style.paddingTop || '0') + banner.offsetHeight) + 'px';
}

// Listen for tab navigation
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete') return;
  const url = tab.url || '';
  // Skip chrome:// and extension pages
  if (!url.startsWith('http://') && !url.startsWith('https://')) return;
  analyzeUrl(url, tabId);
});
