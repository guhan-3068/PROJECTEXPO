import React, { useState } from 'react';
import { Gauge, ShieldCheck, AlertCircle, Sparkles, CheckCircle2, ChevronRight, Info } from 'lucide-react';
import ConfidenceMeterModal from './ConfidenceMeterModal';

const ConfidenceMeterCard = ({ confidenceData = null }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const meanScore = confidenceData?.mean_score || 88;
  const overallLevel = confidenceData?.overall_level || 'High Confidence';
  const totalDocs = confidenceData?.total_documents || 0;

  return (
    <>
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition space-y-3.5 flex flex-col justify-between">
        <div className="space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="p-2.5 rounded-xl bg-indigo-50 text-indigo-700">
              <Gauge className="w-5 h-5" />
            </span>
            <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              Measurable Reliability
            </span>
          </div>

          <div>
            <h3 className="font-extrabold text-slate-900 text-sm">
              Verification Confidence Meter
            </h3>
            <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
              Transparent, measurable reliability scores across 6 dimensions with mandatory authenticity disclosures.
            </p>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-slate-700">
              <span>Overall AI Analysis Reliability</span>
              <span className="text-indigo-600">{meanScore}% ({overallLevel})</span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-indigo-600 h-full rounded-full transition-all duration-300"
                style={{ width: `${meanScore}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[10px] text-slate-400">
              <span>Official Authenticity: Not Verified</span>
              <span>Based on {totalDocs || 1} Document(s)</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="w-full inline-flex items-center justify-center space-x-1 py-2 px-3 bg-slate-100 hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 text-xs font-bold rounded-xl transition border border-slate-200"
        >
          <span>Inspect Confidence Breakdown</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <ConfidenceMeterModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        confidenceData={confidenceData}
      />
    </>
  );
};

export default ConfidenceMeterCard;
