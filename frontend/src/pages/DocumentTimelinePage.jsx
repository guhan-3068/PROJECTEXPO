import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Calendar, Clock, AlertTriangle, ArrowLeft, ArrowRight, Filter, RefreshCw,
  Upload, ShieldCheck, CheckCircle2, Edit3, Bell, ExternalLink,
  Loader2, X, Sparkles, FileText, ChevronRight, HelpCircle, AlertCircle, Info
} from 'lucide-react';
import { timelineApi } from '../services/api';

const STATUS_CONFIG = {
  'ACTIVE': {
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    label: 'Active & Valid',
    icon: CheckCircle2,
    color: 'text-emerald-600'
  },
  'EXPIRING_SOON': {
    badge: 'bg-amber-100 text-amber-800 border-amber-300',
    label: 'Expiring Soon',
    icon: Clock,
    color: 'text-amber-600'
  },
  'EXPIRED': {
    badge: 'bg-rose-100 text-rose-800 border-rose-300',
    label: 'Past Validity',
    icon: AlertTriangle,
    color: 'text-rose-600'
  },
  'NO_EXPIRY': {
    badge: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    label: 'Permanent (Lifetime Validity)',
    icon: ShieldCheck,
    color: 'text-indigo-600'
  },
  'VALIDITY_NEEDS_CONFIRMATION': {
    badge: 'bg-slate-100 text-slate-700 border-slate-300',
    label: 'Validity Needs Confirmation',
    icon: HelpCircle,
    color: 'text-slate-500'
  },
  'RENEWAL_IN_PROGRESS': {
    badge: 'bg-purple-100 text-purple-800 border-purple-300',
    label: 'Renewal in Progress',
    icon: RefreshCw,
    color: 'text-purple-600'
  }
};

const DocumentTimelinePage = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [viewMode, setViewMode] = useState('timeline'); // 'timeline' or 'calendar'

  // Modal states
  const [dateModal, setDateModal] = useState({ isOpen: false, record: null, issueDate: '', expiryDate: '', saving: false });
  const [renewModal, setRenewModal] = useState({ isOpen: false, record: null, file: null, uploading: false, result: null });
  const [affectedModal, setAffectedModal] = useState({ isOpen: false, apps: [], docName: '' });

  useEffect(() => {
    fetchRecords();
  }, [statusFilter]);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const data = await timelineApi.getRecords(statusFilter);
      setRecords(data);
    } catch (err) {
      console.error('Failed to load timeline records', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDateModal = (record) => {
    setDateModal({
      isOpen: true,
      record,
      issueDate: record.issue_date || '',
      expiryDate: record.expiry_date || '',
      saving: false
    });
  };

  const handleSaveDates = async () => {
    if (!dateModal.record) return;
    setDateModal(prev => ({ ...prev, saving: true }));
    try {
      await timelineApi.updateDates(dateModal.record.document_id, dateModal.issueDate, dateModal.expiryDate);
      await fetchRecords();
      setDateModal({ isOpen: false, record: null, issueDate: '', expiryDate: '', saving: false });
    } catch (err) {
      alert('Failed to update dates: ' + (err.response?.data?.detail || err.message));
      setDateModal(prev => ({ ...prev, saving: false }));
    }
  };

  const handleOpenRenewModal = (record) => {
    setRenewModal({
      isOpen: true,
      record,
      file: null,
      uploading: false,
      result: null
    });
  };

  const handleUploadRenewedFile = async (e) => {
    e.preventDefault();
    if (!renewModal.file || !renewModal.record) return;
    setRenewModal(prev => ({ ...prev, uploading: true }));
    try {
      const res = await timelineApi.uploadRenewedDocument(renewModal.record.document_id, renewModal.file);
      setRenewModal(prev => ({ ...prev, uploading: false, result: res }));
      await fetchRecords();
    } catch (err) {
      alert('Failed to upload renewed file: ' + (err.response?.data?.detail || err.message));
      setRenewModal(prev => ({ ...prev, uploading: false }));
    }
  };

  const handleViewAffected = async (docId, docName) => {
    try {
      const apps = await timelineApi.getAffectedApplications(docId);
      setAffectedModal({ isOpen: true, apps, docName });
    } catch (err) {
      console.error('Failed to fetch affected applications', err);
    }
  };

  const handleReminderChange = async (recordId, reminderDays) => {
    try {
      await timelineApi.setReminder(recordId, reminderDays, true);
      await fetchRecords();
    } catch (err) {
      console.error('Failed to update reminder', err);
    }
  };

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
          Certificate Validity & Renewal Tracker
        </span>
      </div>

      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-[#0f2942] via-[#1e3a8a] to-[#0f2942] text-white p-6 sm:p-8 rounded-3xl shadow-md relative overflow-hidden">
        <div className="max-w-3xl space-y-2 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-bold border border-blue-400/30">
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            <span>Document Timeline & Renewal History</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Certificate Issue, Expiry & Renewal Timeline
          </h1>
          <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
            Manage important certificate validity dates, configure citizen reminders (30d / 15d / 7d), and upload renewed documents with side-by-side entity comparisons. Lifetime certificates (Aadhaar, Community, TC) are protected from false expiration warnings.
          </p>
        </div>
      </div>

      {/* Filter and View Toggles Bar */}
      <div className="bg-white p-4 sm:p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {['ALL', 'ACTIVE', 'EXPIRING_SOON', 'EXPIRED', 'NO_EXPIRY', 'VALIDITY_NEEDS_CONFIRMATION'].map((statusKey) => (
            <button
              key={statusKey}
              onClick={() => setStatusFilter(statusKey)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition whitespace-nowrap ${
                statusFilter === statusKey
                  ? 'bg-[#0f2942] text-white shadow-sm'
                  : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {statusKey === 'ALL' ? 'All Documents' : (STATUS_CONFIG[statusKey]?.label || statusKey)}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-1.5 self-start sm:self-center bg-slate-100 p-1 rounded-xl text-xs font-bold">
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-3 py-1 rounded-lg transition ${viewMode === 'timeline' ? 'bg-white text-[#0f2942] shadow-sm' : 'text-slate-500'}`}
          >
            Chronological View
          </button>
          <button
            onClick={() => setViewMode('calendar')}
            className={`px-3 py-1 rounded-lg transition ${viewMode === 'calendar' ? 'bg-white text-[#0f2942] shadow-sm' : 'text-slate-500'}`}
          >
            Calendar Overview
          </button>
        </div>
      </div>

      {/* Main Records Display */}
      {loading ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-[#0f2942] mx-auto" />
          <p className="text-xs text-slate-500 font-semibold">Synchronizing document lifecycle records...</p>
        </div>
      ) : records.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
          <Calendar className="w-12 h-12 text-slate-300 mx-auto" />
          <h4 className="text-base font-bold text-slate-800">No documents in your timeline yet</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Upload certificates via a Pre-Application Check or your Dashboard to track issue dates, validity periods, and renewal milestones.
          </p>
          <Link
            to="/pre-check"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-[#ea580c] text-white text-xs font-bold rounded-xl hover:bg-[#c2410c] transition"
          >
            <span>Start Pre-Application Check</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : viewMode === 'timeline' ? (
        /* Chronological Timeline View */
        <div className="relative border-l-2 border-slate-200 ml-4 sm:ml-6 pl-6 sm:pl-8 space-y-8">
          {records.map((rec) => {
            const cfg = STATUS_CONFIG[rec.validity_status] || STATUS_CONFIG['VALIDITY_NEEDS_CONFIRMATION'];
            const StatusIcon = cfg.icon;

            return (
              <div key={rec.id} className="relative group">
                {/* Timeline node dot */}
                <div className={`absolute -left-[35px] sm:-left-[43px] top-1.5 w-6 h-6 rounded-full border-4 border-white shadow-sm flex items-center justify-center ${cfg.color.replace('text-', 'bg-')}`}>
                  <StatusIcon className="w-3 h-3 text-white" />
                </div>

                {/* Timeline Card */}
                <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${cfg.badge}`}>
                          {cfg.label}
                        </span>
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                          {rec.doc_category.replace(/_/g, ' ')}
                        </span>
                        {rec.renewal_status === 'RENEWED_AND_VERIFIED' && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                            Renewed Version Active
                          </span>
                        )}
                      </div>

                      <h3 className="text-base font-black text-slate-900">
                        {rec.document_name}
                      </h3>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 pt-0.5">
                        <span>Issue Date: <strong className="text-slate-800">{rec.issue_date || 'Not specified'}</strong></span>
                        <span>&bull;</span>
                        <span>Expiry Date: <strong className="text-slate-800">{rec.expiry_date || (rec.validity_status === 'NO_EXPIRY' ? 'Permanent' : 'Not detected')}</strong></span>
                        {rec.days_remaining !== null && (
                          <>
                            <span>&bull;</span>
                            <span className={rec.days_remaining < 0 ? 'text-rose-600 font-bold' : (rec.days_remaining <= 30 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold')}>
                              {rec.days_remaining < 0 ? `Expired ${Math.abs(rec.days_remaining)}d ago` : `${rec.days_remaining}d remaining`}
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex flex-wrap items-center gap-2 self-start">
                      <button
                        onClick={() => handleOpenDateModal(rec)}
                        className="inline-flex items-center space-x-1 px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition"
                        title="Review or correct issue/expiry dates"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        <span>Edit Dates</span>
                      </button>

                      {rec.validity_status !== 'NO_EXPIRY' && (
                        <button
                          onClick={() => handleOpenRenewModal(rec)}
                          className="inline-flex items-center space-x-1 px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition shadow-sm"
                          title="Upload renewed certificate"
                        >
                          <Upload className="w-3.5 h-3.5" />
                          <span>Renew / Replace</span>
                        </button>
                      )}

                      <button
                        onClick={() => handleViewAffected(rec.document_id, rec.document_name)}
                        className="inline-flex items-center space-x-1 px-2.5 py-1.5 bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 text-xs font-bold rounded-xl transition border border-slate-200"
                        title="Show which applications use this document"
                      >
                        <span>Affected Apps</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  {/* Validity explanation */}
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start space-x-2">
                    <Info className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                    <p className="leading-relaxed">
                      {rec.validity_explanation}
                    </p>
                  </div>

                  {/* Reminder and comparison controls */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-slate-100 text-xs">
                    {rec.validity_status !== 'NO_EXPIRY' ? (
                      <div className="flex items-center space-x-2 text-slate-600">
                        <Bell className="w-3.5 h-3.5 text-slate-400" />
                        <span>Expiry Reminder:</span>
                        <select
                          value={rec.reminder_days_configured}
                          onChange={(e) => handleReminderChange(rec.id, Number(e.target.value))}
                          className="px-2 py-1 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-800"
                        >
                          <option value={30}>30 Days Before</option>
                          <option value={15}>15 Days Before</option>
                          <option value={7}>7 Days Before</option>
                        </select>
                      </div>
                    ) : (
                      <span className="text-slate-400 text-[11px] italic">
                        Permanent certificate; no expiration reminders required.
                      </span>
                    )}

                    {rec.previous_document_name && (
                      <span className="text-[11px] text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                        Renewed from: <strong>{rec.previous_document_name}</strong>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Calendar Overview Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {records.map((rec) => {
            const cfg = STATUS_CONFIG[rec.validity_status] || STATUS_CONFIG['VALIDITY_NEEDS_CONFIRMATION'];
            return (
              <div key={rec.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${cfg.badge}`}>
                      {cfg.label}
                    </span>
                    <span className="text-xs text-slate-400">
                      {rec.doc_category.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <h4 className="font-black text-slate-900 text-sm truncate">
                    {rec.document_name}
                  </h4>

                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Issued:</span>
                      <span className="font-bold text-slate-800">{rec.issue_date || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Expires:</span>
                      <span className="font-bold text-slate-800">{rec.expiry_date || (rec.validity_status === 'NO_EXPIRY' ? 'Permanent' : 'Unconfirmed')}</span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-600 line-clamp-2">
                    {rec.validity_explanation}
                  </p>
                </div>

                <div className="flex items-center space-x-2 pt-2 border-t border-slate-100">
                  <button
                    onClick={() => handleOpenDateModal(rec)}
                    className="flex-1 py-1.5 px-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition text-center"
                  >
                    Edit Dates
                  </button>
                  {rec.validity_status !== 'NO_EXPIRY' && (
                    <button
                      onClick={() => handleOpenRenewModal(rec)}
                      className="flex-1 py-1.5 px-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition text-center"
                    >
                      Renew
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Date Correction Modal */}
      {dateModal.isOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
            <div className="bg-[#0f2942] text-white p-5 flex items-start justify-between">
              <div>
                <h3 className="font-black text-base">Edit Certificate Dates</h3>
                <p className="text-xs text-slate-300">
                  {dateModal.record?.document_name}
                </p>
              </div>
              <button
                onClick={() => setDateModal({ isOpen: false, record: null, issueDate: '', expiryDate: '', saving: false })}
                className="p-1 text-slate-300 hover:text-white rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="font-bold text-slate-700 block">
                  Issue Date (DD/MM/YYYY or YYYY-MM-DD):
                </label>
                <input
                  type="text"
                  placeholder="e.g. 15/05/2024"
                  value={dateModal.issueDate}
                  onChange={(e) => setDateModal(prev => ({ ...prev, issueDate: e.target.value }))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
                />
              </div>

              {dateModal.record?.validity_status !== 'NO_EXPIRY' ? (
                <div className="space-y-1.5">
                  <label className="font-bold text-slate-700 block">
                    Expiry Date (DD/MM/YYYY or YYYY-MM-DD):
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 31/03/2026"
                    value={dateModal.expiryDate}
                    onChange={(e) => setDateModal(prev => ({ ...prev, expiryDate: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:ring-2 focus:ring-[#0f2942]"
                  />
                  <p className="text-[10px] text-slate-400">
                    Leave blank if document has lifetime validity or expiry is unconfirmed.
                  </p>
                </div>
              ) : (
                <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-900 text-xs">
                  This document type ({dateModal.record?.doc_category}) has lifetime validity and does not require an expiration date.
                </div>
              )}
            </div>

            <div className="bg-slate-50 p-4 border-t border-slate-200 flex justify-end space-x-2">
              <button
                onClick={() => setDateModal({ isOpen: false, record: null, issueDate: '', expiryDate: '', saving: false })}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl text-xs transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveDates}
                disabled={dateModal.saving}
                className="px-5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white font-bold rounded-xl text-xs transition disabled:opacity-50"
              >
                {dateModal.saving ? 'Saving...' : 'Save Dates'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Renew Document Modal & Side-by-Side Comparison */}
      {renewModal.isOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-150">
            <div className="bg-emerald-700 text-white p-5 flex items-start justify-between">
              <div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-white/20 text-emerald-100">
                  Document Renewal Workflow
                </span>
                <h3 className="font-black text-base mt-1">
                  Upload Renewed Certificate
                </h3>
                <p className="text-xs text-emerald-100">
                  Replacing: {renewModal.record?.document_name}
                </p>
              </div>
              <button
                onClick={() => setRenewModal({ isOpen: false, record: null, file: null, uploading: false, result: null })}
                className="p-1 text-emerald-200 hover:text-white rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              {!renewModal.result ? (
                <form onSubmit={handleUploadRenewedFile} className="space-y-4">
                  <div className="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center space-y-2 hover:border-emerald-500 transition">
                    <Upload className="w-8 h-8 text-emerald-600 mx-auto" />
                    <p className="font-bold text-slate-800">
                      Select your renewed certificate (PDF or JPEG)
                    </p>
                    <p className="text-[11px] text-slate-400">
                      The system will run OCR, extract new issue/expiry dates, and compare values against your previous certificate.
                    </p>
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => setRenewModal(prev => ({ ...prev, file: e.target.files[0] }))}
                      className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer pt-2"
                    />
                  </div>

                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      onClick={() => setRenewModal({ isOpen: false, record: null, file: null, uploading: false, result: null })}
                      className="px-4 py-2 bg-slate-200 text-slate-700 font-bold rounded-xl text-xs"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={!renewModal.file || renewModal.uploading}
                      className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition disabled:opacity-50"
                    >
                      {renewModal.uploading ? 'Processing Renewal...' : 'Upload & Compare'}
                    </button>
                  </div>
                </form>
              ) : (
                /* Side-by-side comparison results */
                <div className="space-y-4">
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>
                      <strong>Renewal Successful!</strong> New certificate linked and application checklist updated.
                    </span>
                  </div>

                  <h4 className="font-extrabold text-slate-900 uppercase tracking-wider text-[11px]">
                    Side-by-Side Version Comparison
                  </h4>

                  <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden">
                    <div className="grid grid-cols-3 p-2.5 bg-slate-50 font-bold text-slate-500 text-[10px] uppercase">
                      <span>Attribute</span>
                      <span>Prior Version</span>
                      <span>Renewed Version</span>
                    </div>
                    {renewModal.result.comparison?.field_diffs?.map((diff, i) => (
                      <div key={i} className="grid grid-cols-3 p-2.5 text-xs">
                        <span className="font-bold text-slate-800">{diff.field}</span>
                        <span className="text-slate-500">{diff.old_version}</span>
                        <span className={`font-bold ${diff.is_changed ? 'text-emerald-700' : 'text-slate-800'}`}>
                          {diff.new_version} {diff.is_changed && '✓'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="text-right pt-2">
                    <button
                      onClick={() => setRenewModal({ isOpen: false, record: null, file: null, uploading: false, result: null })}
                      className="px-5 py-2 bg-[#0f2942] text-white font-bold rounded-xl text-xs"
                    >
                      Finish
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Affected Applications Modal */}
      {affectedModal.isOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
            <div className="bg-[#0f2942] text-white p-5 flex items-start justify-between">
              <div>
                <h3 className="font-black text-base">Associated Applications</h3>
                <p className="text-xs text-slate-300">
                  {affectedModal.docName}
                </p>
              </div>
              <button
                onClick={() => setAffectedModal({ isOpen: false, apps: [], docName: '' })}
                className="p-1 text-slate-300 hover:text-white rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-3 text-xs">
              {affectedModal.apps.length === 0 ? (
                <p className="text-slate-500 italic text-center py-4">
                  This document is not currently required by any of your active applications.
                </p>
              ) : (
                affectedModal.apps.map((app, i) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{app.profile_name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">Ref: {app.reference_number}</span>
                    </div>
                    <p className="text-slate-600">
                      {app.impact_description}
                    </p>
                    <Link
                      to={`/application/${app.application_id}`}
                      className="text-[11px] font-bold text-indigo-700 hover:underline inline-block pt-1"
                    >
                      Open Application Cockpit &rarr;
                    </Link>
                  </div>
                ))
              )}
            </div>

            <div className="bg-slate-50 p-3 border-t border-slate-200 text-right">
              <button
                onClick={() => setAffectedModal({ isOpen: false, apps: [], docName: '' })}
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

export default DocumentTimelinePage;
