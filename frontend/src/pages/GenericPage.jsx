import React from 'react';
import { useLocation, Link } from 'react-router-dom';

const GenericPage = () => {
  const location = useLocation();
  const path = location.pathname.replace('/', '').replace(/-/g, ' ');
  const title = path.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') || 'Page';

  return (
    <div className="min-h-[70vh] bg-slate-50 pt-32 pb-20">
      <div className="section-container">
        <div className="max-w-3xl mx-auto bg-white rounded-[2rem] p-10 md:p-16 shadow-soft border border-slate-100 text-center">
          <div className="h-20 w-20 bg-secusafe-50 text-secusafe-500 rounded-3xl flex items-center justify-center mx-auto mb-8">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h1 className="text-3xl md:text-5xl font-black text-slate-900 mb-6">{title}</h1>
          <p className="text-lg text-slate-500 mb-10 leading-relaxed">
            We are currently updating our {title.toLowerCase()} documentation. 
            This page will be available very soon with detailed information. 
            Thank you for your patience!
          </p>
          <Link to="/" className="inline-block bg-secusafe-900 text-white font-bold py-4 px-10 rounded-xl hover:bg-secusafe-800 transition-all shadow-xl">
            Return to Scanner
          </Link>
        </div>
      </div>
    </div>
  );
};

export default GenericPage;
