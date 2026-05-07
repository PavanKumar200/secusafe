import React, { useState } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import './BulkScanInput.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * BulkScanInput — Accepts up to 20 URLs (one per line) and displays
 * results as a sorted list of mini risk cards.
 */
function BulkScanInput() {
  const [urlsText, setUrlsText] = useState('');
  const [results, setResults] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const getRiskColor = (level) => {
    const map = { Low: '#16a34a', Medium: '#d97706', High: '#dc2626', Critical: '#7c1e1e' };
    return map[level] || '#6b7280';
  };

  const getRiskBg = (level) => {
    const map = { Low: '#f0fdf4', Medium: '#fefce8', High: '#fff5f5', Critical: '#fdf2f2' };
    return map[level] || '#f9fafb';
  };

  const handleScan = async () => {
    const urls = urlsText
      .split('\n')
      .map((u) => u.trim())
      .filter(Boolean);

    if (urls.length === 0) { setError('Enter at least one URL.'); return; }
    if (urls.length > 20) { setError('Maximum 20 URLs per bulk scan.'); return; }

    setLoading(true);
    setError('');
    setResults([]);
    setErrors([]);

    try {
      const resp = await axios.post(`${API_URL}/api/bulk`, { urls });
      const sorted = (resp.data.results || []).sort(
        (a, b) => b.risk_score - a.risk_score
      );
      setResults(sorted);
      setErrors(resp.data.errors || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Bulk scan failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const lineCount = urlsText.split('\n').filter((l) => l.trim()).length;

  return (
    <div className="bulk-scan-container">
      <div className="bulk-header">
        <h3 className="bulk-title">⚡ Bulk URL Scanner</h3>
        <span className="bulk-counter">{lineCount}/20 URLs</span>
      </div>

      <textarea
        className="bulk-textarea"
        placeholder={"Enter up to 20 URLs, one per line:\ngoogle.com\nhttps://example.com\nfacebook.com"}
        value={urlsText}
        onChange={(e) => setUrlsText(e.target.value)}
        rows={6}
        disabled={loading}
      />

      {error && <div className="bulk-error">{error}</div>}

      <button
        className="bulk-scan-btn"
        onClick={handleScan}
        disabled={loading || lineCount === 0}
      >
        {loading ? (
          <>
            <span className="spinner" /> Scanning {lineCount} URL{lineCount !== 1 ? 's' : ''}...
          </>
        ) : (
          `🔍 Scan ${lineCount} URL${lineCount !== 1 ? 's' : ''}`
        )}
      </button>

      {results.length > 0 && (
        <div className="bulk-results">
          <p className="bulk-results-header">
            Results — sorted by risk score (highest first)
          </p>
          <div className="bulk-cards">
            {results.map((r, i) => (
              <div
                key={r.scan_id || i}
                className="mini-risk-card"
                style={{ background: getRiskBg(r.risk_level), borderColor: getRiskColor(r.risk_level) }}
              >
                <div className="mini-card-score" style={{ color: getRiskColor(r.risk_level) }}>
                  {r.risk_score}%
                </div>
                <div className="mini-card-info">
                  <span className="mini-card-url">{r.url}</span>
                  <span
                    className="mini-card-level"
                    style={{ color: getRiskColor(r.risk_level) }}
                  >
                    {r.risk_level}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {errors.length > 0 && (
            <div className="bulk-errors">
              <p className="bulk-errors-header">⚠️ Failed URLs:</p>
              {errors.map((e, i) => (
                <div key={i} className="bulk-error-item">
                  <code>{e.url}</code> — {e.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

BulkScanInput.propTypes = {};

export default BulkScanInput;
