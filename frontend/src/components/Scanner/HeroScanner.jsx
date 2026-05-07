import React from 'react';

const HeroScanner = ({ url, setUrl, onScan, loading }) => {
  return (
    <section className="relative pt-24 pb-40 overflow-hidden bg-white">
      {/* Decorative Blobs */}
      <div className="hero-blob w-96 h-96 bg-secusafe-300 top-0 -left-20 animate-[pulse_6s_infinite]"></div>
      <div className="hero-blob w-96 h-96 bg-blue-300 bottom-0 -right-20 animate-[pulse_8s_infinite] delay-1000"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block px-4 py-1.5 bg-secusafe-50 text-secusafe-600 rounded-full text-sm font-bold tracking-wide uppercase mb-8 border border-secusafe-100 animate-fade-in">
            🛡️ Safe Surfing for Everyone
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 mb-8 leading-[1.1] tracking-tight">
            Stop scams before <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-secusafe-500 to-secusafe-700">they stop you.</span>
          </h1>
          
          <p className="text-xl text-slate-500 mb-12 max-w-2xl mx-auto leading-relaxed">
            SecuSafe is your digital guardian. We use advanced AI to verify suspicious links in seconds, so you can browse with confidence.
          </p>
          
          <div className="relative max-w-2xl mx-auto mb-10 group">
            <div className="absolute -inset-1 bg-gradient-to-r from-secusafe-400 to-blue-500 rounded-[2rem] blur opacity-25 group-focus-within:opacity-50 transition duration-1000 group-focus-within:duration-200"></div>
            <div className="relative flex flex-col md:flex-row items-center bg-white rounded-[1.5rem] shadow-2xl p-2 border border-slate-100 group-focus-within:border-secusafe-200 transition-smooth">
              <div className="flex items-center w-full px-4">
                <div className="text-slate-400 mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Paste any suspicious link..."
                  className="w-full py-5 text-slate-700 bg-transparent outline-none text-lg font-medium"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && onScan()}
                  disabled={loading}
                />
              </div>
              <button
                onClick={onScan}
                disabled={loading}
                className="w-full md:w-auto premium-gradient hover:shadow-premium text-white font-bold py-4 px-10 rounded-2xl transition-smooth flex items-center justify-center gap-3 whitespace-nowrap"
              >
                {loading ? (
                  <>
                    <div className="h-5 w-5 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    Scan Now
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
          
          <div className="flex flex-wrap justify-center gap-8 text-sm font-semibold text-slate-400">
            <div className="flex items-center gap-2">
              <span className="p-1 bg-secusafe-100 text-secusafe-600 rounded-lg">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
              No Login Required
            </div>
            <div className="flex items-center gap-2">
              <span className="p-1 bg-secusafe-100 text-secusafe-600 rounded-lg">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
              Instant Results
            </div>
            <div className="flex items-center gap-2">
              <span className="p-1 bg-secusafe-100 text-secusafe-600 rounded-lg">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
              Bank-grade Security
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroScanner;
