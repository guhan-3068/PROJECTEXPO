import React, { useState, useEffect } from 'react';
import { X, ExternalLink, ShieldAlert, CheckCircle, FileText, ArrowRight, UserCheck, AlertTriangle, Building, HelpCircle, Sparkles, AlertCircle } from 'lucide-react';
import { applicationsApi } from '../services/api';

const HowToFixModal = ({ isOpen, onClose, guideId = 'name_mismatch', customIssueTitle = null }) => {
  const [guide, setGuide] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lang, setLang] = useState('en'); // 'en' or 'ta'

  useEffect(() => {
    if (isOpen && guideId) {
      fetchGuide(guideId);
    }
  }, [isOpen, guideId]);

  const fetchGuide = async (id) => {
    setLoading(true);
    try {
      const data = await applicationsApi.getCorrectionGuide(id);
      setGuide(data);
    } catch (err) {
      console.error('Failed to fetch guide', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const sections = guide?.sections || {};

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden max-h-[90vh] flex flex-col animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0f2942] to-[#1e3a8a] text-white p-6 flex items-start justify-between">
          <div className="space-y-1 pr-6">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-orange-500/20 text-orange-300 text-[10px] font-bold border border-orange-400/30">
              <Sparkles className="w-3 h-3 text-orange-400" />
              <span>Official Citizen Correction Guide</span>
            </div>
            <h2 className="text-lg sm:text-xl font-black leading-snug">
              {lang === 'ta' && guide?.title_ta ? guide.title_ta : (customIssueTitle || guide?.title || 'How to Fix This Issue')}
            </h2>
            <p className="text-xs text-slate-300">
              {lang === 'ta' && guide?.summary_ta ? guide.summary_ta : guide?.summary}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            {/* Bilingual Toggle */}
            <div className="flex items-center bg-white/10 rounded-xl p-0.5 border border-white/20 text-xs font-bold">
              <button
                onClick={() => setLang('en')}
                className={`px-2.5 py-1 rounded-lg transition ${lang === 'en' ? 'bg-[#ea580c] text-white shadow' : 'text-slate-300 hover:text-white'}`}
              >
                English
              </button>
              <button
                onClick={() => setLang('ta')}
                className={`px-2.5 py-1 rounded-lg transition ${lang === 'ta' ? 'bg-[#ea580c] text-white shadow' : 'text-slate-300 hover:text-white'}`}
              >
                தமிழ்
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition"
              title="Close guide"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-slate-800 text-xs sm:text-sm">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-3 border-[#0f2942]/20 border-t-[#0f2942] rounded-full animate-spin" />
              <span className="text-xs text-slate-500">Loading verified correction steps...</span>
            </div>
          ) : (
            <>
              {/* Point 1: What is the issue */}
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center space-x-1.5 text-slate-900 font-extrabold text-xs">
                  <AlertCircle className="w-4 h-4 text-[#ea580c]" />
                  <span>1. {lang === 'ta' ? 'பிரச்சினை என்ன?' : 'What is the issue?'}</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed pl-5">
                  {lang === 'ta' && sections.what_is_issue_ta ? sections.what_is_issue_ta : sections.what_is_issue}
                </p>
              </div>

              {/* Point 2: Why it causes a problem */}
              <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-1">
                <div className="flex items-center space-x-1.5 text-amber-900 font-extrabold text-xs">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>2. {lang === 'ta' ? 'இது ஏன் பிரச்சினையை ஏற்படுத்தும்?' : 'Why could this cause a problem during application?'}</span>
                </div>
                <p className="text-xs text-amber-800 leading-relaxed pl-5">
                  {lang === 'ta' && sections.why_it_causes_problem_ta ? sections.why_it_causes_problem_ta : sections.why_it_causes_problem}
                </p>
              </div>

              {/* Point 3 & 4: Which doc & Who is authorized */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-1 shadow-sm">
                  <div className="flex items-center space-x-1.5 text-slate-900 font-bold text-xs">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span>3. {lang === 'ta' ? 'கவனிக்க வேண்டிய ஆவணம்' : 'Which document needs attention?'}</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed pl-5">
                    {lang === 'ta' && sections.which_doc_needs_attention_ta ? sections.which_doc_needs_attention_ta : sections.which_doc_needs_attention}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-1 shadow-sm">
                  <div className="flex items-center space-x-1.5 text-slate-900 font-bold text-xs">
                    <UserCheck className="w-4 h-4 text-emerald-600" />
                    <span>4. {lang === 'ta' ? 'திருத்தம் செய்ய தகுதியானவர் யார்?' : 'Who is authorised to correct it?'}</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed pl-5 whitespace-pre-line">
                    {lang === 'ta' && sections.who_is_authorized_ta ? sections.who_is_authorized_ta : sections.who_is_authorized}
                  </p>
                </div>
              </div>

              {/* Point 5: Official Correction Process */}
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center space-x-1.5 text-slate-900 font-extrabold text-xs">
                  <Building className="w-4 h-4 text-[#0f2942]" />
                  <span>5. {lang === 'ta' ? 'அதிகாரப்பூர்வ திருத்த வழிமுறைகள்' : 'Official Step-by-Step Correction Process'}</span>
                </div>
                <div className="space-y-2 pl-2">
                  {(lang === 'ta' && sections.official_correction_process_ta
                    ? sections.official_correction_process_ta
                    : sections.official_correction_process || []
                  ).map((step, idx) => (
                    <div key={idx} className="flex items-start space-x-2 text-xs text-slate-700 leading-relaxed">
                      <span className="w-5 h-5 rounded-full bg-[#0f2942] text-white flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-0.5">
                        {idx + 1}
                      </span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Point 6: Supporting Documents Needed */}
              <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-2 shadow-sm">
                <div className="flex items-center space-x-1.5 text-slate-900 font-extrabold text-xs">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span>6. {lang === 'ta' ? 'தேவையான துணை ஆவணங்கள்' : 'Which supporting documents may be needed?'}</span>
                </div>
                <ul className="space-y-1.5 pl-6 list-disc text-xs text-slate-600">
                  {(lang === 'ta' && sections.supporting_docs_needed_ta
                    ? sections.supporting_docs_needed_ta
                    : sections.supporting_docs_needed || []
                  ).map((doc, idx) => (
                    <li key={idx}>{doc}</li>
                  ))}
                </ul>
              </div>

              {/* Point 7: Where to find official service */}
              {sections.official_service_portal && (
                <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-0.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700">
                      7. {lang === 'ta' ? 'அதிகாரப்பூர்வ அரசு இணையதளம்' : 'Official Correction Portal'}
                    </span>
                    <h4 className="text-xs font-bold text-slate-900">
                      {sections.official_service_name || 'Official Portal'}
                    </h4>
                  </div>
                  <a
                    href={sections.official_service_portal}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 px-4 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition shadow-sm self-start sm:self-auto"
                  >
                    <span>Open Official Portal</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              )}

              {/* Point 8 & 9: After correction & Recheck */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-xs font-bold text-slate-900">
                    8. {lang === 'ta' ? 'திருத்தம் செய்த பிறகு செய்ய வேண்டியவை' : 'What to do after correction?'}
                  </span>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {lang === 'ta' && sections.after_correction_ta ? sections.after_correction_ta : sections.after_correction}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-xs font-bold text-slate-900">
                    9. {lang === 'ta' ? 'விண்ணப்பிக்கும் முன் சரிபார்க்க வேண்டியவை' : 'Details to check again before applying'}
                  </span>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {sections.what_to_recheck}
                  </p>
                </div>
              </div>

              {/* Safety Advisory Banner */}
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-start space-x-2 text-[11px] text-rose-800">
                <ShieldAlert className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Citizen Safety Alert:</strong> Never modify an official government certificate PDF using photo-editing or PDF editing software. Submitting an altered image can lead to criminal disqualification. Always apply through official channels. QUBIX never asks for your password or OTP.
                </span>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex items-center justify-between">
          <span className="text-[11px] text-slate-500">
            Official government procedures may vary slightly by state authority.
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold transition"
          >
            Close Guide
          </button>
        </div>

      </div>
    </div>
  );
};

export default HowToFixModal;
