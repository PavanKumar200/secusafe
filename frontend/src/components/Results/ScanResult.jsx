import React from 'react';

const ScanResult = ({ result }) => {
  if (!result) return null;

  // Safely extract all fields with fallbacks
  const {
    risk_level = 'Low',
    risk_score = 0,
    url = '',
    recommendation = '',
    issues = [],
    warnings = [],
    threat_intel = {},
    domain_info = {},
    ml_score = 0,
  } = result;

  const safeIssues = Array.isArray(issues) ? issues : [];
  const safeWarnings = Array.isArray(warnings) ? warnings : [];

  // Helper: extract string from an issue/warning that may be a string or an object
  const getText = (item) => {
    if (typeof item === 'string') return item;
    if (typeof item === 'object' && item !== null) {
      return item.description || item.detail || item.type || JSON.stringify(item);
    }
    return String(item);
  };

  const getTitle = (item) => {
    if (typeof item === 'object' && item !== null) return item.type || 'Security Issue';
    return 'Security Issue';
  };

  const getStatusColor = () => {
    if (risk_level === 'Critical') return 'bg-red-600';
    if (risk_level === 'High') return 'bg-red-500';
    if (risk_level === 'Medium') return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  const getStatusBg = () => {
    if (risk_level === 'Critical') return 'bg-red-50 border-red-200';
    if (risk_level === 'High') return 'bg-red-50 border-red-100';
    if (risk_level === 'Medium') return 'bg-amber-50 border-amber-100';
    return 'bg-emerald-50 border-emerald-100';
  };

  const getStatusTextColor = () => {
    if (risk_level === 'Critical' || risk_level === 'High') return 'text-red-700';
    if (risk_level === 'Medium') return 'text-amber-700';
    return 'text-emerald-700';
  };

  const getVerdictLabel = () => {
    if (risk_level === 'Critical') return '⛔ Critical Threat Detected';
    if (risk_level === 'High') return '🚨 Dangerous Link Detected';
    if (risk_level === 'Medium') return '⚠️ Caution Recommended';
    return '✅ This Link Appears Safe';
  };

  const getVerdictEmoji = () => {
    if (risk_level === 'Critical' || risk_level === 'High') return '🛑';
    if (risk_level === 'Medium') return '⚠️';
    return '✅';
  };

  const domainAge = domain_info?.domain_age_days ?? -1;
  const sslDays = domain_info?.ssl_days_remaining ?? -1;
  const phishtankClean = !threat_intel?.phishtank;
  const googleSBSafe = !(threat_intel?.google_sb?.flagged);

  return (
    <div className="py-16">
      <div className="section-container">
        <div className="max-w-4xl mx-auto">

          {/* ── Verdict Banner ─────────────────────────────────────────────── */}
          <div className={`rounded-[2.5rem] p-8 md:p-12 mb-10 border-2 overflow-hidden ${getStatusBg()}`}>
            <div className="flex flex-col md:flex-row items-center gap-8">
              {/* Risk Score Circle */}
              <div className="flex-shrink-0">
                <div className={`h-36 w-36 rounded-full ${getStatusColor()} flex flex-col items-center justify-center text-white shadow-xl`}>
                  <div className="text-4xl font-black">{Math.round(risk_score)}</div>
                  <div className="text-[10px] font-bold uppercase tracking-widest opacity-80">Risk Score</div>
                </div>
              </div>

              {/* Verdict Text */}
              <div className="flex-grow text-center md:text-left">
                <div className={`text-2xl md:text-3xl font-extrabold mb-3 ${getStatusTextColor()}`}>
                  {getVerdictLabel()}
                </div>
                <p className="text-slate-600 text-base leading-relaxed mb-4 max-w-xl">
                  {recommendation}
                </p>
                <div className="flex items-center justify-center md:justify-start gap-2 text-xs text-slate-400 font-medium">
                  <svg className="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
                  </svg>
                  <span className="truncate max-w-[320px] md:max-w-lg bg-white/60 px-3 py-1 rounded-lg border border-white/50">
                    {url}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Stats Row ──────────────────────────────────────────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
            {[
              { label: 'Risk Level', value: risk_level, color: risk_level === 'Low' ? 'text-emerald-600' : risk_level === 'Medium' ? 'text-amber-600' : 'text-red-600' },
              { label: 'ML Score', value: `${Math.round(ml_score)}%`, color: 'text-secusafe-600' },
              { label: 'Issues Found', value: safeIssues.length, color: safeIssues.length > 0 ? 'text-red-500' : 'text-emerald-600' },
              { label: 'Warnings', value: safeWarnings.length, color: safeWarnings.length > 0 ? 'text-amber-500' : 'text-emerald-600' },
            ].map((stat, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-2xl p-5 text-center shadow-sm">
                <div className={`text-2xl font-extrabold ${stat.color} mb-1`}>{stat.value}</div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* ── Issues (Critical Problems) ─────────────────────────────────── */}
          {safeIssues.length > 0 && (
            <div className="mb-10">
              <h3 className="text-lg font-extrabold text-slate-900 mb-5 flex items-center gap-2">
                <span className="h-8 w-8 bg-red-100 text-red-500 rounded-xl flex items-center justify-center">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </span>
                Critical Security Issues
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {safeIssues.map((issue, idx) => (
                  <div key={idx} className="bg-white rounded-2xl border-2 border-red-100 p-6 shadow-sm">
                    <div className="flex items-start gap-4">
                      <div className="h-8 w-8 bg-red-100 text-red-500 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </div>
                      <div className="min-w-0">
                        <div className="font-bold text-slate-900 text-sm mb-1">{getTitle(issue)}</div>
                        <p className="text-sm text-slate-500 leading-relaxed">{getText(issue)}</p>
                        <span className="inline-block mt-2 text-[9px] font-bold uppercase tracking-widest bg-red-50 text-red-500 px-2 py-0.5 rounded-md">High Severity</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Warnings ───────────────────────────────────────────────────── */}
          {safeWarnings.length > 0 && (
            <div className="mb-10">
              <h3 className="text-lg font-extrabold text-slate-900 mb-5 flex items-center gap-2">
                <span className="h-8 w-8 bg-amber-100 text-amber-500 rounded-xl flex items-center justify-center">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </span>
                Cautionary Signals
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {safeWarnings.map((warning, idx) => (
                  <div key={idx} className="bg-white rounded-2xl border-2 border-amber-100 p-6 shadow-sm">
                    <div className="flex items-start gap-4">
                      <div className="h-8 w-8 bg-amber-100 text-amber-500 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
                        </svg>
                      </div>
                      <div className="min-w-0">
                        <div className="font-bold text-slate-900 text-sm mb-1">{getTitle(warning)}</div>
                        <p className="text-sm text-slate-500 leading-relaxed">{getText(warning)}</p>
                        <span className="inline-block mt-2 text-[9px] font-bold uppercase tracking-widest bg-amber-50 text-amber-500 px-2 py-0.5 rounded-md">Moderate Severity</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Intelligence Panel ─────────────────────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-5">Domain Info</h4>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Domain Age</span>
                  <span className={`text-sm font-bold ${domainAge >= 0 && domainAge < 30 ? 'text-red-500' : 'text-slate-800'}`}>
                    {domainAge >= 0 ? `${domainAge} days` : 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">SSL Status</span>
                  <span className={`text-sm font-bold ${sslDays > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                    {sslDays > 0 ? `✓ Encrypted` : 'Unsecured'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Registrar</span>
                  <span className="text-sm font-bold text-slate-800 truncate max-w-[120px]">
                    {domain_info?.registrar || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-5">Threat Intel</h4>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Google Safe Browsing</span>
                  <span className={`text-sm font-bold ${googleSBSafe ? 'text-emerald-600' : 'text-red-500'}`}>
                    {googleSBSafe ? '✓ Clean' : '✗ Flagged'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">PhishTank</span>
                  <span className={`text-sm font-bold ${phishtankClean ? 'text-emerald-600' : 'text-red-500'}`}>
                    {phishtankClean ? '✓ Clean' : '✗ Listed'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">OpenPhish</span>
                  <span className={`text-sm font-bold ${!threat_intel?.openphish ? 'text-emerald-600' : 'text-red-500'}`}>
                    {!threat_intel?.openphish ? '✓ Clean' : '✗ Listed'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-5">AI Prediction</h4>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">ML Risk Score</span>
                  <span className="text-sm font-bold text-slate-800">{Math.round(ml_score)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Model</span>
                  <span className="text-sm font-bold text-slate-800">Ensemble</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Intel Boost</span>
                  <span className={`text-sm font-bold ${result.intel_boost > 0 ? 'text-red-500' : 'text-slate-800'}`}>
                    +{result.intel_boost ?? 0}pts
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ScanResult;
