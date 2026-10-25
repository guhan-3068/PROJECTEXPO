import React, { useState } from 'react';
import {
  X, ShieldCheck, AlertCircle, CheckCircle2, HelpCircle,
  FileText, Sparkles, Eye, FileQuestion, ArrowRight, Info
} from 'lucide-react';

const LEVEL_CONFIG = {
  'High Confidence': {
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    bar: 'bg-emerald-500',
    icon: CheckCircle2,
    iconColor: 'text-emerald-600',
    desc: 'Analysis results are reliable; scan text and metadata align with expected requirements.'
  },
  'Moderate Confidence': {
    badge: 'bg-amber-100 text-amber-800 border-amber-300',
    bar: 'bg-amber-500',
    icon: AlertCircle,
    iconColor: 'text-amber-600',
    desc: 'Mild variations, partial OCR uncertainty, or minor formatting differences detected.'
  },
  'Low Confidence': {
    badge: 'bg-rose-100 text-rose-800 border-rose-300',
    bar: 'bg-rose-500',
    icon: AlertCircle,
    iconColor: 'text-rose-600',
    desc: 'Significant degradation, low scan resolution, or missing mandatory fields.'
  },
  'Unable to Determine': {
    badge: 'bg-slate-100 text-slate-700 border-slate-300',
    bar: 'bg-slate-400',
    icon: HelpCircle,
    iconColor: 'text-slate-500',
    desc: 'Insufficient data points to evaluate this dimension reliably.'
  }
};

const ConfidenceMeterModal = ({ isOpen, onClose, confidenceData = null, documentTitle = 'Application Documents' }) => {
  const [selectedDocIndex, setSelectedDocIndex] = useState(0);

  if (!isOpen || !confidenceData) return null;

  const docs = confidenceData.documents || [];
  const currentDoc = docs[selectedDocIndex] || docs[0] || null;
  const dims = currentDoc?.dimensions || {};
  const overallLevel = currentDoc?.overall_level || confidenceData.overall_level || 'Unable to Determine';
  const overallScore = currentDoc?.overall_score || confidenceData.mean_score || 0;
  const overallCfg = LEVEL_CONFIG[overallLevel] || LEVEL_CONFIG['Unable to Determine'];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-3xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden max-h-[92vh] flex flex-col animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0f2942] to-[#1e3a8a] text-white p-6 flex items-start justify-between">
          <div className="space-y-1 pr-6">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-orange-500/20 text-orange-300 text-[10px] font-bold border border-orange-400/30">
              <Sparkles className="w-3 h-3 text-orange-400" />
              <span>Explainable AI Reliability Diagnostics</span>
            </div>
            <h2 className="text-lg sm:text-xl font-black leading-snug">
              Verification Confidence Meter
            </h2>
            <p className="text-xs text-slate-300">
              Transparent reliability measurements across 6 dimensions grounded in actual OCR and schema outputs.
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-full transition"
            title="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Document Selector if multiple */}
        {docs.length > 1 && (
          <div className="bg-slate-50 border-b border-slate-200 px-6 py-2.5 flex items-center space-x-2 overflow-x-auto text-xs">
            <span className="font-bold text-slate-500 whitespace-nowrap">Select Document:</span>
            {docs.map((d, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedDocIndex(idx)}
                className={`px-3 py-1.5 rounded-xl font-bold transition whitespace-nowrap ${
                  selectedDocIndex === idx
                    ? 'bg-[#0f2942] text-white shadow-sm'
                    : 'bg-white text-slate-700 hover:bg-slate-200 border border-slate-200'
                }`}
              >
                {d.original_filename}
              </button>
            ))}
          </div>
        )}

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-slate-800">

          {/* 1. Overall Score Banner */}
          <div className={`p-5 rounded-2xl border ${overallCfg.badge} bg-white shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4`}>
            <div className="flex items-center space-x-3.5">
              <div className="p-3 bg-white rounded-2xl shadow-sm border border-slate-200">
                <overallCfg.icon className={`w-7 h-7 ${overallCfg.iconColor}`} />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Automated Analysis Confidence
                  </span>
                  <span className={`text-[11px] font-extrabold px-2 py-0.5 rounded-full border ${overallCfg.badge}`}>
                    {overallLevel}
                  </span>
                </div>
                <div className="text-2xl font-black text-slate-900 mt-0.5">
                  {overallScore}% <span className="text-xs font-semibold text-slate-500">overall reliability</span>
                </div>
                <p className="text-xs text-slate-600 mt-1">
                  {overallCfg.desc}
                </p>
              </div>
            </div>

            <div className="text-left sm:text-right text-[11px] text-slate-400 max-w-xs font-mono bg-slate-50 p-2.5 rounded-xl border border-slate-200">
              {currentDoc?.formula_explanation || 'Weighted composite score across 6 measurable verification dimensions.'}
            </div>
          </div>

          {/* 2. MANDATORY CITIZEN ADVISORY CALLOUT */}
          <div className="p-4 rounded-2xl bg-amber-50/90 border-2 border-amber-300 text-amber-900 space-y-2">
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded-md bg-amber-200/80 text-amber-900 font-black text-xs border border-amber-400/50">
                Official Authenticity: Not Verified
              </span>
              <span className="text-xs font-bold text-amber-800">
                &bull; Mandatory Citizen Advisory
              </span>
            </div>
            <p className="text-xs leading-relaxed text-amber-950">
              A high automated confidence score indicates that your document is crisp, readable, complete, and consistent.
              It <strong>does not prove</strong> that the certificate is legally authentic or that a government department has officially approved it.
              Legal authenticity can only be verified by the issuing authority (e.g. Tahsildar / UIDAI / Parivahan) or via an authorized DigiLocker / e-District API verification.
            </p>
          </div>

          {/* 3. The 6 Individual Measurable Dimensions */}
          <div className="space-y-3">
            <h3 className="text-sm font-black text-[#0f2942] uppercase tracking-wider">
              Six Dimension Reliability Breakdown
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              
              {/* Dim 1: Type Detection */}
              {dims.type_detection && (
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-800">
                      1. Document Type Detection
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${LEVEL_CONFIG[dims.type_detection.level]?.badge || 'bg-slate-100'}`}>
                      {dims.type_detection.score}% ({dims.type_detection.level})
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full ${LEVEL_CONFIG[dims.type_detection.level]?.bar || 'bg-slate-400'}`} style={{ width: `${dims.type_detection.score}%` }} />
                  </div>
                  <div className="text-[11px] text-slate-600 space-y-1">
                    {dims.type_detection.reasons?.map((r, i) => (
                      <div key={i} className="flex items-start space-x-1.5">
                        <span className="text-slate-400">&bull;</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Dim 2: OCR Quality */}
              {dims.ocr_extraction && (
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-800">
                      2. OCR & Text Quality
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${LEVEL_CONFIG[dims.ocr_extraction.level]?.badge || 'bg-slate-100'}`}>
                      {dims.ocr_extraction.score}% ({dims.ocr_extraction.level})
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full ${LEVEL_CONFIG[dims.ocr_extraction.level]?.bar || 'bg-slate-400'}`} style={{ width: `${dims.ocr_extraction.score}%` }} />
                  </div>
                  <div className="text-[11px] text-slate-600 space-y-1">
                    {dims.ocr_extraction.reasons?.map((r, i) => (
                      <div key={i} className="flex items-start space-x-1.5">
                        <span className="text-slate-400">&bull;</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Dim 3: Required-Field Completeness */}
              {dims.field_completeness && (
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-800">
                      3. Required-Field Completeness
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${LEVEL_CONFIG[dims.field_completeness.level]?.badge || 'bg-slate-100'}`}>
                      {dims.field_completeness.score}% ({dims.field_completeness.level})
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full ${LEVEL_CONFIG[dims.field_completeness.level]?.bar || 'bg-slate-400'}`} style={{ width: `${dims.field_completeness.score}%` }} />
                  </div>
                  <div className="text-[11px] text-slate-600 space-y-1">
                    {dims.field_completeness.reasons?.map((r, i) => (
                      <div key={i} className="flex items-start space-x-1.5">
                        <span className="text-slate-400">&bull;</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Dim 4: Cross-Document Consistency */}
              {dims.cross_consistency && (
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-800">
                      4. Cross-Document Consistency
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${LEVEL_CONFIG[dims.cross_consistency.level]?.badge || 'bg-slate-100'}`}>
                      {dims.cross_consistency.score !== null ? `${dims.cross_consistency.score}%` : 'N/A'} ({dims.cross_consistency.level})
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${LEVEL_CONFIG[dims.cross_consistency.level]?.bar || 'bg-slate-400'}`}
                      style={{ width: `${dims.cross_consistency.score || 0}%` }}
                    />
                  </div>
                  <div className="text-[11px] text-slate-600 space-y-1">
                    {dims.cross_consistency.reasons?.map((r, i) => (
                      <div key={i} className="flex items-start space-x-1.5">
                        <span className="text-slate-400">&bull;</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Dim 5: Readability & Scan Quality */}
              {dims.readability && (
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-800">
                      5. Readability & Image Integrity
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${LEVEL_CONFIG[dims.readability.level]?.badge || 'bg-slate-100'}`}>
                      {dims.readability.score}% ({dims.readability.level})
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                    <div className={`h-full ${LEVEL_CONFIG[dims.readability.level]?.bar || 'bg-slate-400'}`} style={{ width: `${dims.readability.score}%` }} />
                  </div>
                  <div className="text-[11px] text-slate-600 space-y-1">
                    {dims.readability.reasons?.map((r, i) => (
                      <div key={i} className="flex items-start space-x-1.5">
                        <span className="text-slate-400">&bull;</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Dim 6: Official Authenticity Verification */}
              {dims.official_authenticity && (
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-800">
                      6. Official Authenticity Status
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 border border-amber-300">
                      Unverified
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-600 leading-snug space-y-1">
                    <p className="font-semibold text-slate-800">
                      Status: {dims.official_authenticity.status}
                    </p>
                    <p>
                      {dims.official_authenticity.legal_advisory}
                    </p>
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 p-4 border-t border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Info className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <span>Scores reflect objective criteria: keyword density, character recognition certainty, and schema field count.</span>
          </div>
          <button
            onClick={onClose}
            className="px-5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white text-xs font-bold rounded-xl transition"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
};

export default ConfidenceMeterModal;
