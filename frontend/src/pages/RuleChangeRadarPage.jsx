import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Radio, ArrowLeft, Search, Filter, ShieldCheck, AlertTriangle,
  ExternalLink, Calendar, Building, Sparkles, CheckCircle2,
  FileText, ArrowRight, RefreshCw, X, Loader2, HelpCircle
} from 'lucide-react';
import { ruleRadarApi } from '../services/api';

const STATUS_BADGES = {
  'New Official Update': 'bg-emerald-100 text-emerald-800 border-emerald-300',
  'Requirement Changed': 'bg-orange-100 text-orange-800 border-orange-300',
  'No Confirmed Change': 'bg-blue-100 text-blue-800 border-blue-300',
  'Verification Required': 'bg-rose-100 text-rose-800 border-rose-300'
};

const RuleChangeRadarPage = () => {
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stateFilter, setStateFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [departmentFilter, setDepartmentFilter] = useState('All');
  const [onlyVerified, setOnlyVerified] = useState(false);

  // Requirement Comparison Modal state
  const [comparisonModal, setComparisonModal] = useState({ isOpen: false, profileCode: null, data: null, loading: false });

  useEffect(() => {
    fetchUpdates();
  }, [stateFilter, statusFilter, departmentFilter, onlyVerified]);

  const fetchUpdates = async () => {
    setLoading(true);
    try {
      const filters = {};
      if (stateFilter !== 'All') filters.state = stateFilter;
      if (statusFilter !== 'All') filters.status = statusFilter;
      if (departmentFilter !== 'All') filters.department = departmentFilter;
      if (onlyVerified) filters.only_verified = true;

      const data = await ruleRadarApi.getUpdates(filters);
      setUpdates(data);
    } catch (err) {
      console.error('Failed to load regulatory updates', err);
    } finally {
      setLoading(false);
    }
  };

  const openComparison = async (profileCode) => {
    setComparisonModal({ isOpen: true, profileCode, data: null, loading: true });
    try {
      const diffData = await ruleRadarApi.compareRequirements(profileCode);
      setComparisonModal({ isOpen: true, profileCode, data: diffData, loading: false });
    } catch (err) {
      console.error('Failed to compare requirements', err);
      setComparisonModal({ isOpen: true, profileCode, data: null, loading: false });
    }
  };

  const filteredUpdates = updates.filter(u => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      u.title.toLowerCase().includes(term) ||
      u.department.toLowerCase().includes(term) ||
      u.source_authority.toLowerCase().includes(term) ||
      u.impact_summary.toLowerCase().includes(term)
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Top Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          to="/dashboard"
          className="inline-flex items-center text-xs font-bold text-slate-600 hover:text-[#0f2942] transition"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5 text-slate-500" />
          Back to Citizen Dashboard
        </Link>
        <span className="text-[11px] font-semibold text-slate-500 bg-white px-3 py-1 rounded-full border border-slate-200">
          Source: Official State Gazettes & Ministry Circulars
        </span>
      </div>

      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-[#0f2942] via-[#1e3a8a] to-[#0f2942] text-white p-6 sm:p-8 rounded-3xl shadow-md relative overflow-hidden">
        <div className="max-w-3xl space-y-2 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-orange-500/20 text-orange-300 text-xs font-bold border border-orange-400/30">
            <Radio className="w-3.5 h-3.5 text-orange-400 animate-pulse" />
            <span>Rule Change Radar – Regulatory Update Tracker</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Indian Citizen Document Rules & Regulatory Radar
          </h1>
          <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
            Monitor real government requirement updates across First Graduate schemes, college admissions (TNEA), scholarships (NSP), RTO licensing, and Tahsildar revenue certificates. Distinguishes verified official Gazettes from unverified social claims.
          </p>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white p-4 sm:p-5 rounded-2xl shadow-sm border border-slate-200 space-y-3.5">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by keyword, department, G.O. reference, or certificate..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* State filter */}
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:outline-none"
            >
              <option value="All">All Regions</option>
              <option value="Tamil Nadu">Tamil Nadu</option>
              <option value="Central">All India / Central</option>
            </select>

            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:outline-none"
            >
              <option value="All">All Statuses</option>
              <option value="New Official Update">New Official Update</option>
              <option value="Requirement Changed">Requirement Changed</option>
              <option value="No Confirmed Change">No Confirmed Change</option>
              <option value="Verification Required">Verification Required</option>
            </select>

            {/* Only Verified toggle */}
            <label className="inline-flex items-center space-x-1.5 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={onlyVerified}
                onChange={(e) => setOnlyVerified(e.target.checked)}
                className="rounded border-slate-300 text-[#0f2942] focus:ring-0"
              />
              <span>Verified Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Regulatory Updates List */}
      <div className="space-y-4">
        {loading ? (
          <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
            <Loader2 className="w-8 h-8 animate-spin text-[#0f2942] mx-auto" />
            <p className="text-xs text-slate-500 font-semibold">Scanning official gazettes and regulatory feeds...</p>
          </div>
        ) : filteredUpdates.length === 0 ? (
          <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-2">
            <Radio className="w-10 h-10 text-slate-300 mx-auto" />
            <h4 className="text-sm font-bold text-slate-700">No verified rule updates available</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No regulatory updates match your selected filters. Requirements remain unchanged under active official department gazettes.
            </p>
          </div>
        ) : (
          filteredUpdates.map((upd) => {
            const isUnverified = !upd.is_verified || upd.status === 'Verification Required';
            const badgeClass = STATUS_BADGES[upd.status] || 'bg-slate-100 text-slate-700 border-slate-300';

            return (
              <div
                key={upd.id}
                className={`bg-white rounded-2xl p-6 border shadow-sm space-y-4 transition hover:shadow-md ${
                  isUnverified ? 'border-amber-300 bg-amber-50/20' : 'border-slate-200'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${badgeClass}`}>
                        {upd.status}
                      </span>
                      <span className="text-[11px] font-bold text-slate-500 px-2.5 py-0.5 bg-slate-100 rounded-md">
                        {upd.state} &bull; {upd.category}
                      </span>
                      {isUnverified ? (
                        <span className="text-[10px] font-black px-2 py-0.5 rounded bg-rose-100 text-rose-800 border border-rose-300 flex items-center space-x-1">
                          <AlertTriangle className="w-3 h-3 text-rose-600" />
                          <span>Unverified Source – Not Official</span>
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center space-x-1">
                          <ShieldCheck className="w-3 h-3 text-emerald-600" />
                          <span>Official Confirmed Notice</span>
                        </span>
                      )}
                    </div>

                    <h3 className="text-base sm:text-lg font-black text-slate-900 leading-snug">
                      {upd.title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      <span>Authority: <strong className="text-slate-700">{upd.source_authority}</strong></span>
                      <span>&bull;</span>
                      <span>Department: <strong className="text-slate-700">{upd.department}</strong></span>
                      {upd.effective_date && (
                        <>
                          <span>&bull;</span>
                          <span>Effective: <strong className="text-slate-700">{upd.effective_date}</strong></span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 self-start">
                    {upd.profile_code !== 'ALL' && (
                      <button
                        onClick={() => openComparison(upd.profile_code)}
                        className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white text-xs font-bold rounded-xl transition shadow-sm whitespace-nowrap"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        <span>Compare Checklist Versions</span>
                      </button>
                    )}

                    {upd.official_source_url && (
                      <a
                        href={upd.official_source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="p-2 text-slate-500 hover:text-[#0f2942] hover:bg-slate-100 rounded-xl transition border border-slate-200"
                        title="View Official Source Document"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </div>

                {/* Impact for Citizens Card */}
                <div className={`p-4 rounded-xl border text-xs space-y-1.5 ${
                  isUnverified ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}>
                  <div className="font-extrabold flex items-center space-x-1.5 text-slate-900">
                    <Sparkles className="w-3.5 h-3.5 text-orange-500" />
                    <span>What this regulatory change means for applicants:</span>
                  </div>
                  <p className="leading-relaxed">
                    {upd.impact_summary}
                  </p>
                </div>

                {/* Requirement change details if modified */}
                {upd.change_type === 'MODIFIED' && upd.previous_requirement && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                      <div className="text-[10px] font-bold text-slate-400 uppercase">Prior Requirement</div>
                      <p className="text-slate-600 italic">
                        {upd.previous_requirement.rule || upd.previous_requirement.description || 'Legacy format'}
                      </p>
                    </div>
                    <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-1">
                      <div className="text-[10px] font-bold text-emerald-700 uppercase">Updated New Requirement</div>
                      <p className="text-slate-800 font-medium">
                        {upd.updated_requirement.rule || upd.updated_requirement.description || 'Updated rule'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Requirement Version Comparison Modal */}
      {comparisonModal.isOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden max-h-[90vh] flex flex-col animate-in fade-in zoom-in-95 duration-150">
            <div className="bg-[#0f2942] text-white p-5 flex items-start justify-between">
              <div className="space-y-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-orange-500/20 text-orange-300">
                  Version Difference Audit
                </span>
                <h3 className="text-base font-black">
                  Checklist Comparison: {comparisonModal.data?.profile_name || comparisonModal.profileCode}
                </h3>
                <p className="text-xs text-slate-300">
                  Detailed view of added, modified, and unchanged document rules.
                </p>
              </div>
              <button
                onClick={() => setComparisonModal({ isOpen: false, profileCode: null, data: null, loading: false })}
                className="p-1.5 text-slate-300 hover:text-white rounded-full hover:bg-white/10"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              {comparisonModal.loading ? (
                <div className="p-12 text-center text-slate-400">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-[#0f2942]" />
                  <span>Computing requirement diffs...</span>
                </div>
              ) : comparisonModal.data ? (
                <>
                  {/* Modified Requirements */}
                  {comparisonModal.data.modified_requirements?.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-extrabold text-orange-700 uppercase tracking-wider text-[11px] flex items-center space-x-1.5">
                        <span className="w-2 h-2 rounded-full bg-orange-500" />
                        <span>Modified Requirements ({comparisonModal.data.modified_requirements.length})</span>
                      </h4>
                      {comparisonModal.data.modified_requirements.map((m, i) => (
                        <div key={i} className="p-3 rounded-xl bg-orange-50/60 border border-orange-200 space-y-1">
                          <div className="font-bold text-slate-900">{m.display_name}</div>
                          <div className="text-slate-600"><strong>New Rule:</strong> {m.new_rule}</div>
                          <div className="text-slate-400 text-[10px]">Prior rule: {m.previous_rule}</div>
                          <div className="text-[10px] text-orange-800 font-medium pt-1">Authority: {m.authority}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Added Requirements */}
                  {comparisonModal.data.added_requirements?.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-extrabold text-emerald-700 uppercase tracking-wider text-[11px] flex items-center space-x-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-500" />
                        <span>Newly Added Requirements ({comparisonModal.data.added_requirements.length})</span>
                      </h4>
                      {comparisonModal.data.added_requirements.map((a, i) => (
                        <div key={i} className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-1">
                          <div className="font-bold text-slate-900">{a.display_name}</div>
                          <div className="text-slate-700">{a.explanation}</div>
                          <div className="text-[10px] text-emerald-800 font-medium">Authority: {a.authority}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Unchanged Requirements */}
                  {comparisonModal.data.unchanged_requirements?.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-100">
                      <h4 className="font-extrabold text-slate-500 uppercase tracking-wider text-[11px]">
                        Unchanged Standard Checklist Items ({comparisonModal.data.unchanged_requirements.length})
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {comparisonModal.data.unchanged_requirements.map((u, i) => (
                          <div key={i} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                            <span className="font-bold text-slate-800">{u.display_name}</span>
                            <span className="text-[10px] text-slate-400 block">{u.requirement_type}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-8 text-center text-slate-400">
                  Failed to compute requirements difference.
                </div>
              )}
            </div>

            <div className="bg-slate-50 p-3 border-t border-slate-200 text-right">
              <button
                onClick={() => setComparisonModal({ isOpen: false, profileCode: null, data: null, loading: false })}
                className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl text-xs transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default RuleChangeRadarPage;
