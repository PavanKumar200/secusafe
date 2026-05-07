import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './History.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * History page — Fetches and displays the last 50 scan records.
 */
function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await axios.get(`${API_URL}/api/history`);
      const rows = resp.data.history || [];
      setHistory(rows.reverse()); // Most recent first
    } catch (err) {
      setError('Failed to load history. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    const map = { Low: '#16a34a', Medium: '#d97706', High: '#dc2626', Critical: '#7c1e1e' };
    return map[level] || '#6b7280';
  };

  const getRiskBg = (level) => {
    const map = { Low: '#f0fdf4', Medium: '#fefce8', High: '#fff5f5', Critical: '#fdf2f2' };
    return map[level] || '#f9fafb';
  };

  const handleRescan = (url) => {
    window.location.href = `/?url=${encodeURIComponent(url)}`;
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <div>
          <h2 className="history-title">📋 Scan History</h2>
          <p className="history-subtitle">Your last {history.length} security scans</p>
        </div>
        <button className="refresh-btn" onClick={fetchHistory} disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      {loading && (
        <div className="history-loading">
          <div className="loading-spinner" />
          <p>Loading history...</p>
        </div>
      )}

      {error && <div className="history-error">{error}</div>}

      {!loading && !error && history.length === 0 && (
        <div className="history-empty">
          <p>🔍 No scans yet.</p>
          <p>Go to the <a href="/">scanner</a> and analyze a URL to get started.</p>
        </div>
      )}

      {!loading && history.length > 0 && (
        <div className="history-table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>#</th>
                <th>URL</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Scanned At</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row, idx) => (
                <tr key={row.scan_id || idx} className="history-row">
                  <td className="row-num">{idx + 1}</td>
                  <td className="row-url" title={row.url}>
                    <span className="url-text">{row.url}</span>
                  </td>
                  <td className="row-score">
                    <span
                      className="score-badge"
                      style={{
                        background: getRiskBg(row.risk_level),
                        color: getRiskColor(row.risk_level),
                      }}
                    >
                      {row.risk_score}%
                    </span>
                  </td>
                  <td className="row-level">
                    <span
                      className="level-badge"
                      style={{
                        background: getRiskBg(row.risk_level),
                        color: getRiskColor(row.risk_level),
                      }}
                    >
                      {row.risk_level}
                    </span>
                  </td>
                  <td className="row-time">
                    {row.scanned_at ? new Date(row.scanned_at).toLocaleString() : '—'}
                  </td>
                  <td>
                    <button
                      className="rescan-btn"
                      onClick={() => handleRescan(row.url)}
                      title="Re-scan this URL"
                    >
                      🔁 Re-scan
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default History;
