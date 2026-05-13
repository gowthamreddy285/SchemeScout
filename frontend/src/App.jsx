import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Filter, BookOpen, ExternalLink, ShieldCheck, Loader2, Info, ChevronRight, Globe, Building2, Gavel } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = 'http://localhost:8000';

const App = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [filters, setFilters] = useState({
    state: 'Central',
    ministry: '',
    section: ''
  });
  const [activeTab, setActiveTab] = useState('all');

  // Metadata for UI
  const states = ['Central', 'Karnataka', 'Tamil Nadu', 'Maharashtra', 'Delhi'];
  const categories = ['MSME', 'Agriculture', 'Startup', 'Student'];
  const sections = [
    { id: 'overview', label: 'Overview', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'eligibility', label: 'Eligibility', icon: <ShieldCheck className="w-4 h-4" /> },
    { id: 'benefits', label: 'Benefits', icon: <Info className="w-4 h-4" /> },
    { id: 'application', label: 'How to Apply', icon: <ExternalLink className="w-4 h-4" /> }
  ];

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const activeFilters = {};
      if (filters.state) activeFilters.state = filters.state;
      if (filters.ministry) activeFilters.ministry = filters.ministry;
      if (filters.section) activeFilters.section = filters.section;

      const response = await axios.post(`${API_BASE_URL}/query`, {
        query: query,
        filters: Object.keys(activeFilters).length > 0 ? activeFilters : null
      });

      setResult(response.data);
    } catch (error) {
      console.error('Search error:', error);
      alert('Failed to connect to the backend. Ensure FastAPI is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen text-slate-200 font-sans px-4 py-8 md:px-8">
      {/* Header */}
      <header className="max-w-6xl mx-auto mb-12 flex flex-col items-center">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-4"
        >
          <div className="bg-primary-500 p-2 rounded-xl shadow-lg shadow-primary-500/20">
            <Gavel className="text-white w-8 h-8" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            Policy Intelligence
          </h1>
        </motion.div>
        <p className="text-slate-400 text-center max-w-xl">
          AI-powered retrieval of Indian government schemes, subsidies, and citizen services with verifiable citations.
        </p>
      </header>

      <main className="max-w-4xl mx-auto">
        {/* Search & Filter Hub */}
        <section className="glass p-1 mb-8 shadow-2xl">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-2">
            <div className="relative flex-1 group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary-400 transition-colors" />
              <input
                type="text"
                placeholder="Ask about PMEGP eligibility, SISFS grants, or organic farming subsidies..."
                className="w-full bg-transparent border-none focus:ring-0 py-4 pl-12 pr-4 text-lg placeholder:text-slate-600 outline-none"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button 
              type="submit"
              disabled={loading}
              className="bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white font-semibold px-8 py-4 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
            </button>
          </form>

          {/* Quick Filters */}
          <div className="border-t border-white/5 p-4 flex flex-wrap gap-4 items-center overflow-x-auto no-scrollbar">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider pr-4 border-r border-white/10">
              <Filter className="w-3 h-3" /> Filters
            </div>
            
            {/* State Selector */}
            <div className="flex gap-2">
              {states.map(s => (
                <button
                  key={s}
                  onClick={() => setFilters({...filters, state: s === filters.state ? '' : s})}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    filters.state === s 
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                    : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-transparent'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>

            <div className="w-px h-4 bg-white/10 mx-2" />

            {/* Section Quick Tabs */}
            <div className="flex gap-2">
              {sections.map(s => (
                <button
                  key={s.id}
                  onClick={() => setFilters({...filters, section: s.id === filters.section ? '' : s.id})}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    filters.section === s.id 
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' 
                    : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-transparent'
                  }`}
                >
                  {s.icon} {s.label}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Results Area */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-20 gap-4"
            >
              <div className="relative">
                <div className="w-16 h-16 border-4 border-primary-500/20 border-t-primary-500 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center text-primary-500 font-bold text-xs uppercase animate-pulse">
                  RAG
                </div>
              </div>
              <p className="text-slate-400 animate-pulse tracking-wide font-medium">Scanning Policy Database & Reranking Chunks...</p>
            </motion.div>
          )}

          {result && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              {/* Main Answer */}
              <div className="glass p-8 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-5">
                  <Gavel className="w-32 h-32" />
                </div>
                <div className="flex items-center gap-2 mb-6">
                  <div className="bg-primary-500/20 text-primary-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border border-primary-500/20">
                    AI-Generated Answer
                  </div>
                  {result.provider && (
                    <div className="bg-slate-800/50 text-slate-400 px-2 py-1 rounded text-[10px] font-mono border border-white/5">
                      via {result.provider}
                    </div>
                  )}
                </div>
                
                <div className="prose prose-invert max-w-none text-lg text-slate-300 leading-relaxed space-y-4">
                  {result.answer.split('\n').map((para, i) => (
                    <p key={i}>{para}</p>
                  ))}
                </div>
              </div>

              {/* Citations & Sources */}
              <div>
                <h3 className="flex items-center gap-2 text-xl font-bold mb-4 px-2">
                  <Building2 className="text-primary-500 w-5 h-5" /> 
                  Sources & Citations
                  <span className="text-xs font-normal text-slate-500 ml-auto">Verified against government guidelines</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.citations.map((cite, idx) => (
                    <motion.div 
                      key={idx}
                      whileHover={{ scale: 1.02 }}
                      className="glass p-5 flex flex-col gap-3 group transition-all hover:bg-white/5"
                    >
                      <div className="flex justify-between items-start">
                        <h4 className="font-bold text-lg text-white group-hover:text-primary-400 transition-colors">
                          {cite.scheme_name}
                        </h4>
                        <span className="bg-white/5 px-2 py-1 rounded text-[10px] font-mono text-slate-500">
                          Match: {(cite.rerank_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      
                      <div className="flex flex-col gap-1 text-sm text-slate-400">
                        <div className="flex items-center gap-2">
                          <Building2 className="w-3 h-3" /> {cite.ministry}
                        </div>
                        <div className="flex items-center gap-2">
                          <Globe className="w-3 h-3" /> {cite.state} • {cite.section.toUpperCase()}
                        </div>
                      </div>

                      <a 
                        href={cite.source_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="mt-2 flex items-center justify-between text-xs font-bold text-primary-400 hover:text-primary-300 transition-colors pt-3 border-t border-white/5"
                      >
                        Official Source URL <ExternalLink className="w-3 h-3" />
                      </a>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {!result && !loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-20 text-slate-500"
            >
              <Search className="w-12 h-12 mb-4 opacity-20" />
              <p>Type a query to search official scheme guidelines</p>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="max-w-6xl mx-auto mt-20 pt-8 border-t border-white/5 text-center text-slate-600 text-sm">
        <p>© 2026 Policy Intelligence System • Grounded in Official Government Guidelines</p>
        <p className="mt-1">Powered by Llama-3.3-70b & BGE Embeddings</p>
      </footer>
    </div>
  );
};

export default App;
