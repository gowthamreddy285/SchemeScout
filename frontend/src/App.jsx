import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Search, 
  ExternalLink, 
  RotateCcw, 
  Loader2,
  ArrowRight,
  Sparkles,
  UserPlus,
  Columns,
  X,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import EligibilityWizard from './EligibilityWizard';

const API_BASE_URL = 'http://localhost:8000';

const App = () => {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('scheme_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [showHistory, setShowHistory] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('scheme_history', JSON.stringify(history));
  }, [history]);

  const resetToHome = () => {
    setConversation([]);
    setInputValue('');
  };

  const handleSubmit = async (e, forcedQuery = null) => {
    if (e) e.preventDefault();
    const query = forcedQuery || inputValue;
    if (!query.trim() || loading) return;

    const newTurn = { query, result: null, id: Date.now() };
    setConversation(prev => [...prev, newTurn]);
    if (!history.includes(query)) setHistory(prev => [query, ...prev].slice(0, 10));
    setInputValue('');
    setShowHistory(false);
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, { query });
      setConversation(prev => prev.map(turn => 
        turn.id === newTurn.id ? { ...turn, result: response.data } : turn
      ));
    } catch (error) {
      setConversation(prev => prev.map(turn => 
        turn.id === newTurn.id ? { ...turn, result: { answer: "Server connection failed.", citations: [] } } : turn
      ));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation, loading]);

  return (
    <div className="min-h-screen bg-[#080808] text-slate-200 selection:bg-indigo-500/30 font-sans pb-40">
      
      {/* Refined Minimalist Header */}
      <header className="max-w-5xl mx-auto px-6 py-10 flex justify-between items-center">
        <button onClick={resetToHome} className="flex items-center gap-3 hover:opacity-80 transition-all">
          <div className="bg-white p-1.5 rounded-lg">
            <Sparkles className="w-4 h-4 text-black" />
          </div>
          <span className="text-sm font-bold tracking-tight text-white uppercase tracking-[0.2em]">SchemeScout</span>
        </button>
        
        <div className="flex items-center gap-4 relative">
          {history.length > 0 && (
            <div className="relative">
              <button 
                onClick={() => setShowHistory(!showHistory)} 
                className={`text-slate-500 hover:text-white transition-colors ${showHistory ? 'text-white' : ''}`}
                title="Recent Queries"
              >
                <Clock className="w-5 h-5" />
              </button>
              
              <AnimatePresence>
                {showHistory && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute right-0 mt-4 w-64 bg-[#111] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
                  >
                    <div className="p-3 border-b border-white/5 bg-white/5">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Recent Queries</span>
                    </div>
                    <div className="max-h-60 overflow-y-auto scrollbar-none">
                      {history.map((h, i) => (
                        <button
                          key={i}
                          onClick={() => handleSubmit(null, h)}
                          className="w-full text-left px-4 py-3 text-sm text-slate-300 hover:bg-white/5 hover:text-white transition-colors truncate border-b border-white/5 last:border-0"
                          title={h}
                        >
                          {h}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {conversation.length > 0 && (
            <button onClick={() => setConversation([])} className="text-slate-500 hover:text-white transition-colors" title="New Chat">
              <RotateCcw className="w-5 h-5" />
            </button>
          )}
        </div>
      </header>

      {/* Main Column */}
      <div className="max-w-4xl mx-auto px-6">
        
        <AnimatePresence mode="wait">
          {conversation.length === 0 ? (
            <motion.div 
              key="hero-view"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-20 text-left"
            >
              <h1 className="text-6xl font-bold text-white mb-6 tracking-tighter leading-none">
                Policy intelligence,<br/>simply delivered.
              </h1>
              <p className="text-slate-500 text-xl max-w-xl leading-relaxed mb-12">
                Direct answers from 200+ official government sources. No fluff, just the facts you need.
              </p>
            </motion.div>
          ) : (
            <motion.div 
              key="chat-view"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-24 mt-10"
            >
              {conversation.map((turn) => (
                <div key={turn.id} className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <div className="text-3xl font-bold text-white tracking-tight">
                    {turn.query}
                  </div>

                  <div className="space-y-8 pl-8 border-l border-white/10">
                    {turn.result ? (
                      <>
                        <div className="text-slate-300 text-lg leading-relaxed max-w-2xl whitespace-pre-wrap">
                          {turn.result.answer}
                        </div>
                        
                        <div className="flex flex-wrap gap-3 pt-4">
                          {turn.result.citations?.map((cite, i) => {
                            // Guard against broken/invalid URLs
                            const isValidUrl = cite.source_url && 
                                              cite.source_url !== 'N/A' && 
                                              cite.source_url.startsWith('http');
                            
                            if (!isValidUrl) return null;

                            return (
                              <div key={i} className="group flex items-center bg-white/[0.03] border border-white/5 rounded-full overflow-hidden transition-all hover:border-white/20">
                                <a 
                                  href={cite.source_url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="px-4 py-2 text-[10px] font-bold text-slate-400 hover:text-white transition-all flex items-center gap-2"
                                >
                                  {cite.scheme_name} <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
                                </a>
                              </div>
                            );
                          })}
                        </div>
                      </>
                    ) : (
                      <div className="flex items-center gap-3 text-slate-500 text-xs font-bold uppercase tracking-[0.2em] animate-pulse">
                        <Loader2 className="w-4 h-4 animate-spin" /> Retrieving data...
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={scrollRef} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Minimalist Input - Becomes Sticky */}
        <div className={`mt-20 transition-all duration-700 ${conversation.length > 0 ? 'fixed bottom-12 left-0 right-0 z-50 flex justify-center px-6' : ''}`}>
           <form 
              onSubmit={handleSubmit}
              className={`w-full max-w-4xl bg-[#0d0d0d] border border-white/10 rounded-2xl p-2 flex items-center gap-2 transition-all ${conversation.length > 0 ? 'shadow-2xl shadow-black ring-1 ring-white/5' : ''}`}
            >
              <input 
                className="flex-1 bg-transparent border-none focus:ring-0 px-6 py-4 text-xl font-medium text-white placeholder:text-slate-700 outline-none"
                placeholder="What would you like to know?"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
              <button 
                type="submit"
                disabled={loading || !inputValue.trim()}
                className="bg-white hover:bg-slate-200 disabled:opacity-20 text-black px-8 py-4 rounded-xl font-bold text-xs uppercase tracking-widest transition-all"
              >
                Ask
              </button>
            </form>
        </div>
      </div>
    </div>
  );
};

export default App;
