import React from 'react';

const SafetyInsights = () => {
  const tips = [
    {
      label: "Domain Check",
      title: "Check the domain carefully",
      description: "Scammers often use 'amazon-security.com' instead of 'amazon.com'. Look for extra words or dashes that shouldn't be there.",
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )
    },
    {
      label: "Urgency",
      title: "Watch for urgent language",
      description: "Emails or texts saying 'Your account will be deleted in 1 hour' are almost always scams. Take a deep breath and verify.",
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    {
      label: "Branding",
      title: "Avoid unexpected logos",
      description: "If a message from 'Netflix' has a blurry logo or weird colors, it's a red flag. Legitimate companies keep their branding sharp.",
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    }
  ];

  return (
    <section className="py-32 bg-white">
      <div className="section-container">
        <header className="mb-16">
          <h2 className="text-3xl font-extrabold text-secusafe-900 mb-4">Stay one step ahead</h2>
          <p className="text-slate-500 max-w-2xl">Simple tips to help you and your family spot common scams before they can do harm.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {tips.map((tip, i) => (
            <div key={i} className="flex flex-col bg-secusafe-50/30 p-8 rounded-[2rem] border border-secusafe-100 hover:bg-white hover:shadow-premium transition-all duration-500 group">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-xl bg-white text-secusafe-500 flex items-center justify-center shadow-sm border border-secusafe-50 group-hover:scale-110 transition-transform duration-500">
                  {tip.icon}
                </div>
                <span className="text-[10px] font-bold text-secusafe-400 uppercase tracking-widest">{tip.label}</span>
              </div>
              <h3 className="text-xl font-bold text-secusafe-900 mb-4">{tip.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                {tip.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SafetyInsights;
