import React, { useState } from 'react';
import {
  CheckCircle2, AlertTriangle, AlertCircle, RefreshCw, HelpCircle,
  ArrowRight, ShieldCheck, FileText, Upload, Sparkles, ExternalLink
} from 'lucide-react';
import HowToFixModal from './HowToFixModal';

const ActionPlanChecklist = ({
  checklist = [],
  actionPlan = [],
  onRecheck,
  isRechecking = false,
  onOpenUpload
}) => {
  const [selectedGuideId, setSelectedGuideId] = useState(null);
  const [customTitle, setCustomTitle] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openGuide = (guideId, title = null) => {
    setSelectedGuideId(guideId || 'name_mismatch');
    setCustomTitle(title);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* 1. Prioritized Document Checklist */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-extrabold text-[#0f2942] flex items-center space-x-2">
              <FileText className="w-5 h-5 text-brand-600" />
              <span>Prioritized Document Checklist</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Current readiness status of all mandatory, conditional, and supporting certificates.
            </p>
          </div>

          {onRecheck && (
            <button
              onClick={onRecheck}
              disabled={isRechecking}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition shadow-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRechecking ? 'animate-spin' : ''}`} />
              <span>{isRechecking ? 'Rechecking...' : 'Recheck Documents'}</span>
            </button>
          )}
        </div>

        <div className="divide-y divide-slate-100">
          {checklist.map((item, idx) => {
            const isSatisfied = item.status === 'SATISFIED';
            const isMissing = item.status === 'MISSING';
            const isReview = item.status === 'NEEDS_REVIEW';

            let symbolBg = 'bg-slate-100 text-slate-500';
            let symbolText = '[ ]';
            let statusBadge = 'bg-slate-100 text-slate-700 border-slate-200';

            if (isSatisfied) {
              symbolBg = 'bg-emerald-100 text-emerald-800 border border-emerald-300';
              symbolText = '[x]';
              statusBadge = 'bg-emerald-50 text-emerald-800 border-emerald-200';
            } else if (isReview) {
              symbolBg = 'bg-amber-100 text-amber-800 border border-amber-300';
              symbolText = '[!]';
              statusBadge = 'bg-amber-50 text-amber-800 border-amber-200';
            } else if (isMissing && item.is_mandatory) {
              symbolBg = 'bg-rose-100 text-rose-800 border border-rose-300';
              symbolText = '[ ]';
              statusBadge = 'bg-rose-50 text-rose-800 border-rose-200';
            }

            return (
              <div key={idx} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start space-x-3">
                  <span className={`w-7 h-7 rounded-lg font-mono font-bold flex items-center justify-center text-xs flex-shrink-0 ${symbolBg}`}>
                    {symbolText}
                  </span>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-extrabold text-sm text-slate-900">
                        {item.display_name}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusBadge}`}>
                        {item.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {item.detail}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2 self-start sm:self-auto pl-10 sm:pl-0">
                  {item.guide_id && (
                    <button
                      onClick={() => openGuide(item.guide_id, `How to Fix ${item.display_name}`)}
                      className="px-3 py-1.5 bg-orange-50 hover:bg-orange-100 text-[#ea580c] border border-orange-200 rounded-lg text-xs font-bold transition flex items-center space-x-1"
                    >
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>How to Fix This?</span>
                    </button>
                  )}
                  {isMissing && onOpenUpload && (
                    <button
                      onClick={onOpenUpload}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition flex items-center space-x-1"
                    >
                      <Upload className="w-3.5 h-3.5" />
                      <span>Upload</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Recommended Next Actions Plan */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-extrabold text-[#0f2942] flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-orange-500" />
              <span>Fix My Application – Action Plan</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Prioritized step-by-step actions to get your application 100% submission ready.
            </p>
          </div>
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
            {actionPlan.length} Recommended Actions
          </span>
        </div>

        <div className="space-y-3">
          {actionPlan.map((action, idx) => {
            const isCritical = action.urgency === 'CRITICAL';
            const isWarning = action.urgency === 'WARNING';

            let cardBorder = 'border-slate-200 bg-slate-50';
            let badgeStyle = 'bg-blue-100 text-blue-800 border-blue-200';
            let icon = <CheckCircle2 className="w-4 h-4 text-blue-600" />;

            if (isCritical) {
              cardBorder = 'border-rose-200 bg-rose-50/40';
              badgeStyle = 'bg-rose-100 text-rose-800 border-rose-200';
              icon = <AlertCircle className="w-4 h-4 text-rose-600" />;
            } else if (isWarning) {
              cardBorder = 'border-amber-200 bg-amber-50/40';
              badgeStyle = 'bg-amber-100 text-amber-800 border-amber-200';
              icon = <AlertTriangle className="w-4 h-4 text-amber-600" />;
            }

            return (
              <div
                key={action.id || idx}
                className={`p-4 rounded-xl border ${cardBorder} flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition`}
              >
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">{icon}</div>
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-extrabold text-xs sm:text-sm text-slate-900">
                        {idx + 1}. {action.title}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeStyle}`}>
                        {action.urgency}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {action.description}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2 self-start sm:self-auto pl-7 sm:pl-0">
                  <button
                    onClick={() => openGuide(action.guide_id, action.title)}
                    className="px-3.5 py-1.5 bg-white hover:bg-orange-50 text-[#ea580c] border border-orange-200 rounded-xl text-xs font-bold transition shadow-sm flex items-center space-x-1"
                  >
                    <span>{action.action_label || 'How to Fix This?'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Guide Modal */}
      <HowToFixModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        guideId={selectedGuideId}
        customIssueTitle={customTitle}
      />
    </div>
  );
};

export default ActionPlanChecklist;
