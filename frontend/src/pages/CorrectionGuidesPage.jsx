import React, { useState, useEffect } from 'react';
import {
  HelpCircle, Search, ArrowRight, ShieldCheck, CheckCircle2,
  AlertTriangle, BookOpen, ExternalLink, Sparkles, Languages
} from 'lucide-react';
import { applicationsApi } from '../services/api';
import HowToFixModal from '../components/HowToFixModal';

const CorrectionGuidesPage = () => {
  const [guides, setGuides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [lang, setLang] = useState('en'); // 'en' or 'ta'
  const [selectedGuideId, setSelectedGuideId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchGuides();
  }, []);

  const fetchGuides = async () => {
    setLoading(true);
    try {
      const data = await applicationsApi.getCorrectionGuides();
      setGuides(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openGuide = (guideId) => {
    setSelectedGuideId(guideId);
    setIsModalOpen(true);
  };

  const filteredGuides = guides.filter((g) => {
    const q = searchQuery.toLowerCase();
    const title = (g.title || '').toLowerCase();
    const titleTa = (g.title_ta || '').toLowerCase();
    const summary = (g.summary || '').toLowerCase();
    return title.includes(q) || titleTa.includes(q) || summary.includes(q);
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-br from-[#0f2942] via-[#1e3a8a] to-[#0f2942] rounded-3xl p-6 sm:p-8 text-white shadow-md border border-slate-700 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-semibold text-orange-300 border border-white/10">
              <Sparkles className="w-3.5 h-3.5 text-orange-400" />
              <span>How to Fix Documents – Citizen Knowledge Base</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              Official Document Correction Guidance
            </h1>
            <p className="text-xs sm:text-sm text-slate-200 max-w-2xl leading-relaxed">
              Step-by-step instructions on correcting spelling differences, renewing expired certificates, updating Aadhaar, PAN, driving licenses, and obtaining Tahsildar e-Sevai revenue certificates.
            </p>
          </div>

          {/* Global Language Toggle */}
          <div className="flex items-center space-x-2 bg-white/10 p-1.5 rounded-2xl border border-white/20 self-start sm:self-center">
            <Languages className="w-4 h-4 text-orange-400 ml-1.5" />
            <button
              onClick={() => setLang('en')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                lang === 'en' ? 'bg-[#ea580c] text-white shadow' : 'text-slate-200 hover:text-white'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLang('ta')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                lang === 'ta' ? 'bg-[#ea580c] text-white shadow' : 'text-slate-200 hover:text-white'
              }`}
            >
              தமிழ் (Tamil)
            </button>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search correction guide (e.g., name mismatch, Aadhaar update, PAN error, expired DL, income cert)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
          />
        </div>
        <span className="text-xs font-bold text-slate-500">
          Showing {filteredGuides.length} Correction Guides
        </span>
      </div>

      {/* Guides Grid */}
      {loading ? (
        <div className="py-16 text-center text-slate-500 text-xs">
          Loading official correction guides...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredGuides.map((g) => {
            const sections = g.sections || {};
            const title = lang === 'ta' && g.title_ta ? g.title_ta : g.title;
            const summary = lang === 'ta' && g.summary_ta ? g.summary_ta : g.summary;

            return (
              <div
                key={g.id}
                className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:border-brand-500 hover:shadow-md transition flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-orange-50 text-[#ea580c] border border-orange-200 uppercase">
                      {g.issue_type || 'CORRECTION'}
                    </span>
                    <span className="text-[10px] text-slate-400 font-bold">
                      9-Point Checklist
                    </span>
                  </div>

                  <div>
                    <h3 className="font-black text-base text-slate-900 group-hover:text-brand-600 transition leading-snug">
                      {title}
                    </h3>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed line-clamp-3">
                      {summary}
                    </p>
                  </div>

                  {/* Highlights */}
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-[11px] text-slate-600 space-y-1">
                    <div>
                      <strong>Authorized Authority:</strong>{' '}
                      <span className="line-clamp-1">{sections.who_is_authorized?.split('\n')[0] || 'Government Authority'}</span>
                    </div>
                    {sections.official_service_name && (
                      <div>
                        <strong>Portal:</strong> {sections.official_service_name}
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <button
                    onClick={() => openGuide(g.id)}
                    className="text-xs font-bold text-slate-600 hover:text-brand-600 transition flex items-center space-x-1"
                  >
                    <BookOpen className="w-3.5 h-3.5 mr-1" />
                    <span>View 9 Points</span>
                  </button>

                  <button
                    onClick={() => openGuide(g.id)}
                    className="px-3.5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-sm"
                  >
                    <span>How to Fix This?</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Guide Modal */}
      <HowToFixModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        guideId={selectedGuideId}
      />
    </div>
  );
};

export default CorrectionGuidesPage;
