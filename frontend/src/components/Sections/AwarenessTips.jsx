import React from 'react';

const AwarenessTips = () => {
  const tips = [
    {
      title: "Check the domain carefully",
      content: "Scammers often use domains that look like real sites (e.g., g00gle.com instead of google.com). Always look closely at the spelling.",
      color: "bg-blue-50 text-blue-600"
    },
    {
      title: "Watch for urgent language",
      content: "Messages that create fear or urgency (like 'Your account will be suspended!') are common tactics to make you click without thinking.",
      color: "bg-amber-50 text-amber-600"
    },
    {
      title: "Avoid unexpected logins",
      content: "If a link asks you to log in to a service you didn't expect, be very careful. It could be a fake page designed to steal your password.",
      color: "bg-secusafe-50 text-secusafe-600"
    }
  ];

  return (
    <section className="py-24 bg-slate-50">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Stay one step ahead</h2>
            <div className="hidden md:block h-px flex-grow mx-8 bg-slate-200"></div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {tips.map((tip, idx) => (
              <div key={idx} className="bg-white p-8 rounded-3xl border border-slate-100 shadow-soft hover:translate-y-[-4px] transition-smooth">
                <div className={`inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest mb-6 ${tip.color}`}>
                  Pro Tip
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-4">{tip.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{tip.content}</p>
              </div>
            ))}
          </div>
          
          <div className="mt-16 bg-slate-900 rounded-3xl p-8 md:p-12 text-white relative overflow-hidden">
            <div className="relative z-10 max-w-lg">
              <h3 className="text-2xl font-bold mb-4">Protect your family and friends</h3>
              <p className="text-slate-400 mb-8">Share SecuSafe with people you care about. Help them stay safe from online scams and phishing attempts.</p>
              <button 
                onClick={async () => {
                  if (navigator.share) {
                    try { await navigator.share({ title: 'SecuSafe', text: 'Check out SecuSafe - free AI phishing protection!', url: window.location.origin }); }
                    catch (err) { console.log('Share canceled'); }
                  } else {
                    navigator.clipboard.writeText(window.location.origin);
                    alert('Link copied to clipboard!');
                  }
                }}
                className="bg-secusafe-500 hover:bg-secusafe-600 text-white font-semibold py-3 px-8 rounded-xl transition-smooth"
              >
                Share SecuSafe
              </button>
            </div>
            
            {/* Abstract decoration */}
            <div className="absolute top-0 right-0 h-full w-1/3 bg-secusafe-500/10 skew-x-[-20deg] translate-x-1/2"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AwarenessTips;
