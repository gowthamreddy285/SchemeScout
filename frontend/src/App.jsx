import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Search, 
  ExternalLink, 
  RotateCcw, 
  Loader2,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = 'http://localhost:8000';

const App = () => {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [filters, setFilters] = useState({ state: 'Central', section: '' });
  const scrollRef = useRef(null);

  const states = ['Central', 'Karnataka', 'Tamil Nadu', 'Maharashtra', 'Delhi'];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation, loading]);

  const handleSubmit = async (e, forcedQuery = null) => {
    if (e) e.preventDefault();
    const query = forcedQuery || inputValue;
    if (!query.trim() || loading) return;

    const newTurn = { query, result: null, id: Date.now() };
    setConversation(prev => [...prev, newTurn]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query,
        filters: filters.state ? { state: filters.state } : null
      });
      setConversation(prev => prev.map(turn => 
        turn.id === newTurn.id ? { ...turn, result: response.data } : turn
      ));
    } catch (error) {
      setConversation(prev => prev.map(turn => 
        turn.id === newTurn.id ? { ...turn, result: { answer: "Server connection failed. Is the backend running?", citations: [] } } : turn
      ));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-200 selection:bg-indigo-500/30 font-sans pb-20">
      {/* Top Bar */}
      <div className="max-w-4xl mx-auto px-6 pt-12 flex justify-between items-center mb-16">
        <div className="flex items-center gap-2">
          <div className="bg-indigo-600 p-1 rounded-md">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">SchemeScout</span>
        </div>
        {conversation.length > 0 && (
          <button 
            onClick={() => setConversation([])}
            className="text-xs font-bold text-slate-500 hover:text-white flex items-center gap-2 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> RESET
          </button>
        )}
      </div>

      <div className="max-w-2xl mx-auto px-6">
        {/* Initial Hero */}
        {conversation.length === 0 && (
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
              Search Indian Policies.
            </h1>
            <p className="text-slate-500 text-lg">
              Instant answers from 92+ official government schemes.
            </p>
          </div>
        )}

        {/* Conversation List */}
        <div className="space-y-16 mb-12">
          {conversation.map((turn) => (
            <div key={turn.id} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* User Side */}
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-400 shrink-0">YOU</div>
                <div className="text-xl font-medium text-white leading-snug">
                  {turn.query}
                </div>
              </div>

              {/* AI Side */}
              <div className="flex items-start gap-4 pl-12 border-l-2 border-indigo-500/20">
                <div className="flex-1">
                  {turn.result ? (
                    <div className="space-y-6">
                      <div className="text-slate-300 text-lg leading-relaxed whitespace-pre-wrap">
                        {turn.result.answer}
                      </div>
                      
                      {/* Sources */}
                      <div className="flex flex-wrap gap-2 pt-4 border-t border-white/5">
                        {turn.result.citations?.map((cite, i) => (
                          <a 
                            key={i} 
                            href={cite.source_url} 
                            target="_blank" 
                            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-white/5 text-[11px] font-bold text-slate-400 hover:text-indigo-400 hover:border-indigo-500/30 transition-all"
                          >
                            {cite.scheme_name} <ExternalLink className="w-3 h-3" />
                          </a>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-slate-500 text-sm italic animate-pulse">
                      <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={scrollRef} />
        </div>

        {/* Input Area - Floats at bottom when chat starts, or stays in middle */}
        <div className={`transition-all duration-500 ${conversation.length > 0 ? 'sticky bottom-8' : ''}`}>
          <form 
            onSubmit={handleSubmit}
            className="bg-[#111] border border-white/10 rounded-2xl p-3 flex items-center gap-3 shadow-2xl focus-within:border-indigo-500/50 transition-all max-w-3xl mx-auto"
          >
            <input 
              className="flex-1 bg-transparent border-none focus:ring-0 px-6 py-5 text-xl font-medium text-white placeholder:text-slate-600 outline-none"
              placeholder="Ask a question about central government schemes..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <button 
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white px-8 py-4 rounded-xl font-bold transition-all flex items-center gap-2"
            >
              ASK
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default App;
