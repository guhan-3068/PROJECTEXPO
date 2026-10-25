import React from 'react';
import { ShieldAlert, ShieldCheck, AlertOctagon, Info } from 'lucide-react';

const TamperAlert = ({ tamperingFlags = [] }) => {
  const flagged = tamperingFlags.filter((t) => t.is_flagged);

  if (flagged.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
        <div className="inline-flex p-3 rounded-full bg-emerald-50 text-emerald-600 mb-2">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h3 className="text-sm font-semibold text-slate-900">Document Integrity Cleared</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          No graphic editing signatures (Photoshop, Canva) or abnormal Error Level Analysis (ELA) compression deltas were found.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-rose-200 overflow-hidden">
      <div className="p-5 bg-rose-50/50 border-b border-rose-100 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <ShieldAlert className="w-5 h-5 text-rose-600" />
          <div>
            <h2 className="text-base font-bold text-rose-950">Structural Anomaly & Tampering Screening</h2>
            <p className="text-xs text-rose-700">Advisory automated screening – Manual human adjudication required</p>
          </div>
        </div>
        <span className="text-xs font-bold px-2.5 py-1 rounded bg-rose-200 text-rose-900">
          {flagged.length} Flagged Case{flagged.length === 1 ? '' : 's'}
        </span>
      </div>

      <div className="p-5 space-y-4">
        {flagged.map((item, idx) => (
          <div key={idx} className="p-4 rounded-lg border border-rose-200 bg-white space-y-2.5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-sm text-slate-900">{item.document_name}</span>
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded ${
                  item.risk_level === 'HIGH'
                    ? 'bg-rose-100 text-rose-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {item.risk_level} RISK FLAGGED
              </span>
            </div>

            {item.software_detected && (
              <div className="text-xs text-slate-600 flex items-center space-x-1.5">
                <AlertOctagon className="w-3.5 h-3.5 text-rose-500" />
                <span>Detected Editing Tool: <strong className="text-slate-800">{item.software_detected}</strong></span>
              </div>
            )}

            {item.ela_score > 0 && (
              <div className="text-xs text-slate-500">
                Error Level Analysis (ELA) Variance: <strong className="text-slate-700">{item.ela_score}</strong>
              </div>
            )}

            <p className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200">
              <strong>Forensic Reason:</strong> {item.explanation}
            </p>

            <div className="p-2.5 rounded bg-amber-50 text-[11px] text-amber-800 flex items-start space-x-2 border border-amber-200">
              <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600" />
              <span>
                <strong>Important Policy:</strong> This flag does not constitute confirmed fraud. An administrator will review original physical records before making any final determination.
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TamperAlert;
