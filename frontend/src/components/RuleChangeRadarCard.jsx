import React from 'react';
import { Radio, AlertTriangle, ArrowRight, ShieldCheck, Sparkles, Bell, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

const RuleChangeRadarCard = ({ updates = [], notifications = [] }) => {
  const verifiedCount = updates.filter(u => u.is_verified).length;
  const recentUpdate = updates[0] || null;
  const hasAlerts = notifications.length > 0;

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition space-y-3.5 flex flex-col justify-between">
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="p-2.5 rounded-xl bg-orange-50 text-orange-600">
            <Radio className="w-5 h-5 animate-pulse" />
          </span>
          <div className="flex items-center space-x-1.5">
            {hasAlerts && (
              <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-rose-500 text-white animate-bounce flex items-center space-x-1">
                <Bell className="w-3 h-3" />
                <span>{notifications.length} Active Alert{notifications.length > 1 ? 's' : ''}</span>
              </span>
            )}
            <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 border border-orange-200">
              Regulatory Updates
            </span>
          </div>
        </div>

        <div>
          <h3 className="font-extrabold text-slate-900 text-sm">
            Rule Change Radar
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
            Tracks official government gazettes, G.O. revisions, and document checklist changes (TN & Central).
          </p>
        </div>

        {recentUpdate ? (
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Latest Confirmed Notice
              </span>
              <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                Official
              </span>
            </div>
            <div className="font-bold text-slate-900 truncate">
              {recentUpdate.title}
            </div>
            <p className="text-[11px] text-slate-500 line-clamp-2">
              {recentUpdate.impact_summary}
            </p>
          </div>
        ) : (
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-400 italic text-center">
            No verified rule updates recorded for this category yet.
          </div>
        )}
      </div>

      <Link
        to="/rule-radar"
        className="w-full inline-flex items-center justify-center space-x-1 py-2 px-3 bg-slate-100 hover:bg-orange-50 text-slate-700 hover:text-orange-700 text-xs font-bold rounded-xl transition border border-slate-200"
      >
        <span>Open Rule Change Radar</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
};

export default RuleChangeRadarCard;
