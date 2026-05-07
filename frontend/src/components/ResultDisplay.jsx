import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import './ResultDisplay.css';

function ResultDisplay({ result }) {
  const getRiskColor = (level) => {
    switch(level) {
      case 'Low': return '#10b981';
      case 'Medium': return '#f59e0b';
      case 'High': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const chartData = [
    { name: 'Risk', value: result.risk_score },
    { name: 'Safe', value: 100 - result.risk_score }
  ];

  const COLORS = [getRiskColor(result.risk_level), '#e5e7eb'];

  return (
    <div className="result-container">
      <div className="risk-summary">
        <h2>Analysis Results</h2>
        <div className="url-display">{result.url}</div>
        
        <div className="risk-score-section">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          
          <div className="score-display">
            <div className="score-number" style={{color: getRiskColor(result.risk_level)}}>
              {result.risk_score}%
            </div>
            <div className={`risk-badge risk-${result.risk_level.toLowerCase()}`}>
              {result.risk_level} Risk
            </div>
          </div>
        </div>

        <div className="recommendation">
          <strong>Recommendation:</strong> {result.recommendation}
        </div>
      </div>

      {result.issues.length > 0 && (
        <div className="issues-section">
          <h3>⚠️ Security Issues Found</h3>
          {result.issues.map((issue, index) => (
            <div key={index} className={`issue-card severity-${issue.severity}`}>
              <div className="issue-header">
                <span className="issue-type">{issue.type}</span>
                <span className={`severity-badge severity-${issue.severity}`}>
                  {issue.severity}
                </span>
              </div>
              <p className="issue-description">{issue.description}</p>
              <p className="issue-detail">{issue.detail}</p>
            </div>
          ))}
        </div>
      )}

      {result.warnings.length > 0 && (
        <div className="warnings-section">
          <h3>⚡ Warnings</h3>
          {result.warnings.map((warning, index) => (
            <div key={index} className="warning-card">
              <strong>{warning.type}:</strong> {warning.description}
            </div>
          ))}
        </div>
      )}

      {result.key_indicators.length > 0 && (
        <div className="indicators-section">
          <h3>🔍 Key Indicators</h3>
          {result.key_indicators.map((indicator, index) => (
            <div key={index} className="indicator-item">
              <span className="indicator-name">{indicator.feature}</span>
              <span className="indicator-value">Value: {indicator.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ResultDisplay;