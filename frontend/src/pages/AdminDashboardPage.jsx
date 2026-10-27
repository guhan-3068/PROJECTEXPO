import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminApi, applicationsApi } from '../services/api';
import {
  ShieldCheck, AlertTriangle, CheckCircle, XCircle, Clock, ExternalLink,
  Filter, Plus, Edit3, Trash2, RefreshCw, Search, Check, AlertCircle,
  FileText, Layers, Globe, Calendar, CheckSquare, Loader2
} from 'lucide-react';

const AdminDashboardPage = () => {
  const [activeTab, setActiveTab] = useState('applications'); // 'applications' | 'requirements'

  // Application Queue state
  const [applications, setApplications] = useState([]);
  const [filter, setFilter] = useState('');
  const [loadingApps, setLoadingApps] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [decision, setDecision] = useState('APPROVED');
  const [notes, setNotes] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  // Requirements System state
  const [requirementsData, setRequirementsData] = useState({ stats: {}, requirements: [] });
  const [loadingReqs, setLoadingReqs] = useState(false);
  const [profiles, setProfiles] = useState([]);
  const [reqProfileFilter, setReqProfileFilter] = useState('');
  const [reqStatusFilter, setReqStatusFilter] = useState('');
  const [reqSearch, setReqSearch] = useState('');
  const [reviewNeededOnly, setReviewNeededOnly] = useState(false);
  const [editReqModalOpen, setEditReqModalOpen] = useState(false);
  const [addReqModalOpen, setAddReqModalOpen] = useState(false);
  const [editingReq, setEditingReq] = useState(null);
  const [reqFormData, setReqFormData] = useState({
    application_profile_id: '',
    requirement_code: '',
    display_name: '',
    description: '',
    is_mandatory: true,
    requirement_type: 'REQUIRED',
    alternative_documents_str: '',
    validity_rules: '',
    accepted_formats: 'PDF, JPG, JPEG, PNG (Max 5MB)',
    official_source_url: '',
    status: 'Current'
  });
  const [savingReq, setSavingReq] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    if (activeTab === 'applications') {
      fetchApplications();
    } else {
      fetchRequirements();
      fetchProfiles();
    }
  }, [activeTab, filter, reqProfileFilter, reqStatusFilter, reqSearch, reviewNeededOnly]);

  const fetchApplications = async () => {
    setLoadingApps(true);
    try {
      const data = await adminApi.listApplications(filter || null);
      setApplications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingApps(false);
    }
  };

  const fetchRequirements = async () => {
    setLoadingReqs(true);
    try {
      const filters = {};
      if (reqProfileFilter) filters.profile_code = reqProfileFilter;
      if (reqStatusFilter) filters.status = reqStatusFilter;
      if (reqSearch) filters.search = reqSearch;
      if (reviewNeededOnly) filters.review_needed_only = true;

      const res = await adminApi.getRequirements(filters);
      setRequirementsData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingReqs(false);
    }
  };

  const fetchProfiles = async () => {
    try {
      const data = await applicationsApi.getProfiles();
      setProfiles(data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!notes.trim()) {
      alert('Please enter review rationale notes');
      return;
    }
    setSubmittingReview(true);
    try {
      await adminApi.submitReview(selectedApp.id, decision, notes);
      setReviewModalOpen(false);
      fetchApplications();
      setStatusMsg('Application review recorded successfully.');
      setTimeout(() => setStatusMsg(''), 4000);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit review');
    } finally {
      setSubmittingReview(false);
    }
  };

  // Requirement Actions
  const handleVerifyRequirement = async (id, name) => {
    try {
      await adminApi.verifyRequirement(id);
      setStatusMsg(`Verified "${name}". Periodic review timer reset to 180 days.`);
      setTimeout(() => setStatusMsg(''), 4000);
      fetchRequirements();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to verify requirement');
    }
  };

  const handleDeleteRequirement = async (id, name) => {
    if (!window.confirm(`Permanently delete the document requirement "${name}"?`)) return;
    try {
      await adminApi.deleteRequirement(id);
      setStatusMsg(`Requirement "${name}" removed.`);
      setTimeout(() => setStatusMsg(''), 4000);
      fetchRequirements();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete requirement');
    }
  };

  const handleSyncDefaults = async () => {
    if (!window.confirm('Synchronize database requirements with official 2026 state rules across all 14 services?')) return;
    try {
      const res = await adminApi.syncDefaultRequirements();
      setStatusMsg(res.message || 'Requirements synchronized.');
      setTimeout(() => setStatusMsg(''), 4000);
      fetchRequirements();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to sync defaults');
    }
  };

  const openAddReqModal = () => {
    setReqFormData({
      application_profile_id: profiles[0]?.id || '',
      requirement_code: '',
      display_name: '',
      description: '',
      is_mandatory: true,
      requirement_type: 'REQUIRED',
      alternative_documents_str: '',
      validity_rules: 'Permanent record or current financial year',
      accepted_formats: 'PDF, JPG, JPEG, PNG (Max 5MB)',
      official_source_url: 'https://tnesevai.tn.gov.in',
      status: 'Current'
    });
    setAddReqModalOpen(true);
  };

  const openEditReqModal = (req) => {
    setEditingReq(req);
    setReqFormData({
      display_name: req.display_name,
      description: req.description || '',
      is_mandatory: req.is_mandatory,
      requirement_type: req.requirement_type,
      alternative_documents_str: (req.alternative_documents || []).join(', '),
      validity_rules: req.validity_rules || '',
      accepted_formats: req.accepted_formats || 'PDF, JPG, JPEG, PNG (Max 5MB)',
      official_source_url: req.official_source_url || '',
      status: req.status || 'Current'
    });
    setEditReqModalOpen(true);
  };

  const handleCreateReqSubmit = async (e) => {
    e.preventDefault();
    setSavingReq(true);
    try {
      const alts = reqFormData.alternative_documents_str
        ? reqFormData.alternative_documents_str.split(',').map((s) => s.trim()).filter(Boolean)
        : [];

      await adminApi.createRequirement({
        application_profile_id: reqFormData.application_profile_id,
        requirement_code: reqFormData.requirement_code.toUpperCase().replace(/\s+/g, '_'),
        display_name: reqFormData.display_name,
        description: reqFormData.description,
        is_mandatory: reqFormData.is_mandatory,
        requirement_type: reqFormData.requirement_type,
        alternative_documents: alts,
        validity_rules: reqFormData.validity_rules,
        accepted_formats: reqFormData.accepted_formats,
        official_source_url: reqFormData.official_source_url,
        status: reqFormData.status
      });

      setAddReqModalOpen(false);
      setStatusMsg('New requirement created and stored in database.');
      setTimeout(() => setStatusMsg(''), 4000);
      fetchRequirements();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create requirement');
    } finally {
      setSavingReq(false);
    }
  };

  const handleEditReqSubmit = async (e) => {
    e.preventDefault();
    if (!editingReq) return;
    setSavingReq(true);
    try {
      const alts = reqFormData.alternative_documents_str
        ? reqFormData.alternative_documents_str.split(',').map((s) => s.trim()).filter(Boolean)
        : [];

      await adminApi.updateRequirement(editingReq.id, {
        display_name: reqFormData.display_name,
        description: reqFormData.description,
        is_mandatory: reqFormData.is_mandatory,
        requirement_type: reqFormData.requirement_type,
        alternative_documents: alts,
        validity_rules: reqFormData.validity_rules,
        accepted_formats: reqFormData.accepted_formats,
        official_source_url: reqFormData.official_source_url,
        status: reqFormData.status
      });

      setEditReqModalOpen(false);
      setStatusMsg(`Updated "${reqFormData.display_name}".`);
      setTimeout(() => setStatusMsg(''), 4000);
      fetchRequirements();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update requirement');
    } finally {
      setSavingReq(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Banner with Navigation Tabs */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="p-1.5 bg-[#0f2942] text-white rounded-lg text-xs font-bold uppercase tracking-wider">
                Admin Console
              </span>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                Government Compliance & Verification Management
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Live database-backed rules management, periodical audit review flags, and applicant adjudication queue.
            </p>
          </div>

          {/* Navigation Pill Tabs */}
          <div className="flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200 self-start md:self-center">
            <button
              onClick={() => setActiveTab('applications')}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 ${
                activeTab === 'applications'
                  ? 'bg-white text-[#0f2942] shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <CheckSquare className="w-3.5 h-3.5" />
              <span>Adjudication Queue</span>
            </button>
            <button
              onClick={() => setActiveTab('requirements')}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 ${
                activeTab === 'requirements'
                  ? 'bg-white text-[#0f2942] shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Requirements Management</span>
            </button>
          </div>
        </div>

        {statusMsg && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2 animate-fadeIn">
            <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{statusMsg}</span>
          </div>
        )}
      </div>

      {/* ========================================================= */}
      {/* TAB 1: APPLICATION ADJUDICATION QUEUE */}
      {/* ========================================================= */}
      {activeTab === 'applications' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-bold text-slate-700">Filter Applications:</span>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="text-xs font-semibold px-3 py-1.5 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
              >
                <option value="">All Applications</option>
                <option value="REVIEW_REQUIRED">Review Required</option>
                <option value="INCOMPLETE">Incomplete</option>
                <option value="COMPLETE">Complete</option>
                <option value="APPROVED">Approved</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
            <span className="text-xs font-mono text-slate-500 font-bold">
              {applications.length} Records Listed
            </span>
          </div>

          {/* Applications Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            {loadingApps ? (
              <div className="p-12 text-center text-slate-400 text-sm">
                <Loader2 className="w-6 h-6 animate-spin mx-auto text-[#0f2942] mb-2" />
                Loading application adjudication queue...
              </div>
            ) : applications.length === 0 ? (
              <div className="p-12 text-center text-slate-400 text-sm italic">
                No applications found matching the selected filter.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
                    <tr>
                      <th className="px-5 py-3.5">Reference & Applicant</th>
                      <th className="px-5 py-3.5">Category & Jurisdiction</th>
                      <th className="px-5 py-3.5">Docs</th>
                      <th className="px-5 py-3.5">Forensic & Mismatch Flags</th>
                      <th className="px-5 py-3.5">Status</th>
                      <th className="px-5 py-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {applications.map((app) => (
                      <tr key={app.id} className="hover:bg-slate-50/80 transition">
                        <td className="px-5 py-4">
                          <div className="font-bold text-slate-900 text-sm">{app.reference_number}</div>
                          <div className="text-slate-500">{app.applicant_name} ({app.applicant_email})</div>
                        </td>
                        <td className="px-5 py-4">
                          <div className="font-semibold text-slate-800">{app.profile_name}</div>
                          <div className="text-slate-400">{app.jurisdiction}</div>
                        </td>
                        <td className="px-5 py-4 font-mono font-semibold text-slate-700">
                          {app.document_count} files
                        </td>
                        <td className="px-5 py-4 space-y-1">
                          {app.has_tampering_flags && (
                            <span className="inline-block px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold text-[10px] mr-1">
                              TAMPER FLAG
                            </span>
                          )}
                          {app.has_mismatches && (
                            <span className="inline-block px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px] mr-1">
                              MISMATCH
                            </span>
                          )}
                          {app.has_expired_docs && (
                            <span className="inline-block px-2 py-0.5 rounded bg-red-100 text-red-800 font-bold text-[10px]">
                              EXPIRED DOC
                            </span>
                          )}
                          {!app.has_tampering_flags && !app.has_mismatches && !app.has_expired_docs && (
                            <span className="text-emerald-600 font-semibold text-[11px]">✓ Clean</span>
                          )}
                        </td>
                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold ${
                              app.status === 'APPROVED' || app.status === 'COMPLETE'
                                ? 'bg-emerald-100 text-emerald-800'
                                : app.status === 'REVIEW_REQUIRED'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {app.status}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-right space-x-2">
                          <Link
                            to={`/applications/${app.id}`}
                            className="inline-flex items-center px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 font-medium transition"
                          >
                            <ExternalLink className="w-3.5 h-3.5 mr-1" />
                            Inspect Cockpit
                          </Link>
                          <button
                            onClick={() => {
                              setSelectedApp(app);
                              setDecision('APPROVED');
                              setNotes('');
                              setReviewModalOpen(true);
                            }}
                            className="inline-flex items-center px-3 py-1.5 rounded-lg bg-[#0f2942] hover:bg-[#1e3a8a] text-white font-medium transition"
                          >
                            Adjudicate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 2: DOCUMENT REQUIREMENTS MANAGEMENT SYSTEM */}
      {/* ========================================================= */}
      {activeTab === 'requirements' && (
        <div className="space-y-6">
          {/* Stats Counters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                Total Requirements
              </span>
              <div className="text-2xl font-black text-slate-900 mt-1">
                {requirementsData.stats?.total_requirements || 0}
              </div>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Stored in Database</span>
            </div>

            <div className="bg-white p-4 rounded-xl border border-emerald-200 bg-emerald-50/30 shadow-sm">
              <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block">
                Current & Verified
              </span>
              <div className="text-2xl font-black text-emerald-800 mt-1">
                {requirementsData.stats?.current_count || 0}
              </div>
              <span className="text-[10px] text-emerald-600 mt-0.5 block">Within 180-day cycle</span>
            </div>

            <div className="bg-white p-4 rounded-xl border border-amber-200 bg-amber-50/40 shadow-sm">
              <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider block">
                Review Needed (Flagged)
              </span>
              <div className="text-2xl font-black text-amber-800 mt-1">
                {requirementsData.stats?.review_needed_count || 0}
              </div>
              <span className="text-[10px] text-amber-600 mt-0.5 block">Overdue periodic review</span>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                Outdated Rules
              </span>
              <div className="text-2xl font-black text-slate-900 mt-1">
                {requirementsData.stats?.outdated_count || 0}
              </div>
              <span className="text-[10px] text-slate-400 mt-0.5 block">Flagged for deprecation</span>
            </div>
          </div>

          {/* Action Bar & Filters */}
          <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2.5">
              {/* Search */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="Search requirements..."
                  value={reqSearch}
                  onChange={(e) => setReqSearch(e.target.value)}
                  className="pl-8 pr-3 py-2 text-xs border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
                />
              </div>

              {/* Service Profile Filter */}
              <select
                value={reqProfileFilter}
                onChange={(e) => setReqProfileFilter(e.target.value)}
                className="text-xs font-semibold px-3 py-2 border border-slate-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
              >
                <option value="">All 14 Citizen Services</option>
                {profiles.map((p) => (
                  <option key={p.id} value={p.code}>
                    {p.name}
                  </option>
                ))}
              </select>

              {/* Status Filter */}
              <select
                value={reqStatusFilter}
                onChange={(e) => setReqStatusFilter(e.target.value)}
                className="text-xs font-semibold px-3 py-2 border border-slate-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
              >
                <option value="">All Statuses</option>
                <option value="Current">Current</option>
                <option value="Review Needed">Review Needed</option>
                <option value="Outdated">Outdated</option>
              </select>

              {/* Periodic Review Needed Checkbox */}
              <label className="flex items-center space-x-1.5 text-xs font-bold text-slate-700 bg-amber-50 px-3 py-2 rounded-xl border border-amber-200 cursor-pointer">
                <input
                  type="checkbox"
                  checked={reviewNeededOnly}
                  onChange={(e) => setReviewNeededOnly(e.target.checked)}
                  className="rounded text-amber-600 focus:ring-amber-500"
                />
                <span>Overdue Review Flags Only</span>
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleSyncDefaults}
                className="inline-flex items-center space-x-1 px-3 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 transition"
                title="Refresh database with verified official rules"
              >
                <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                <span>Sync Defaults</span>
              </button>

              <button
                onClick={openAddReqModal}
                className="inline-flex items-center space-x-1 px-4 py-2 rounded-xl bg-[#0f2942] hover:bg-[#1e3a8a] text-white text-xs font-bold shadow-sm transition"
              >
                <Plus className="w-4 h-4 text-white" />
                <span>Add Requirement</span>
              </button>
            </div>
          </div>

          {/* Requirements List / Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            {loadingReqs ? (
              <div className="p-12 text-center text-slate-400 text-sm">
                <Loader2 className="w-6 h-6 animate-spin mx-auto text-[#0f2942] mb-2" />
                Loading document requirements...
              </div>
            ) : (requirementsData.requirements || []).length === 0 ? (
              <div className="p-12 text-center text-slate-400 text-sm italic">
                No document requirements match your current filters.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {requirementsData.requirements.map((r) => (
                  <div key={r.id} className="p-5 hover:bg-slate-50/70 transition space-y-3">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                      <div>
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                            {r.profile_name}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                            r.is_mandatory
                              ? 'bg-rose-100 text-rose-800'
                              : r.requirement_type === 'CONDITIONALLY_REQUIRED'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-slate-100 text-slate-700'
                          }`}>
                            {r.requirement_type}
                          </span>
                          {r.is_review_needed && (
                            <span className="inline-flex items-center space-x-1 text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">
                              <AlertTriangle className="w-3 h-3 text-amber-600" />
                              <span>Periodic Review Overdue</span>
                            </span>
                          )}
                        </div>

                        <h3 className="text-base font-bold text-slate-900">
                          {r.display_name}
                          <span className="text-xs font-mono text-slate-400 ml-2 font-normal">
                            ({r.requirement_code})
                          </span>
                        </h3>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {r.description || 'No description configured'}
                        </p>
                      </div>

                      {/* Status & Quick Actions */}
                      <div className="flex items-center space-x-2 self-start md:self-center">
                        {/* Verify One-Click Action */}
                        <button
                          onClick={() => handleVerifyRequirement(r.id, r.display_name)}
                          className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-200 transition"
                          title="Mark requirement verified and reset 180-day review cycle"
                        >
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Mark Verified</span>
                        </button>

                        <button
                          onClick={() => openEditReqModal(r)}
                          className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition"
                          title="Edit requirement criteria and alternatives"
                        >
                          <Edit3 className="w-3.5 h-3.5 text-slate-500" />
                          <span>Edit</span>
                        </button>

                        <button
                          onClick={() => handleDeleteRequirement(r.id, r.display_name)}
                          className="p-1.5 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-600 transition"
                          title="Delete requirement"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Metadata Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 bg-slate-50/80 p-3 rounded-xl border border-slate-200/80 text-xs">
                      <div>
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">Accepted Alternatives</span>
                        <span className="font-medium text-slate-800">
                          {r.alternative_documents && r.alternative_documents.length > 0
                            ? r.alternative_documents.join(', ')
                            : 'None (Mandatory certificate only)'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">Validity & Expiry Rules</span>
                        <span className="font-medium text-slate-800">
                          {r.validity_rules || 'Permanent validity'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">Formats & Source</span>
                        <div className="flex items-center space-x-2 mt-0.5">
                          <span className="font-medium text-slate-700">{r.accepted_formats || 'PDF, JPG'}</span>
                          {r.official_source_url && (
                            <a
                              href={r.official_source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[#0f2942] hover:text-[#ea580c] inline-flex items-center space-x-0.5"
                            >
                              <Globe className="w-3 h-3 text-slate-400" />
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">Last Verified Date</span>
                        <span className="font-medium text-slate-800">
                          {r.last_verified_date ? new Date(r.last_verified_date).toLocaleDateString() : 'Initial Setup'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* EDIT REQUIREMENT MODAL */}
      {/* ========================================================= */}
      {editReqModalOpen && editingReq && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-xl max-w-xl w-full overflow-hidden border border-slate-200 animate-fadeIn my-8">
            <div className="p-5 bg-[#0f2942] text-white flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base">Edit Document Requirement</h3>
                <p className="text-xs text-slate-300">{editingReq.requirement_code} &bull; {editingReq.profile_name}</p>
              </div>
              <button onClick={() => setEditReqModalOpen(false)} className="text-slate-300 hover:text-white">
                &times;
              </button>
            </div>

            <form onSubmit={handleEditReqSubmit} className="p-6 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Display Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  value={reqFormData.display_name}
                  onChange={(e) => setReqFormData({ ...reqFormData, display_name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Requirement Type
                </label>
                <select
                  value={reqFormData.requirement_type}
                  onChange={(e) => setReqFormData({
                    ...reqFormData,
                    requirement_type: e.target.value,
                    is_mandatory: e.target.value === 'REQUIRED'
                  })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                >
                  <option value="REQUIRED">REQUIRED (Mandatory)</option>
                  <option value="CONDITIONALLY_REQUIRED">CONDITIONALLY REQUIRED</option>
                  <option value="OPTIONAL">OPTIONAL SUPPORTING</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Accepted Alternative Documents (Comma Separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. CBSE Mark Sheet, Provisional Certificate, Passing Slip"
                  value={reqFormData.alternative_documents_str}
                  onChange={(e) => setReqFormData({ ...reqFormData, alternative_documents_str: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
                <span className="text-[10px] text-slate-400 mt-0.5 block">
                  Leave empty if no alternative certificates are officially permitted.
                </span>
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Validity & Expiry Rules
                </label>
                <input
                  type="text"
                  placeholder="e.g. Permanent validity or Valid for 1 financial year"
                  value={reqFormData.validity_rules}
                  onChange={(e) => setReqFormData({ ...reqFormData, validity_rules: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Official Source Link
                </label>
                <input
                  type="url"
                  placeholder="https://tnesevai.tn.gov.in"
                  value={reqFormData.official_source_url}
                  onChange={(e) => setReqFormData({ ...reqFormData, official_source_url: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Accepted File Formats
                </label>
                <input
                  type="text"
                  value={reqFormData.accepted_formats}
                  onChange={(e) => setReqFormData({ ...reqFormData, accepted_formats: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Requirement Status
                </label>
                <select
                  value={reqFormData.status}
                  onChange={(e) => setReqFormData({ ...reqFormData, status: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                >
                  <option value="Current">Current (Active)</option>
                  <option value="Review Needed">Review Needed</option>
                  <option value="Outdated">Outdated / Deprecated</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Description / Guidance
                </label>
                <textarea
                  rows={3}
                  value={reqFormData.description}
                  onChange={(e) => setReqFormData({ ...reqFormData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditReqModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingReq}
                  className="px-5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white font-bold rounded-xl disabled:opacity-50"
                >
                  {savingReq ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* ADD REQUIREMENT MODAL */}
      {/* ========================================================= */}
      {addReqModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-xl max-w-xl w-full overflow-hidden border border-slate-200 animate-fadeIn my-8">
            <div className="p-5 bg-[#0f2942] text-white flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base">Add New Document Requirement</h3>
                <p className="text-xs text-slate-300">Creates a dynamic requirement record directly in the database</p>
              </div>
              <button onClick={() => setAddReqModalOpen(false)} className="text-slate-300 hover:text-white">
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateReqSubmit} className="p-6 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Target Service Profile <span className="text-rose-500">*</span>
                </label>
                <select
                  value={reqFormData.application_profile_id}
                  onChange={(e) => setReqFormData({ ...reqFormData, application_profile_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                  required
                >
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.jurisdiction})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Requirement Code <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. INCOME_CERTIFICATE_PROOF"
                  value={reqFormData.requirement_code}
                  onChange={(e) => setReqFormData({ ...reqFormData, requirement_code: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono font-bold focus:ring-2 focus:ring-[#0f2942] focus:outline-none uppercase"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Display Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Income Certificate (Tahsildar / e-Sevai)"
                  value={reqFormData.display_name}
                  onChange={(e) => setReqFormData({ ...reqFormData, display_name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Requirement Type
                </label>
                <select
                  value={reqFormData.requirement_type}
                  onChange={(e) => setReqFormData({
                    ...reqFormData,
                    requirement_type: e.target.value,
                    is_mandatory: e.target.value === 'REQUIRED'
                  })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                >
                  <option value="REQUIRED">REQUIRED (Mandatory)</option>
                  <option value="CONDITIONALLY_REQUIRED">CONDITIONALLY REQUIRED</option>
                  <option value="OPTIONAL">OPTIONAL SUPPORTING</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Accepted Alternative Documents (Comma Separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Salary Slip, Form 16, VAO Report"
                  value={reqFormData.alternative_documents_str}
                  onChange={(e) => setReqFormData({ ...reqFormData, alternative_documents_str: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Validity & Expiry Rules
                </label>
                <input
                  type="text"
                  placeholder="e.g. Valid for 1 financial year from issue date"
                  value={reqFormData.validity_rules}
                  onChange={(e) => setReqFormData({ ...reqFormData, validity_rules: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Official Source Link
                </label>
                <input
                  type="url"
                  placeholder="https://tnesevai.tn.gov.in"
                  value={reqFormData.official_source_url}
                  onChange={(e) => setReqFormData({ ...reqFormData, official_source_url: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Description / Guidance
                </label>
                <textarea
                  rows={2}
                  value={reqFormData.description}
                  onChange={(e) => setReqFormData({ ...reqFormData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                  placeholder="Instructions explaining what document the applicant must produce..."
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setAddReqModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingReq}
                  className="px-5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white font-bold rounded-xl disabled:opacity-50"
                >
                  {savingReq ? 'Creating...' : 'Create Requirement'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Adjudication Modal for Tab 1 */}
      {reviewModalOpen && selectedApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full overflow-hidden border border-slate-200">
            <div className="p-5 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 text-base">Adjudicate Application</h3>
              <p className="text-xs text-slate-500 mt-0.5">{selectedApp.reference_number} – {selectedApp.applicant_name}</p>
            </div>

            <form onSubmit={handleReviewSubmit} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Determination Decision
                </label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-semibold focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                >
                  <option value="APPROVED">APPROVE APPLICATION</option>
                  <option value="REJECTED">REJECT APPLICATION</option>
                  <option value="REVIEW_REQUIRED">FLAG FOR FURTHER REVIEW</option>
                  <option value="INCOMPLETE">MARK INCOMPLETE (REQUEST RE-UPLOAD)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Reviewer Notes & Rationale <span className="text-rose-500">*</span>
                </label>
                <textarea
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                  placeholder="Provide audit justification for approval, rejection, or required clarification..."
                  required
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setReviewModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg text-sm hover:bg-slate-50 font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingReview}
                  className="px-5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white font-bold rounded-lg text-sm disabled:opacity-50"
                >
                  {submittingReview ? 'Recording...' : 'Submit Determination'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboardPage;
