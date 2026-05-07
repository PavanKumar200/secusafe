import React from 'react';
import PropTypes from 'prop-types';
import './DomainInfoPanel.css';

/**
 * DomainInfoPanel — Displays domain metadata, SSL info,
 * redirect chain, and typosquatting warnings.
 */
function DomainInfoPanel({ domainInfo }) {
  if (!domainInfo) return null;

  const {
    domain_age_days,
    registrar,
    is_new_domain,
    ssl_days_remaining,
    ssl_self_signed,
    redirect_count,
    closest_brand,
    typosquat_score,
  } = domainInfo;

  const getSslStatus = () => {
    if (ssl_days_remaining === -1) return { label: 'No SSL', cls: 'status-danger' };
    if (ssl_self_signed) return { label: 'Self-Signed', cls: 'status-warning' };
    if (ssl_days_remaining < 10) return { label: `Expires in ${ssl_days_remaining}d`, cls: 'status-warning' };
    return { label: `${ssl_days_remaining} days left`, cls: 'status-safe' };
  };

  const getAgeStatus = () => {
    if (domain_age_days === -1) return { label: 'Unknown', cls: 'status-neutral' };
    if (domain_age_days < 30) return { label: `${domain_age_days} days ⚠️`, cls: 'status-danger' };
    if (domain_age_days < 365) return { label: `${domain_age_days} days`, cls: 'status-warning' };
    const years = Math.floor(domain_age_days / 365);
    return { label: `${years} year${years > 1 ? 's' : ''}`, cls: 'status-safe' };
  };

  const getTypoStatus = () => {
    if (typosquat_score === 2) return { label: `Likely typosquat of ${closest_brand}`, cls: 'status-danger' };
    if (typosquat_score === 1) return { label: `Resembles ${closest_brand}`, cls: 'status-warning' };
    return { label: 'No match detected', cls: 'status-safe' };
  };

  const ssl = getSslStatus();
  const age = getAgeStatus();
  const typo = getTypoStatus();

  const infoRows = [
    {
      icon: '📅',
      label: 'Domain Age',
      value: age.label,
      cls: age.cls,
      note: is_new_domain ? 'Recently registered — high risk signal' : null,
    },
    {
      icon: '🏢',
      label: 'Registrar',
      value: registrar || 'Unknown',
      cls: 'status-neutral',
    },
    {
      icon: '🔒',
      label: 'SSL Certificate',
      value: ssl.label,
      cls: ssl.cls,
      note: ssl_self_signed ? 'Certificate not issued by a trusted CA' : null,
    },
    {
      icon: '↩️',
      label: 'Redirects',
      value: redirect_count > 0 ? `${redirect_count} hop${redirect_count > 1 ? 's' : ''}` : 'None',
      cls: redirect_count > 3 ? 'status-warning' : 'status-safe',
    },
    {
      icon: '🎭',
      label: 'Typosquatting',
      value: typo.label,
      cls: typo.cls,
    },
  ];

  return (
    <div className="domain-info-panel">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">🌍</span>
          Domain Information
        </h3>
      </div>

      <div className="domain-info-rows">
        {infoRows.map((row) => (
          <div className="domain-info-row" key={row.label}>
            <div className="domain-info-label">
              <span className="row-icon">{row.icon}</span>
              <span>{row.label}</span>
            </div>
            <div className="domain-info-value">
              <span className={`domain-status ${row.cls}`}>{row.value}</span>
              {row.note && <p className="row-note">{row.note}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

DomainInfoPanel.propTypes = {
  domainInfo: PropTypes.shape({
    domain_age_days: PropTypes.number,
    registrar: PropTypes.string,
    is_new_domain: PropTypes.bool,
    ssl_days_remaining: PropTypes.number,
    ssl_self_signed: PropTypes.bool,
    redirect_count: PropTypes.number,
    closest_brand: PropTypes.string,
    typosquat_score: PropTypes.number,
  }),
};

export default DomainInfoPanel;
