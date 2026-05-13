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
  Clock,
  ShieldCheck,
  Landmark,
  FileCheck,
  Send,
  Link as LinkIcon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// We fall back to localhost:8000 for local dev if env var is missing
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Typewriter = ({ text = "", delay = 10 }) => {
  const [currentText, setCurrentText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  const safeText = String(text || "");

  useEffect(() => {
    setCurrentText('');
    setCurrentIndex(0);
  }, [safeText]);

  useEffect(() => {
    if (currentIndex < safeText.length) {
      const timeout = setTimeout(() => {
        setCurrentText(prevText => prevText + safeText[currentIndex]);
        setCurrentIndex(prevIndex => prevIndex + 1);
      }, delay);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, delay, safeText]);

  return (
    <div className="text-slate-300 leading-relaxed whitespace-pre-wrap max-w-none">
      {currentText}
    </div>
  );
};

const RotatingPlaceholder = () => {
  const placeholders = [
    "Scholarships for SC students...",
    "PMAY housing eligibility...",
    "Women entrepreneur startup schemes...",
    "Farmer subsidy programs..."
  ];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((current) => (current + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <AnimatePresence mode="wait">
      <motion.span
        key={index}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -5 }}
        className="absolute left-6 text-slate-500 pointer-events-none text-xl font-medium"
      >
        {placeholders[index]}
      </motion.span>
    </AnimatePresence>
  );
};

const App = () => {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('scheme_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [showHistory, setShowHistory] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);
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
    
    // Group similar queries or update recent list
    if (!history.includes(query)) {
      setHistory(prev => [query, ...prev].slice(0, 10));
    }
    
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
        turn.id === newTurn.id ? { ...turn, result: { answer: "Unable to retrieve schemes right now. Please try again.", citations: [] } } : turn
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

  const suggestedQueries = [
    "SC scholarships",
    "Farmer subsidy schemes",
    "Women startup schemes",
    "PMAY eligibility"
  ];

  return (
    <div className="min-h-screen bg-[#080808] text-slate-200 selection:bg-violet-500/30 font-sans pb-40 relative overflow-hidden">
      
      {/* Subtle background effect */}
      <div className="fixed inset-0 pointer-events-none" style={{ background: 'radial-gradient(circle at center 30%, rgba(139, 92, 246, 0.04), transparent 60%)' }} />
      <div className="fixed inset-0 pointer-events-none opacity-[0.015] bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:40px_40px]" />

      {/* Header */}
      <header className="max-w-5xl mx-auto px-6 py-8 flex justify-between items-center relative z-10">
        <button onClick={resetToHome} className="flex items-center gap-3 hover:opacity-80 transition-all">
          <div className="bg-violet-600 p-1.5 rounded-lg shadow-[0_0_15px_rgba(139,92,246,0.3)]">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-bold tracking-tight text-white uppercase tracking-[0.2em]">SchemeScout</span>
        </button>
        
        <div className="flex items-center gap-4 relative">
          {history.length > 0 && (
            <div className="relative">
              <button 
                onClick={() => setShowHistory(!showHistory)} 
                className={`text-slate-500 hover:text-white transition-colors ${showHistory ? 'text-violet-400' : ''}`}
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
                    className="absolute right-0 mt-4 w-72 bg-[#111] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
                  >
                    <div className="p-3 border-b border-white/5 bg-white/5 flex justify-between items-center">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Recent Sessions</span>
                      <button onClick={() => setHistory([])} className="text-[10px] text-slate-500 hover:text-red-400 transition-colors uppercase font-bold tracking-wider">Clear</button>
                    </div>
                    <div className="max-h-60 overflow-y-auto scrollbar-none">
                      {history.map((h, i) => (
                        <button
                          key={i}
                          onClick={() => handleSubmit(null, h)}
                          className="w-full text-left px-4 py-3 text-sm text-slate-300 hover:bg-white/5 hover:text-violet-300 transition-colors truncate border-b border-white/5 last:border-0 flex items-center gap-3 group"
                          title={h}
                        >
                          <Search className="w-3 h-3 text-slate-600 group-hover:text-violet-500 transition-colors shrink-0" />
                          <span className="truncate">{h}</span>
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
      <div className="max-w-4xl mx-auto px-6 relative z-10 flex flex-col min-h-[calc(100vh-140px)]">
        
        <div className="flex-1">
          <AnimatePresence mode="wait">
            {conversation.length === 0 ? (
              <motion.div 
                key="hero-view"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-12 md:mt-24 text-left"
              >
                <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tighter leading-[1.1]">
                  Policy intelligence.<br/>
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-200 to-slate-500">Simply delivered.</span>
                </h1>
                <p className="text-slate-400 text-lg md:text-xl max-w-xl leading-[1.6] mb-12">
                  Direct answers from 200+ official government sources. No fluff, just the facts you need.
                </p>

                {/* Main Input - Hero Position */}
                <div className="w-full max-w-3xl mb-8 relative">
                  <form 
                    onSubmit={handleSubmit}
                    className={`bg-[#0d0d0d] border rounded-2xl p-2 flex items-center gap-2 transition-all duration-300 ${inputFocused ? 'border-violet-500/50 shadow-[0_0_30px_rgba(139,92,246,0.15)] bg-[#111]' : 'border-white/10 hover:border-white/20'}`}
                  >
                    <div className="flex-1 relative flex items-center">
                      {!inputValue && !inputFocused && <RotatingPlaceholder />}
                      <input 
                        className="w-full bg-transparent border-none focus:ring-0 px-6 py-4 md:py-5 text-lg md:text-xl font-medium text-white placeholder:text-transparent outline-none relative z-10"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onFocus={() => setInputFocused(true)}
                        onBlur={() => setInputFocused(false)}
                        placeholder="What would you like to know?"
                      />
                    </div>
                    <button 
                      type="submit"
                      disabled={loading || !inputValue.trim()}
                      className="bg-white hover:bg-slate-200 disabled:opacity-20 disabled:hover:bg-white text-black px-6 md:px-8 py-4 md:py-5 rounded-xl font-bold text-xs uppercase tracking-widest transition-all flex items-center gap-2 shrink-0 group"
                    >
                      {loading ? (
                        <><Loader2 className="w-4 h-4 animate-spin" /> Thinking</>
                      ) : (
                        <>Ask <Send className="w-3 h-3 group-hover:translate-x-1 transition-transform" /></>
                      )}
                    </button>
                  </form>
                  {inputFocused && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="absolute -bottom-8 right-4 text-[10px] text-slate-500 font-medium uppercase tracking-widest flex items-center gap-1"
                    >
                      Press Enter <ArrowRight className="w-3 h-3" />
                    </motion.div>
                  )}
                </div>

                {/* Trust Signals */}
                <div className="flex flex-wrap items-center gap-6 mb-12 text-sm font-medium text-slate-400">
                  <div className="flex items-center gap-2">
                    <Landmark className="w-4 h-4 text-violet-400" />
                    <span>200+ Government Sources</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-violet-400" />
                    <span>Verified Citations</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileCheck className="w-4 h-4 text-violet-400" />
                    <span>AI-Powered Precision</span>
                  </div>
                </div>
                
                {/* Suggested Prompts */}
                <div className="space-y-4">
                  <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest flex items-center gap-2">
                    <Sparkles className="w-3 h-3" /> Try Asking
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {suggestedQueries.map((q, i) => (
                      <button 
                        key={i} 
                        onClick={() => setInputValue(q)}
                        className="px-4 py-2.5 bg-white/5 border border-white/5 rounded-full text-sm text-slate-300 hover:text-white hover:border-violet-500/50 hover:bg-violet-500/10 transition-all cursor-pointer"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>

              </motion.div>
            ) : (
              <motion.div 
                key="chat-view"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-16 mt-6 md:mt-10 pb-32"
              >
                {conversation.map((turn) => (
                  <div key={turn.id} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <div className="text-2xl md:text-3xl font-bold text-white tracking-tight leading-tight">
                      {turn.query}
                    </div>

                    <div className="space-y-8 md:pl-8 border-l-2 border-violet-500/20">
                      {turn.result ? (
                        <>
                          <div className="text-lg">
                            <Typewriter text={turn.result.answer} delay={10} />
                          </div>
                          
                          {/* Rich Citations UI */}
                          {turn.result.citations && turn.result.citations.length > 0 && (
                            <div className="pt-6 space-y-3">
                              <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest">
                                <ShieldCheck className="w-4 h-4 text-green-500/70" />
                                Verified in {turn.result.citations.length} Official Source{turn.result.citations.length > 1 ? 's' : ''}
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {turn.result.citations.map((cite, i) => {
                                  const isValidUrl = cite.source_url && cite.source_url !== 'N/A' && cite.source_url.startsWith('http');
                                  
                                  return (
                                    <div key={i} className="group bg-white/[0.02] border border-white/5 rounded-xl p-4 transition-all hover:border-violet-500/30 hover:bg-white/[0.04]">
                                      <div className="flex items-start justify-between gap-4">
                                        <div>
                                          <h4 className="text-sm font-bold text-slate-200 line-clamp-1 group-hover:text-violet-300 transition-colors">{cite.scheme_name}</h4>
                                          <p className="text-xs text-slate-500 mt-1">{cite.ministry}</p>
                                        </div>
                                        {isValidUrl ? (
                                          <a 
                                            href={cite.source_url} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="p-2 bg-white/5 rounded-lg text-slate-400 hover:text-white hover:bg-violet-500/20 transition-all shrink-0"
                                            title="View Source"
                                          >
                                            <ExternalLink className="w-3.5 h-3.5" />
                                          </a>
                                        ) : (
                                          <div className="p-2 text-slate-600 shrink-0" title="Offline Source">
                                            <FileCheck className="w-3.5 h-3.5" />
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                          
                          {/* Follow up suggestions */}
                          <div className="pt-4 border-t border-white/5 mt-8">
                            <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest block mb-3">Related Topics</span>
                            <div className="flex flex-wrap gap-2">
                              {["Eligibility criteria?", "Required documents?", "Application process?"].map((q, idx) => (
                                <button 
                                  key={idx}
                                  onClick={() => setInputValue(`${turn.query} ${q}`)}
                                  className="text-xs px-3 py-1.5 rounded-md bg-white/5 text-slate-400 hover:text-violet-300 hover:bg-violet-500/10 transition-colors"
                                >
                                  {q}
                                </button>
                              ))}
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="flex items-center gap-3 text-violet-400 text-xs font-bold uppercase tracking-[0.2em] py-4">
                          <Loader2 className="w-4 h-4 animate-spin" /> Synthesizing policy data...
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={scrollRef} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sticky Input for Chat View */}
        {conversation.length > 0 && (
          <div className="fixed bottom-0 left-0 right-0 z-50 p-6 bg-gradient-to-t from-[#080808] via-[#080808] to-transparent pointer-events-none">
             <div className="max-w-3xl mx-auto w-full pointer-events-auto">
               <form 
                  onSubmit={handleSubmit}
                  className={`w-full bg-[#111] border rounded-2xl p-2 flex items-center gap-2 transition-all duration-300 shadow-2xl ${inputFocused ? 'border-violet-500/50 shadow-[0_0_30px_rgba(139,92,246,0.15)]' : 'border-white/10 ring-1 ring-black'}`}
                >
                  <div className="flex-1 relative flex items-center">
                    {!inputValue && !inputFocused && (
                      <span className="absolute left-6 text-slate-500 pointer-events-none text-base font-medium">Ask a follow-up...</span>
                    )}
                    <input 
                      className="w-full bg-transparent border-none focus:ring-0 px-6 py-3 text-base md:text-lg font-medium text-white outline-none relative z-10"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onFocus={() => setInputFocused(true)}
                      onBlur={() => setInputFocused(false)}
                    />
                  </div>
                  <button 
                    type="submit"
                    disabled={loading || !inputValue.trim()}
                    className="bg-violet-600 hover:bg-violet-500 disabled:opacity-30 disabled:bg-slate-800 text-white px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-widest transition-all flex items-center gap-2 shrink-0 group"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </button>
                </form>
             </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
