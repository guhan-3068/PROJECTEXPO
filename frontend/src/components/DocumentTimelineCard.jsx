import React from 'react';
import { Calendar, Clock, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

const DocumentTimelineCard = ({ timelineRecords = [] }) => {
  const expiringCount = timelineRecords.filter(r => r.validity_status === 'EXPIRING_SOON').length;
  const expiredCount = timelineRecords.filter(r => r.validity_status === 'EXPIRED').length;
  const nonExpiringCount = timelineRecords.filter(r => r.validity_status === 'NO_EXPIRY').length;

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition space-y-3.5 flex flex-col justify-between">
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="p-2.5 rounded-xl bg-blue-50 text-blue-600">
            <Calendar className="w-5 h-5" />
          </span>
          <div className="flex items-center space-x-1.5">
            {expiringCount > 0 && (
              <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                {expiringCount} Expiring Soon
              </span>
            )}
            <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              Lifecycle Tracker
            </span>
          </div>
        </div>

        <div>
          <h3 className="font-extrabold text-slate-900 text-sm">
            Document Timeline & Renewals
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
            Tracks issue dates, validity periods, configurable expiry reminders (30/15/7d), and renewal history.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
            <div className="font-black text-slate-900 text-base">{nonExpiringCount}</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase mt-0.5">Permanent</div>
          </div>
          <div className="p-2.5 rounded-xl bg-amber-50/60 border border-amber-200">
            <div className="font-black text-amber-800 text-base">{expiringCount}</div>
            <div className="text-[10px] font-bold text-amber-700 uppercase mt-0.5">Expiring</div>
          </div>
          <div className="p-2.5 rounded-xl bg-rose-50/60 border border-rose-200">
            <div className="font-black text-rose-800 text-base">{expiredCount}</div>
            <div className="text-[10px] font-bold text-rose-700 uppercase mt-0.5">Expired</div>
          </div>
        </div>
      </div>

      <Link
        to="/document-timeline"
        className="w-full inline-flex items-center justify-center space-x-1 py-2 px-3 bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 text-xs font-bold rounded-xl transition border border-slate-200"
      >
        <span>View Full Document Timeline</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
};

export default DocumentTimelineCard;
