import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Clock, ShieldCheck, HelpCircle } from 'lucide-react';

const STATUS_CONFIG = {
  'Ready for Next Step': {
    badgeClass: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    icon: CheckCircle2,
    iconColor: 'text-emerald-600',
    headline: 'Ready for Next Step',
    summary: 'No issues were detected by the automated checks. All mandatory documents are uploaded and readable.',
    advice: 'Review your details once more and proceed to the official department portal to submit your application.'
  },
  'Action Required': {
    badgeClass: 'bg-rose-100 text-rose-800 border-rose-300',
    icon: AlertCircle,
    iconColor: 'text-rose-600',
    headline: 'Action Required',
    summary: 'One or more required documents, expired certificates, or critical corrections are pending.',
    advice: 'Follow the prioritized action plan below to upload missing documents or request renewals before applying.'
  },
  'Needs Manual Review': {
    badgeClass: 'bg-amber-100 text-amber-800 border-amber-300',
    icon: AlertTriangle,
    iconColor: 'text-amber-600',
    headline: 'Needs Manual Review',
    summary: 'The system cannot confidently confirm whether the information is completely consistent or readable.',
    advice: 'Check the highlighted discrepancies. You may need a notarized affidavit or a clearer scan.'
  },
  'Official Verification Pending': {
    badgeClass: 'bg-blue-100 text-blue-800 border-blue-300',
    icon: Clock,
    iconColor: 'text-blue-600',
    headline: 'Official Verification Pending',
    summary: 'Pre-check documents are in order, but official authenticity must be verified by the issuing department.',
    advice: 'Keep your original physical certificates ready for counseling or Tahsildar / RTO verification.'
  }
};

const ReadinessBadge = ({ status = 'Action Required', score = '0%', size = 'md' }) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG['Action Required'];
  const Icon = config.icon;

  if (size === 'sm') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border ${config.badgeClass}`}>
        <Icon className={`w-3.5 h-3.5 mr-1.5 ${config.iconColor}`} />
        <span>{config.headline}</span>
      </span>
    );
  }

  return (
    <div className={`p-5 rounded-2xl border ${config.badgeClass.replace('text-', 'border-').split(' ')[2]} bg-white shadow-sm space-y-3`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-xl ${config.badgeClass.split(' ')[0]}`}>
            <Icon className={`w-6 h-6 ${config.iconColor}`} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Pre-Application Readiness Result
              </span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-extrabold border ${config.badgeClass}`}>
                {config.headline}
              </span>
            </div>
            <h3 className="text-lg font-black text-slate-900 mt-0.5">
              {config.headline}
            </h3>
          </div>
        </div>

        {score && (
          <div className="flex items-center sm:flex-col sm:items-end bg-slate-50 px-4 py-2 rounded-xl border border-slate-200">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mr-2 sm:mr-0">
              Readiness Score
            </span>
            <span className="text-xl font-black text-[#0f2942]">
              {score}
            </span>
          </div>
        )}
      </div>

      <p className="text-xs text-slate-700 leading-relaxed">
        {config.summary}
      </p>

      <div className="pt-2 border-t border-slate-100 flex items-start space-x-2 text-[11px] text-slate-600">
        <ShieldCheck className="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5" />
        <span>
          <strong>Citizen Guidance:</strong> {config.advice}
        </span>
      </div>

      <div className="text-[10px] text-slate-600 bg-amber-50/70 p-2.5 rounded-lg border border-amber-200/80 leading-normal">
        <strong>Important Advisory:</strong> QUBIX is an automated readiness assistance tool. It never guarantees application approval, even when every automated check passes. Final approval rests exclusively with the designated government issuing authority.
      </div>
    </div>
  );
};

export default ReadinessBadge;
