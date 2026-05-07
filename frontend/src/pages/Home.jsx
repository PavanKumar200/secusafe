import React, { useState, useEffect } from 'react';
import axios from 'axios';
import HeroSection from '../components/Scanner/HeroSection';
import ScanResult from '../components/Results/ScanResult';
import FeatureGrid from '../components/Sections/FeatureGrid';
import TelegramTeaser from '../components/Sections/TelegramTeaser';
import SafetyInsights from '../components/Sections/SafetyInsights';
import CommunityCTA from '../components/Sections/CommunityCTA';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const Home = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Handle re-scan from URL params if any
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const preUrl = params.get('url');
    if (preUrl) {
      setUrl(preUrl);
    }
  }, []);

  const handleScan = async () => {
    if (!url.trim()) {
      setError('Please enter a link to scan.');
      return;
    }
    
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/api/analyze`, { url: url.trim() });
      setResult(response.data);
      // Scroll to result
      setTimeout(() => {
        document.getElementById('result-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to scan the link. Please try again.');
      console.error('Scan error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white">
      <HeroSection 
        url={url} 
        setUrl={setUrl} 
        onScan={handleScan} 
        loading={loading} 
      />
      
      {error && (
        <div className="section-container -mt-16 mb-16 relative z-20">
          <div className="max-w-2xl mx-auto bg-red-50 text-red-600 p-5 rounded-3xl border-2 border-red-100 flex items-center gap-4 shadow-xl">
            <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="font-bold">{error}</div>
          </div>
        </div>
      )}

      {loading && !result && (
        <div className="section-container pb-32 text-center">
          <div className="max-w-2xl mx-auto py-20 bg-secusafe-50/50 rounded-[3rem] border border-secusafe-100">
            <div className="flex flex-col items-center">
              <div className="relative h-24 w-24 mb-8">
                <div className="absolute inset-0 border-[6px] border-secusafe-100 rounded-full"></div>
                <div className="absolute inset-0 border-[6px] border-secusafe-500 rounded-full border-t-transparent animate-spin"></div>
              </div>
              <h3 className="text-2xl font-extrabold text-secusafe-900 mb-2">Analyzing Security Protocols</h3>
              <p className="text-slate-500 font-medium tracking-wide">Checking ML heuristic engines and threat databases...</p>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div id="result-section" className="scroll-mt-32">
          <ScanResult result={result} />
        </div>
      )}

      <FeatureGrid />
      <TelegramTeaser />
      <SafetyInsights />
      <CommunityCTA />
    </div>
  );
};

export default Home;
