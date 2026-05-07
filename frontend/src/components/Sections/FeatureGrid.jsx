import React from 'react';

const FeatureGrid = () => {
  const features = [
    {
      title: "Paste a Suspicious Link",
      description: "Found a weird link in WhatsApp, SMS, or Email? Just copy it and paste it into our scanner.",
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
        </svg>
      ),
      color: "bg-blue-50 text-blue-500"
    },
    {
      title: "Our AI Scans the Site",
      description: "We check the domain age, security certificates, and page content using advanced AI algorithms.",
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: "bg-secusafe-50 text-secusafe-500"
    },
    {
      title: "Get a Clear Verdict",
      description: "Receive an instant report with a risk score and clear instructions on whether it's safe to proceed.",
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      color: "bg-emerald-50 text-emerald-500"
    }
  ];

  return (
    <section className="py-32 bg-white">
      <div className="section-container">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-4xl font-extrabold text-secusafe-900 mb-6">How SecuSafe protects you</h2>
          <p className="text-lg text-slate-500 leading-relaxed">
            We've built an analyst-grade security engine behind a simple, friendly interface designed for everyday internet users.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <div key={i} className="premium-card group">
              <div className={`h-16 w-16 ${f.color} rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500 shadow-sm`}>
                {f.icon}
              </div>
              <h3 className="text-xl font-bold text-secusafe-900 mb-4">{f.title}</h3>
              <p className="text-slate-500 leading-relaxed">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureGrid;
