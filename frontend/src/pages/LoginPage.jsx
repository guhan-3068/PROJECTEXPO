import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Lock, Mail, AlertCircle, ArrowRight, Sparkles } from 'lucide-react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate('/dashboard');
    } catch (err) {
      if (!err.response) {
        setError('Cannot reach backend server. Please ensure the backend is running on http://127.0.0.1:8000.');
      } else {
        setError(err.response.data?.detail || 'Invalid email or password');
      }
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full space-y-6 bg-white p-8 rounded-3xl shadow-sm border border-slate-200">
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-1">
            <img 
              src="/qubix-logo.png" 
              alt="QUBIX Logo" 
              className="h-24 w-24 object-contain drop-shadow-md rounded-2xl p-1 bg-white border border-slate-100"
            />
          </div>
          <h1 className="text-2xl font-black text-[#0f2942] tracking-wider">
            Sign in to QUBIX
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Smart Document Verification System for Indian Citizens
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-3.5 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                placeholder="citizen@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-3.5 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-[#0f2942] hover:bg-[#1e3a8a] text-white font-bold rounded-xl text-xs sm:text-sm shadow-md transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <span>{loading ? 'Verifying Credentials...' : 'Sign In to Citizen Portal'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Account Quick-Fill Buttons */}
        <div className="pt-3 border-t border-slate-100">
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center mb-2.5">
            One-Click Instant Demo Access
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => fillCredentials('demo@qubix.ai', 'Password123!')}
              className="px-3 py-2 text-xs font-bold rounded-xl border border-slate-200 hover:border-[#0f2942] hover:bg-slate-50 text-slate-700 transition text-center"
            >
              👤 Citizen Demo
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('admin@qubix.ai', 'AdminPassword123!')}
              className="px-3 py-2 text-xs font-bold rounded-xl border border-amber-200 hover:border-amber-500 hover:bg-amber-50 text-amber-800 transition text-center"
            >
              🛡️ Officer Demo
            </button>
          </div>
          <p className="text-[10px] text-slate-400 text-center mt-2">
            Auto-fills: <code>demo@qubix.ai</code> / <code>Password123!</code>
          </p>
        </div>

        <div className="text-center pt-2">
          <p className="text-xs text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-[#0f2942] hover:underline">
              Create citizen profile
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
