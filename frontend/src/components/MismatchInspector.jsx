import React from 'react';
import { UserCheck, AlertTriangle, HelpCircle, FileText } from 'lucide-react';

const MismatchInspector = ({ mismatches = [] }) => {
  if (mismatches.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
        <div className="inline-flex p-3 rounded-full bg-emerald-50 text-emerald-600 mb-2">
          <UserCheck className="w-6 h-6" />
        </div>
        <h3 className="text-sm font-semibold text-slate-900">Zero Information Mismatches</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Names, dates of birth, and identity records match consistently across all uploaded documents.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Cross-Document Identity Consistency</h2>
          <p className="text-xs text-slate-500 mt-0.5">Automated comparison of names, birth dates, and identity fields across submitted files</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-amber-50 text-amber-800 border border-amber-200">
          {mismatches.length} Discrepanc{mismatches.length === 1 ? 'y' : 'ies'} Detected
        </span>
      </div>

      <div className="divide-y divide-slate-100">
        {mismatches.map((item, idx) => (
          <div key={idx} className="p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  {item.display_field}
                </span>
                {item.requires_manual_review ? (
                  <span className="inline-flex items-center text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded">
                    <AlertTriangle className="w-3.5 h-3.5 mr-1 text-rose-500" />
                    Manual Review Required
                  </span>
                ) : (
                  <span className="inline-flex items-center text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                    <HelpCircle className="w-3.5 h-3.5 mr-1 text-amber-500" />
                    Acceptable Variation
                  </span>
                )}
              </div>
              <span className="text-xs text-slate-400">
                Similarity: <strong className="text-slate-700">{Math.round(item.similarity_score * 100)}%</strong>
              </span>
            </div>

            {/* Comparison Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
              <div className="space-y-1">
                <div className="flex items-center space-x-1.5 text-slate-500 font-medium">
                  <FileText className="w-3.5 h-3.5" />
                  <span>{item.document_a_name}</span>
                </div>
                <div className="p-2 bg-white rounded border border-slate-200 font-mono text-slate-900 font-semibold break-all">
                  {item.document_a_value || '<Not specified>'}
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center space-x-1.5 text-slate-500 font-medium">
                  <FileText className="w-3.5 h-3.5" />
                  <span>{item.document_b_name}</span>
                </div>
                <div className="p-2 bg-white rounded border border-slate-200 font-mono text-slate-900 font-semibold break-all">
                  {item.document_b_value || '<Not specified>'}
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-600 bg-amber-50/50 p-2.5 rounded border border-amber-100">
              <strong>Evaluation:</strong> {item.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MismatchInspector;
