import React from 'react';

const CommunityCTA = () => {
  return (
    <section className="pb-32 bg-white">
      <div className="section-container">
        <div className="bg-gradient-to-br from-secusafe-500 to-secusafe-700 rounded-[3.5rem] p-8 md:p-20 text-center relative overflow-hidden shadow-glow">
          {/* Abstract pattern overlay */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs>
                <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                  <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100" height="100" fill="url(#grid)" />
            </svg>
          </div>

          <div className="relative z-10 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-1 mb-8">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-10 w-10 rounded-full border-2 border-white/20 bg-white/10 flex items-center justify-center overflow-hidden -ml-2 first:ml-0">
                  <img src={`https://i.pravatar.cc/100?u=user${i}`} alt="user" className="w-full h-full object-cover" />
                </div>
              ))}
              <div className="ml-4 text-white/80 text-sm font-semibold tracking-wide">
                Join 10k+ users staying safe
              </div>
            </div>
            
            <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-8 leading-tight">
              Protect your family <br /> and friends
            </h2>
            <p className="text-lg text-white/80 mb-10 leading-relaxed">
              Cybersecurity is better when shared. Send SecuSafe to your loved ones and help them avoid dangerous links forever.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="bg-white text-secusafe-700 hover:bg-secusafe-50 font-bold py-5 px-12 rounded-2xl transition-all duration-300 shadow-xl flex items-center gap-3 group">
                Share SecuSafe
                <svg className="h-5 w-5 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CommunityCTA;
