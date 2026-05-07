import React from 'react';
import PropTypes from 'prop-types';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import './FeatureImportanceChart.css';

/**
 * FeatureImportanceChart — Horizontal bar chart of top ML feature importances.
 */
function FeatureImportanceChart({ featureImportances }) {
  if (!featureImportances || featureImportances.length === 0) return null;

  const data = featureImportances.map((fi) => ({
    name: fi.feature.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    importance: parseFloat((fi.importance * 100).toFixed(2)),
    value: fi.value,
  }));

  const COLORS = ['#4f46e5', '#7c3aed', '#2563eb', '#0891b2', '#059669'];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="fi-tooltip">
          <p className="fi-tooltip-name">{d.name}</p>
          <p className="fi-tooltip-val">Importance: <strong>{d.importance}%</strong></p>
          <p className="fi-tooltip-val">Value: <strong>{d.value}</strong></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="fi-chart-panel">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">📊</span>
          ML Feature Importances
        </h3>
        <span className="fi-subtitle">Top {data.length} signals driving this prediction</span>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 30, left: 10, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f3f4f6" />
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11, fill: '#6b7280' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            dataKey="name"
            type="category"
            width={160}
            tick={{ fontSize: 11, fill: '#374151' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" radius={[0, 6, 6, 0]} maxBarSize={28}>
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

FeatureImportanceChart.propTypes = {
  featureImportances: PropTypes.arrayOf(
    PropTypes.shape({
      feature: PropTypes.string.isRequired,
      importance: PropTypes.number.isRequired,
      value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    })
  ),
};

export default FeatureImportanceChart;
