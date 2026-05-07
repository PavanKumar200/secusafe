import React from 'react';

const HeroSection = ({ url, setUrl, onScan, loading }) => {
  return (
    <section className="relative pt-32 pb-48 overflow-hidden hero-gradient">
      {/* Background Decorative Element */}
      <div className="absolute top-1/2 right-0 -translate-y-1/2 w-[50%] h-[80%] opacity-20 pointer-events-none hidden lg:block">
        <img 
          src="/secusafe_hero_visual_1778162328242.png" 
          alt="Security Visual" 
          className="w-full h-full object-contain floating-animation"
        />
      </div>

      <div className="section-container relative z-10">
        <div className="max-w-3xl lg:max-w-2xl">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-secusafe-50 text-secusafe-600 rounded-full text-xs font-bold uppercase tracking-widest mb-8 border border-secusafe-100 fade-in-up">
            <span className="flex h-2 w-2 rounded-full bg-secusafe-500 animate-pulse"></span>
            Real-time Threat Intelligence
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold text-secusafe-900 mb-8 leading-[1.05] fade-in-up [animation-delay:200ms]">
            Stop scams before <br />
            <span className="text-secusafe-500">they stop you.</span>
          </h1>

          <p className="text-xl text-slate-500 mb-12 leading-relaxed fade-in-up [animation-delay:400ms] max-w-xl">
            SecuSafe is your personal digital guardian. Paste any suspicious link from WhatsApp, SMS, or Email and let our AI verify it instantly.
          </p>

          <div className="fade-in-up [animation-delay:600ms]">
            <div className="premium-input-container mb-6 group">
              <div className="flex items-center w-full px-5 py-2">
                <div className="text-slate-400 mr-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Paste a suspicious link here..."
                  className="w-full py-4 text-slate-700 bg-transparent outline-none text-xl font-medium placeholder:text-slate-300"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && onScan()}
                  disabled={loading}
                />
              </div>
              <button
                onClick={onScan}
                disabled={loading}
                className="w-full md:w-auto btn-accent !py-5 !px-12 whitespace-nowrap"
              >
                {loading ? (
                  <>
                    <div className="h-5 w-5 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Scanning...
                  </>
                ) : (
                  <>
                    Verify Link
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </>
                )}
              </button>
            </div>

            <div className="flex flex-wrap gap-x-8 gap-y-4 text-sm font-semibold text-slate-400 ml-4">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-secusafe-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                No Signup Required
              </div>
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-secusafe-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Instant Results
              </div>
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-secusafe-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Built for Everyone
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
