import React from 'react';
import {
  ShieldCheck, AlertTriangle, CheckCircle, Info, X,
  FileText, Cpu, KeyRound, ExternalLink, Activity
} from 'lucide-react';

const ForensicAuditModal = ({ isOpen, onClose, auditData }) => {
  if (!isOpen || !auditData) return null;

  const evalData = auditData.evaluation || {};
  const dims = evalData.dimensions || {};
  const forensics = auditData.tampering_forensics || {};

  const getStatusBadge = (status, text) => {
    switch (status) {
      case 'PASS':
      case 'READY':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
            <span>{text || 'Pass'}</span>
          </span>
        );
      case 'WARNING':
      case 'PHYSICAL_REQUIRED':
      case 'EXPIRING_SOON':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>{text || 'Review'}</span>
          </span>
        );
      case 'FAIL':
      case 'EXPIRED':
      case 'NEEDS_REVIEW':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
            <span>{text || 'Action Required'}</span>
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full shadow-2xl border border-slate-200 overflow-hidden animate-fadeIn">
        {/* Header */}
        <div className="bg-[#0f2942] text-white p-5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-base font-bold">Individual Document Forensic Audit</h3>
              <p className="text-xs text-slate-300">
                {auditData.filename} &bull; Rules Version: {evalData.rules_version || '2026.4'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Authenticity Screening Headline */}
          <div className={`p-4 rounded-xl border flex items-start space-x-3 ${
            forensics.authenticity_result === 'No obvious manipulation detected'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : forensics.authenticity_result === 'Inconclusive — further verification required'
              ? 'bg-amber-50 border-amber-200 text-amber-900'
              : 'bg-rose-50 border-rose-200 text-rose-900'
          }`}>
            <Activity className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider">
                  Tampering & Authenticity Verdict
                </span>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-white/80 border">
                  Risk Level: {forensics.risk_level || 'LOW'}
                </span>
              </div>
              <p className="text-sm font-black mt-1">
                {forensics.authenticity_result}
              </p>
              <p className="text-xs mt-1 opacity-90">
                {forensics.explanation}
              </p>
            </div>
          </div>

          {/* 6 Evaluation Dimensions Grid */}
          <div>
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-3">
              6-Dimension Verification Evaluation
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* 1. Type Detection */}
              {dims.type_detection && (
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-800">1. Document Type</span>
                    {getStatusBadge(dims.type_detection.status, dims.type_detection.identified_type)}
                  </div>
                  <p className="text-[11px] text-slate-600">{dims.type_detection.note}</p>
                </div>
              )}

              {/* 2. Fields Extraction */}
              {dims.fields_extraction && (
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-800">2. Required Fields</span>
                    {getStatusBadge(dims.fields_extraction.status, `${dims.fields_extraction.total_extracted_count} Extracted`)}
                  </div>
                  <p className="text-[11px] text-slate-600">{dims.fields_extraction.note}</p>
                </div>
              )}

              {/* 3. Validity & Expiry */}
              {dims.validity_expiry && (
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-800">3. Validity & Expiry</span>
                    {getStatusBadge(dims.validity_expiry.status, dims.validity_expiry.label)}
                  </div>
                  <p className="text-[11px] text-slate-600">{dims.validity_expiry.note}</p>
                </div>
              )}

              {/* 4. Readability & Quality */}
              {dims.readability_quality && (
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-800">4. Readability & Quality</span>
                    {getStatusBadge(dims.readability_quality.status, dims.readability_quality.label)}
                  </div>
                  <p className="text-[11px] text-slate-600">{dims.readability_quality.note}</p>
                </div>
              )}

              {/* 5. Document Authenticity Screening */}
              {dims.authenticity_screening && (
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-800">5. Authenticity Screening</span>
                    {getStatusBadge(dims.authenticity_screening.status, forensics.authenticity_result)}
                  </div>
                  <p className="text-[11px] text-slate-600">ELA score: {dims.authenticity_screening.ela_anomaly_score}</p>
                </div>
              )}

              {/* 6. Official Verification Readiness */}
              {dims.official_readiness && (
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-800">6. Official Readiness</span>
                    {getStatusBadge(dims.official_readiness.status, dims.official_readiness.label)}
                  </div>
                  <p className="text-[11px] text-slate-600">{dims.official_readiness.note}</p>
                </div>
              )}
            </div>
          </div>

          {/* AI Generator & Digital Signature Evidence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl border border-slate-200 bg-white">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-800 mb-1">
                <Cpu className="w-4 h-4 text-indigo-600" />
                <span>AI-Generation Screening</span>
              </div>
              <p className="text-xs text-slate-600 font-medium">
                {forensics.ai_generation_screening || 'No synthetic generative signatures identified'}
              </p>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-200 bg-white">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-800 mb-1">
                <KeyRound className="w-4 h-4 text-emerald-600" />
                <span>Digital Signature Status</span>
              </div>
              <p className="text-xs text-slate-600 font-medium">
                {forensics.digital_signature_status || 'No digital signature (Standard paper copy)'}
              </p>
            </div>
          </div>

          {/* Masked Extracted Fields */}
          {dims.fields_extraction?.masked_fields && Object.keys(dims.fields_extraction.masked_fields).length > 0 && (
            <div>
              <h4 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-2">
                Extracted Details (Privacy Masked)
              </h4>
              <div className="bg-slate-50 rounded-xl border border-slate-200 p-3 divide-y divide-slate-200/60">
                {Object.entries(dims.fields_extraction.masked_fields).map(([k, v]) => (
                  <div key={k} className="py-1.5 flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-600 capitalize">
                      {k.replace(/_/g, ' ')}
                    </span>
                    <span className="font-mono font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {v}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detected Issues & Guidance */}
          {evalData.detected_issues && evalData.detected_issues.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs">
              <h4 className="font-bold text-amber-900 mb-1 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Detected Issues & Discrepancies</span>
              </h4>
              <ul className="list-disc list-inside text-amber-800 space-y-1 mt-2">
                {evalData.detected_issues.map((iss, i) => (
                  <li key={i}>{iss}</li>
                ))}
              </ul>
              {evalData.suggested_corrections && evalData.suggested_corrections.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-amber-200 text-amber-900">
                  <span className="font-bold">How to correct:</span>
                  <ul className="list-disc list-inside space-y-1 mt-1 text-amber-800">
                    {evalData.suggested_corrections.map((corr, i) => (
                      <li key={i}>{corr}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Legal / Non-Certification Disclaimer */}
          <div className="p-3.5 rounded-xl bg-slate-100 text-[11px] text-slate-500 leading-relaxed border border-slate-200">
            <strong>Citizen Advisory Notice:</strong> {evalData.disclaimer || 'Absence of suspicious tampering indicators does not constitute official government authenticity certification. Official validation is conducted directly by issuing government authorities upon application submission.'}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white text-xs font-bold rounded-xl transition"
          >
            Close Audit Scorecard
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForensicAuditModal;
