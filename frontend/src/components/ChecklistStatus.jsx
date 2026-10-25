import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, ArrowRight, Info, AlertTriangle, ShieldCheck } from 'lucide-react';

const ChecklistStatus = ({ satisfied = [], missing = [], overallStatus = 'INCOMPLETE', recommendedActions = [] }) => {
  const isComplete = overallStatus === 'COMPLETE';
  const isReview = overallStatus === 'REVIEW_REQUIRED';

  const mandatoryMissing = missing.filter((m) => m.requirement_type === 'REQUIRED' || m.is_mandatory);
  const conditionalMissing = missing.filter((m) => m.requirement_type === 'CONDITIONALLY_REQUIRED');
  const optionalMissing = missing.filter((m) => m.requirement_type === 'OPTIONAL' && !m.is_mandatory);

  const getTypeBadge = (type, isMandatory) => {
    if (type === 'REQUIRED' || (isMandatory && type !== 'CONDITIONALLY_REQUIRED')) {
      return (
        <span className="text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200 px-2 py-0.5 rounded-full">
          Required
        </span>
      );
    }
    if (type === 'CONDITIONALLY_REQUIRED') {
      return (
        <span className="text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200 px-2 py-0.5 rounded-full">
          Conditionally Required
        </span>
      );
    }
    return (
      <span className="text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200 px-2 py-0.5 rounded-full">
        Optional / Supporting
      </span>
    );
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header Banner */}
      <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-slate-50 to-white">
        <div>
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-brand-600" />
            <h2 className="text-base font-bold text-slate-900">Application Requirement Checklist</h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated verification against official Indian citizen service & scheme guidelines
          </p>
        </div>
        <div>
          {isComplete && (
            <span className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-sm">
              <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
              STATUS: COMPLETE (READY TO APPLY)
            </span>
          )}
          {isReview && (
            <span className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300 shadow-sm">
              <AlertCircle className="w-4 h-4 mr-1.5 text-amber-600" />
              STATUS: REVIEW REQUIRED
            </span>
          )}
          {!isComplete && !isReview && (
            <span className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300 shadow-sm">
              <XCircle className="w-4 h-4 mr-1.5 text-rose-600" />
              STATUS: INCOMPLETE ({mandatoryMissing.length} MISSING)
            </span>
          )}
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* Citizen Guidance Summary Banner */}
        {isComplete ? (
          <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 text-xs text-emerald-900 flex items-center space-x-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <div>
              <span className="font-bold">All mandatory documents are present!</span> Your application package is ready. You can now download the verified summary report.
            </div>
          </div>
        ) : isReview ? (
          <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 flex items-center space-x-2.5">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
            <div>
              <span className="font-bold">Human review required.</span> Please inspect the highlighted warnings, expired documents, or name variations before submitting to the authority.
            </div>
          </div>
        ) : (
          <div className="p-3.5 bg-rose-50 rounded-xl border border-rose-200 text-xs text-rose-900 flex items-center space-x-2.5">
            <Info className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <div>
              <span className="font-bold">{mandatoryMissing.length} mandatory document(s) still missing.</span> Upload the missing documents using the ingestion box below to complete your application.
            </div>
          </div>
        )}

        {/* Satisfied Requirements */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center space-x-1.5">
              <span>Uploaded & Satisfied Documents</span>
              <span className="bg-emerald-100 text-emerald-800 text-[10px] px-2 py-0.2 rounded-full font-bold">
                {satisfied.length}
              </span>
            </h3>
          </div>

          {satisfied.length === 0 ? (
            <p className="text-xs text-slate-400 italic p-4 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-center">
              No documents uploaded yet. Upload files below to start verification.
            </p>
          ) : (
            <div className="space-y-2">
              {satisfied.map((item, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-xl bg-emerald-50/40 border border-emerald-200/80 text-xs gap-2">
                  <div className="flex items-start space-x-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-bold text-slate-900 flex items-center space-x-2">
                        <span>{item.display_name}</span>
                        {getTypeBadge(item.requirement_type, item.is_mandatory)}
                      </div>
                      <div className="text-slate-500 mt-0.5">{item.reason}</div>
                    </div>
                  </div>
                  <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100/80 px-2.5 py-1 rounded-lg self-start sm:self-center">
                    Satisfied
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Missing Requirements */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center space-x-1.5">
              <span>Pending / Missing Documents</span>
              <span className={`text-[10px] px-2 py-0.2 rounded-full font-bold ${
                missing.length > 0 ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-600'
              }`}>
                {missing.length}
              </span>
            </h3>
          </div>

          {missing.length === 0 ? (
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-xs text-emerald-800 font-semibold flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>All mandatory and supporting documents for this category are fulfilled!</span>
            </div>
          ) : (
            <div className="space-y-2">
              {missing.map((item, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-xl bg-rose-50/40 border border-rose-200/80 text-xs gap-2">
                  <div className="flex items-start space-x-2.5">
                    <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-bold text-slate-900 flex items-center space-x-2">
                        <span>{item.display_name}</span>
                        {getTypeBadge(item.requirement_type, item.is_mandatory)}
                      </div>
                      <div className="text-rose-700 mt-0.5">{item.reason}</div>
                    </div>
                  </div>
                  <span className="text-[11px] font-bold text-rose-700 bg-rose-100 px-2.5 py-1 rounded-lg self-start sm:self-center">
                    Upload Needed
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actionable Next Steps */}
        {recommendedActions && recommendedActions.length > 0 && (
          <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center">
              <ArrowRight className="w-3.5 h-3.5 mr-1.5 text-brand-600" />
              Recommended Next Steps for Citizen
            </h4>
            <ul className="text-xs text-slate-700 space-y-1.5">
              {recommendedActions.map((act, i) => (
                <li key={i} className="flex items-start space-x-2">
                  <span className="text-brand-600 font-bold">&bull;</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChecklistStatus;
