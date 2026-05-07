import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const PersonalActivity = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/history`);
        setHistory(response.data.history || []);
      } catch (error) {
        console.error('Failed to fetch history:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const getStatusStyle = (level) => {
    if (level === 'High' || level === 'Critical') return 'bg-red-50 text-red-600 border-red-100';
    if (level === 'Medium') return 'bg-amber-50 text-amber-600 border-amber-100';
    return 'bg-secusafe-50 text-secusafe-600 border-secusafe-100';
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">My Activity</h1>
          <p className="text-slate-500">Your recently scanned links and safety reports.</p>
        </header>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 w-full bg-slate-50 rounded-2xl animate-pulse"></div>
            ))}
          </div>
        ) : Array.isArray(history) && history.length > 0 ? (
          <div className="space-y-4">
            {[...history].reverse().map((item) => (
              <div key={item.scan_id} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-secusafe-200 transition-smooth group">
                <div className="flex-grow min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-xs text-slate-400 font-medium">{new Date(item.scanned_at).toLocaleDateString()}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getStatusStyle(item.risk_level)}`}>
                      {item.risk_level} Risk
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-800 truncate">{item.url}</h3>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right hidden md:block">
                    <div className="text-sm font-bold text-slate-900">{item.risk_score}%</div>
                    <div className="text-[10px] text-slate-400 uppercase">Score</div>
                  </div>
                  <Link 
                    to={`/?url=${encodeURIComponent(item.url)}`}
                    className="bg-slate-50 group-hover:bg-secusafe-50 text-slate-600 group-hover:text-secusafe-600 px-4 py-2 rounded-xl text-sm font-bold transition-smooth whitespace-nowrap"
                  >
                    View Report
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-slate-50 rounded-[2.5rem] p-12 text-center border-2 border-dashed border-slate-200">
            <div className="h-16 w-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 text-slate-300">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">No links scanned yet</h3>
            <p className="text-slate-500 mb-8 max-w-sm mx-auto">Start by scanning a suspicious link from your messages or emails on the home page.</p>
            <Link to="/" className="bg-secusafe-500 text-white font-bold px-8 py-3 rounded-xl shadow-lg shadow-secusafe-500/20">
              Go to Scanner
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalActivity;
