import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const EligibilityWizard = ({ onSearch }) => {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    age: '',
    gender: 'General',
    income: '',
    category: 'Student'
  });

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      const query = `I am a ${form.age} year old ${form.gender} ${form.category} with an annual income of ${form.income}. Which government schemes am I eligible for?`;
      onSearch(query);
    }
  };

  return (
    <div className="w-full max-w-xl text-left py-10">
      <div className="flex justify-between items-center mb-16 border-b border-white/10 pb-6">
        <h2 className="text-sm font-bold text-white uppercase tracking-[0.2em]">Advisor Session</h2>
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Step {step} / 3</span>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          className="space-y-12"
        >
          {step === 1 && (
            <div className="space-y-10">
              <h3 className="text-4xl font-bold text-white tracking-tighter">Who are you?</h3>
              <div className="grid grid-cols-2 gap-8">
                <div className="space-y-4">
                  <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Current Age</span>
                  <input 
                    type="number" 
                    className="w-full bg-transparent border-b border-white/20 pb-4 text-3xl font-bold text-white outline-none focus:border-white transition-all"
                    placeholder="25"
                    value={form.age}
                    onChange={(e) => setForm({...form, age: e.target.value})}
                  />
                </div>
                <div className="space-y-4">
                  <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Gender / Category</span>
                  <select 
                    className="w-full bg-transparent border-b border-white/20 pb-4 text-xl font-bold text-white outline-none focus:border-white transition-all appearance-none"
                    value={form.gender}
                    onChange={(e) => setForm({...form, gender: e.target.value})}
                  >
                    <option value="General">General</option>
                    <option value="Female">Female</option>
                    <option value="SC/ST">SC/ST</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-10">
              <h3 className="text-4xl font-bold text-white tracking-tighter">What's your income?</h3>
              <div className="space-y-4">
                <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Annual (INR)</span>
                <input 
                  type="number" 
                  className="w-full bg-transparent border-b border-white/20 pb-4 text-6xl font-bold text-white outline-none focus:border-white transition-all"
                  placeholder="500000"
                  value={form.income}
                  onChange={(e) => setForm({...form, income: e.target.value})}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-10">
              <h3 className="text-4xl font-bold text-white tracking-tighter">Select your focus</h3>
              <div className="grid grid-cols-2 gap-4">
                {['Student', 'Entrepreneur', 'Farmer', 'Worker'].map(cat => (
                  <button 
                    key={cat}
                    onClick={() => setForm({...form, category: cat})}
                    className={`p-6 border transition-all text-xs font-bold uppercase tracking-widest ${
                      form.category === cat ? 'bg-white text-black border-white' : 'bg-transparent border-white/10 text-slate-500 hover:text-white hover:border-white/30'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      <div className="mt-20 flex items-center gap-12">
        <button 
          onClick={handleNext}
          className="bg-white text-black px-10 py-4 font-bold text-[10px] tracking-widest uppercase hover:bg-slate-200 transition-all flex items-center gap-4"
        >
          {step === 3 ? 'Generate Advice' : 'Continue'}
        </button>
        {step > 1 && (
          <button onClick={() => setStep(step - 1)} className="text-[10px] font-bold text-slate-600 hover:text-white uppercase tracking-widest transition-all">
            Go Back
          </button>
        )}
      </div>
    </div>
  );
};

export default EligibilityWizard;
