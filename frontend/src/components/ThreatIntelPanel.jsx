import React from 'react';
import PropTypes from 'prop-types';
import './ThreatIntelPanel.css';

/**
 * ThreatIntelPanel — Displays threat intelligence results as colored badge cards.
 * Green = clean, Red = flagged.
 */
function ThreatIntelPanel({ threatIntel }) {
  if (!threatIntel) return null;

  const { urlhaus, google_sb, phishtank, openphish } = threatIntel;

  const sources = [
    {
      id: 'urlhaus',
      name: 'URLhaus',
      description: 'Abuse.ch malware URL database',
      flagged: urlhaus?.listed || false,
      detail: urlhaus?.listed ? `Threat: ${urlhaus.threat || 'malware'}` : 'No active threats found',
    },
    {
      id: 'google_sb',
      name: 'Google Safe Browsing',
      description: 'Google\'s real-time threat detection',
      flagged: google_sb?.flagged || false,
      detail: google_sb?.flagged ? `Type: ${google_sb.threat_type}` : 'URL is safe',
    },
    {
      id: 'phishtank',
      name: 'PhishTank',
      description: 'Community-verified phishing database',
      flagged: !!phishtank,
      detail: phishtank ? 'Confirmed phishing URL' : 'Not in phishing database',
    },
    {
      id: 'openphish',
      name: 'OpenPhish',
      description: 'ML-powered active phishing feed',
      flagged: !!openphish,
      detail: openphish ? 'Found in active phishing feed' : 'Not in phishing feed',
    },
  ];

  const flaggedCount = sources.filter((s) => s.flagged).length;

  return (
    <div className="threat-intel-panel">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">🛡️</span>
          Threat Intelligence
        </h3>
        <span className={`intel-summary-badge ${flaggedCount > 0 ? 'badge-danger' : 'badge-safe'}`}>
          {flaggedCount > 0 ? `${flaggedCount} source${flaggedCount > 1 ? 's' : ''} flagged` : 'All clear'}
        </span>
      </div>

      <div className="intel-grid">
        {sources.map((source) => (
          <div
            key={source.id}
            className={`intel-card ${source.flagged ? 'intel-flagged' : 'intel-clean'}`}
          >
            <div className="intel-card-header">
              <span className="intel-status-icon">{source.flagged ? '🚨' : '✅'}</span>
              <span className="intel-source-name">{source.name}</span>
            </div>
            <p className="intel-source-desc">{source.description}</p>
            <p className="intel-detail">{source.detail}</p>
            <div className={`intel-status-bar ${source.flagged ? 'bar-danger' : 'bar-safe'}`} />
          </div>
        ))}
      </div>
    </div>
  );
}

ThreatIntelPanel.propTypes = {
  threatIntel: PropTypes.shape({
    urlhaus: PropTypes.shape({
      listed: PropTypes.bool,
      threat: PropTypes.string,
      tags: PropTypes.array,
    }),
    google_sb: PropTypes.shape({
      flagged: PropTypes.bool,
      threat_type: PropTypes.string,
    }),
    phishtank: PropTypes.bool,
    openphish: PropTypes.bool,
  }),
};

export default ThreatIntelPanel;
