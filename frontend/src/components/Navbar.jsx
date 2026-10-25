import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck, User, LogOut, LayoutDashboard, ShieldAlert, Sparkles,
  FolderCheck, Compass, Globe, BookOpen, HelpCircle, CheckSquare,
  Radio, Calendar
} from 'lucide-react';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 shadow-sm bg-white border-b border-slate-200">
      {/* Tri-color Top Strip */}
      <div className="h-1 w-full flex">
        <div className="w-1/3 bg-[#ea580c]"></div>
        <div className="w-1/3 bg-slate-200"></div>
        <div className="w-1/3 bg-[#16a34a]"></div>
      </div>

      {/* Non-Affiliation Disclaimer Banner */}
      <div className="bg-slate-100/90 text-slate-600 text-[10px] sm:text-[11px] py-1 px-4 text-center border-b border-slate-200 font-medium">
        <span className="font-bold text-slate-700">Official Advisory:</span> QUBIX is an independent document-readiness assistance tool. It is not a government website and does not issue, approve, or authenticate government documents.
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo & Portal Title */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-3 transition group">
              <img 
                src="/qubix-logo.png" 
                alt="QUBIX Logo" 
                className="h-10 w-10 sm:h-11 sm:w-11 object-contain rounded-xl shadow-sm bg-white p-0.5 border border-slate-200 group-hover:scale-105 transition-transform"
              />
              <div className="flex flex-col">
                <span className="font-black text-lg sm:text-xl text-[#0f2942] tracking-wider leading-tight">
                  QUBIX
                </span>
                <span className="text-[9px] sm:text-[9.5px] text-slate-500 font-semibold tracking-wider uppercase">
                  Smart Document Verification System
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          {user ? (
            <div className="flex items-center space-x-1 sm:space-x-2">
              <Link
                to="/pre-check"
                className={`flex items-center space-x-1.5 text-xs font-bold px-3 py-1.5 rounded-xl transition ${
                  location.pathname === '/pre-check'
                    ? 'bg-[#ea580c] text-white shadow-sm'
                    : 'bg-orange-50 text-[#ea580c] hover:bg-orange-100 border border-orange-200'
                }`}
              >
                <CheckSquare className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Check Before You Apply</span>
                <span className="sm:hidden">Pre-Check</span>
              </Link>

              <Link
                to="/dashboard"
                className={`flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition ${
                  location.pathname === '/dashboard'
                    ? 'bg-slate-100 text-[#0f2942] font-bold'
                    : 'text-slate-700 hover:text-brand-600 hover:bg-slate-50'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span className="hidden lg:inline">Dashboard</span>
              </Link>

              <Link
                to="/rule-radar"
                className={`hidden md:flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition ${
                  location.pathname === '/rule-radar'
                    ? 'bg-orange-50 text-[#ea580c] font-bold border border-orange-200'
                    : 'text-slate-700 hover:text-orange-600 hover:bg-slate-50'
                }`}
              >
                <Radio className="w-3.5 h-3.5 text-orange-500" />
                <span>Rule Radar</span>
              </Link>

              <Link
                to="/document-timeline"
                className={`hidden md:flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition ${
                  location.pathname === '/document-timeline'
                    ? 'bg-blue-50 text-blue-700 font-bold border border-blue-200'
                    : 'text-slate-700 hover:text-blue-600 hover:bg-slate-50'
                }`}
              >
                <Calendar className="w-3.5 h-3.5 text-blue-500" />
                <span>Timeline</span>
              </Link>

              <Link
                to="/official-services"
                className={`hidden md:flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition ${
                  location.pathname === '/official-services'
                    ? 'bg-slate-100 text-[#0f2942] font-bold'
                    : 'text-slate-700 hover:text-brand-600 hover:bg-slate-50'
                }`}
              >
                <Globe className="w-3.5 h-3.5" />
                <span>Official Portals</span>
              </Link>

              <Link
                to="/correction-guidance"
                className={`hidden lg:flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition ${
                  location.pathname === '/correction-guidance'
                    ? 'bg-slate-100 text-[#0f2942] font-bold'
                    : 'text-slate-700 hover:text-brand-600 hover:bg-slate-50'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Correction Guides</span>
              </Link>

              <Link
                to="/help-faq"
                className={`hidden xl:flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition ${
                  location.pathname === '/help-faq'
                    ? 'bg-slate-100 text-[#0f2942] font-bold'
                    : 'text-slate-700 hover:text-brand-600 hover:bg-slate-50'
                }`}
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>FAQ</span>
              </Link>

              {isAdmin && (
                <Link
                  to="/admin"
                  className="flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100 transition"
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                  <span className="hidden md:inline">Admin</span>
                </Link>
              )}

              <div className="flex items-center space-x-2 border-l border-slate-200 pl-2 sm:pl-3">
                <div className="flex flex-col text-right hidden sm:flex">
                  <span className="text-xs font-bold text-slate-900">{user.full_name}</span>
                  <span className="text-[9.5px] text-slate-500 font-medium">
                    {user.role === 'ADMIN' ? 'Officer / Admin' : 'Citizen Applicant'}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3">
              <Link
                to="/login"
                className="text-xs font-bold text-slate-700 hover:text-[#0f2942] px-3 py-1.5 rounded-lg transition"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="text-xs font-bold bg-[#0f2942] hover:bg-[#1e3a8a] text-white px-4 py-2 rounded-xl transition shadow-sm"
              >
                Citizen Registration
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
