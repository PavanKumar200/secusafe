import React from 'react';

const TelegramTeaser = () => {
  return (
    <section className="py-32 bg-secusafe-50/50">
      <div className="section-container">
        <div className="bg-secusafe-900 rounded-[3rem] p-8 md:p-20 overflow-hidden relative shadow-2xl">
          {/* Abstract background shapes */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-secusafe-500 opacity-10 rounded-full blur-3xl translate-x-1/2 -translate-y-1/2"></div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 items-center gap-16 relative z-10">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 text-secusafe-300 rounded-full text-[10px] font-bold uppercase tracking-widest mb-8 border border-white/10">
                🚀 Security On-the-Go
              </div>
              <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-8 leading-tight">
                Scan links directly <br />
                in <span className="text-secusafe-500">Telegram</span>
              </h2>
              <p className="text-lg text-slate-300 mb-10 leading-relaxed max-w-lg">
                Forward any suspicious message to our Telegram bot and get an instant security verdict without leaving your chat app.
              </p>
              <div className="flex flex-wrap gap-4">
                <a 
                  href="https://t.me/Spam_scanner_bot" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn-accent"
                >
                  Launch Telegram Bot
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M11.944 0C5.346 0 0 5.346 0 11.944c0 6.598 5.346 11.944 11.944 11.944 6.598 0 11.944-5.346 11.944-11.944C23.888 5.346 18.542 0 11.944 0zm5.206 16.561c-.19.19-.506.285-.944.285-.438 0-.876-.118-1.314-.354l-2.614-1.428-1.571 1.571c-.152.152-.354.228-.605.228-.251 0-.453-.076-.605-.228l-.342-.342c-.152-.152-.228-.354-.228-.605 0-.251.076-.453.228-.605l1.571-1.571-1.428-2.614c-.236-.438-.354-.876-.354-1.314 0-.438.095-.754.285-.944.19-.19.506-.285.944-.285.438 0 .876.118 1.314.354l6.057 3.314c.438.236.657.552.657.944s-.219.708-.657.944l-6.057 3.314z"/>
                  </svg>
                </a>
              </div>
            </div>

            <div className="relative hidden md:block">
              {/* Mock Chat UI */}
              <div className="bg-white rounded-[2rem] shadow-2xl p-6 max-w-sm ml-auto relative z-10 border border-slate-100 transform lg:rotate-3">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-50">
                  <div className="h-10 w-10 bg-secusafe-500 rounded-full flex items-center justify-center text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-bold text-slate-900 text-sm">SecuSafe Bot</div>
                    <div className="text-secusafe-500 text-[10px] font-bold">Online</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-slate-50 p-3 rounded-2xl rounded-tl-none mr-8">
                    <p className="text-xs text-slate-600">Forward me any suspicious link!</p>
                  </div>
                  <div className="bg-secusafe-100 p-3 rounded-2xl rounded-tr-none ml-8 text-right">
                    <p className="text-xs text-secusafe-900">https://airbnb-promo.com</p>
                  </div>
                  <div className="bg-white p-4 rounded-2xl border-2 border-red-100 shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="h-2 w-2 bg-red-500 rounded-full animate-ping"></span>
                      <span className="text-[10px] font-bold text-red-600">DANGER DETECTED</span>
                    </div>
                    <p className="text-xs text-slate-700 font-medium">This site is an impersonation scam. Do not provide any info!</p>
                  </div>
                </div>
              </div>
              
              {/* Decorative behind card */}
              <div className="absolute -bottom-10 -left-10 h-64 w-64 bg-secusafe-500/20 rounded-full blur-3xl"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TelegramTeaser;
