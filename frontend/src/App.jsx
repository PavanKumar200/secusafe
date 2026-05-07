import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import PersonalActivity from './pages/PersonalActivity';

// ── Error Boundary – catches any React render crash ───────────────────────────
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { console.error('SecuSafe UI Error:', error, info.componentStack); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-white px-4">
          <div className="max-w-lg text-center">
            <div className="h-20 w-20 bg-red-100 rounded-3xl flex items-center justify-center mx-auto mb-8">
              <svg className="h-10 w-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900 mb-4">Display Error</h2>
            <p className="text-slate-500 mb-2 font-mono text-sm">{this.state.error?.message}</p>
            <p className="text-slate-400 mb-8 text-sm">The scan completed but the result could not be displayed.</p>
            <button onClick={() => window.location.reload()}
              className="bg-secusafe-500 text-white font-bold py-3 px-8 rounded-xl hover:bg-secusafe-600 transition-colors">
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const NavBar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/70 backdrop-blur-xl border-b border-slate-50">
      <div className="section-container h-24 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group" onClick={() => setIsMobileMenuOpen(false)}>
          <div className="h-12 w-12 bg-secusafe-900 rounded-2xl flex items-center justify-center text-white shadow-xl group-hover:bg-secusafe-500 transition-colors duration-500">
            <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span className="text-2xl font-black text-secusafe-900 tracking-tighter">SecuSafe</span>
        </Link>
        
        <div className="hidden md:flex items-center gap-10">
          <Link to="/" className="text-sm font-bold text-slate-500 hover:text-secusafe-900 transition-colors">Scanner</Link>
          <Link to="/activity" className="text-sm font-bold text-slate-500 hover:text-secusafe-900 transition-colors">My Activity</Link>
          <a 
            href="https://t.me/Spam_scanner_bot" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-secusafe-500 text-white hover:bg-secusafe-600 px-6 py-3 rounded-xl text-sm font-bold shadow-lg shadow-secusafe-500/20 transition-all"
          >
            Telegram Bot
          </a>
        </div>
        
        <button 
          className="md:hidden text-slate-900 p-2"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {isMobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-24 left-0 right-0 bg-white border-b border-slate-100 shadow-xl py-6 px-6 flex flex-col gap-6 animate-fade-in">
          <Link 
            to="/" 
            className="text-lg font-bold text-slate-700 hover:text-secusafe-900"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            Scanner
          </Link>
          <Link 
            to="/activity" 
            className="text-lg font-bold text-slate-700 hover:text-secusafe-900"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            My Activity
          </Link>
          <a 
            href="https://t.me/Spam_scanner_bot" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-secusafe-500 text-white text-center hover:bg-secusafe-600 px-6 py-4 rounded-xl text-lg font-bold shadow-lg shadow-secusafe-500/20 transition-all mt-2"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            Open Telegram Bot
          </a>
        </div>
      )}
    </nav>
  );
};

const Footer = () => {
  return (
    <footer className="bg-white pt-32 pb-16">
      <div className="section-container">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-16 mb-20">
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center gap-3 mb-8">
              <div className="h-10 w-10 bg-secusafe-900 rounded-xl flex items-center justify-center text-white">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="text-xl font-black text-secusafe-900 tracking-tighter">SecuSafe</span>
            </div>
            <p className="text-slate-500 text-sm leading-relaxed mb-6">
              Empowering everyday internet users with high-grade security intelligence. Simple, fast, and free.
            </p>
            <div className="flex gap-4">
              {['twitter', 'facebook', 'instagram'].map(s => (
                <div key={s} className="h-8 w-8 bg-slate-50 rounded-lg flex items-center justify-center text-slate-400 hover:bg-secusafe-100 hover:text-secusafe-500 cursor-pointer transition-all">
                  <span className="sr-only">{s}</span>
                  <div className="h-4 w-4 bg-current rounded-sm"></div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h5 className="font-bold text-secusafe-900 mb-6">Product</h5>
            <ul className="space-y-4 text-sm text-slate-500">
              <li><Link to="/" className="hover:text-secusafe-500 transition-colors">URL Scanner</Link></li>
              <li><a href="https://t.me/Spam_scanner_bot" className="hover:text-secusafe-500 transition-colors">Telegram Bot</a></li>
              <li><Link to="/activity" className="hover:text-secusafe-500 transition-colors">Recent Activity</Link></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Bulk Analysis</a></li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-bold text-secusafe-900 mb-6">Support</h5>
            <ul className="space-y-4 text-sm text-slate-500">
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Safety Center</a></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Scam Database</a></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">API Docs</a></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Contact Support</a></li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-bold text-secusafe-900 mb-6">Transparency</h5>
            <ul className="space-y-4 text-sm text-slate-500">
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">How it Works</a></li>
              <li><a href="#" className="hover:text-secusafe-500 transition-colors">Open Source</a></li>
            </ul>
          </div>
        </div>
        
        <div className="pt-12 border-t border-slate-50 flex flex-col md:flex-row justify-between items-center gap-6">
          <p className="text-slate-400 text-xs font-medium">© 2026 SecuSafe Technology. All protections active.</p>
          <div className="flex items-center gap-8">
             <div className="flex items-center gap-2 text-xs font-bold text-emerald-500">
                <span className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></span>
                API ONLINE
             </div>
             <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
                PRIVATE & SECURE
             </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

const App = () => { // wrapped
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-white">
        <NavBar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/activity" element={<PersonalActivity />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
