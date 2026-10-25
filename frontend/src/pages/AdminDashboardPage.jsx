import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminApi } from '../services/api';
import { ShieldCheck, AlertTriangle, CheckCircle, XCircle, Clock, ExternalLink, Filter } from 'lucide-react';

const AdminDashboardPage = () => {
  const [applications, setApplications] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [decision, setDecision] = useState('APPROVED');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchApplications();
  }, [filter]);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const data = await adminApi.listApplications(filter || null);
      setApplications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openReviewModal = (app) => {
    setSelectedApp(app);
    setDecision('APPROVED');
    setNotes('');
    setReviewModalOpen(true);
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!notes.trim()) {
      alert('Please enter review rationale notes');
      return;
    }
    setSubmitting(true);
    try {
      await adminApi.submitReview(selectedApp.id, decision, notes);
      setReviewModalOpen(false);
      fetchApplications();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <span className="p-1.5 bg-amber-100 text-amber-800 rounded-lg text-xs font-bold uppercase tracking-wider">
              Admin Portal
            </span>
            <h1 className="text-2xl font-bold text-slate-900">Verification Adjudication Queue</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Review flagged applications, resolve mismatches, and approve or reject submissions with full audit trail.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-xs font-semibold px-3 py-2 border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Statuses</option>
            <option value="REVIEW_REQUIRED">Review Required</option>
            <option value="INCOMPLETE">Incomplete</option>
            <option value="COMPLETE">Complete</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {/* Applications Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading review queue...</div>
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
                  <th className="px-5 py-3.5">Risk & Mismatch Flags</th>
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
                        <span className="text-emerald-600 font-semibold text-[11px]">✓ No Flags</span>
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
                        Inspect
                      </Link>
                      <button
                        onClick={() => openReviewModal(app)}
                        className="inline-flex items-center px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-medium transition"
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

      {/* Adjudication Modal */}
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
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none"
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
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  placeholder="Provide audit justification for approval, rejection, or required clarification..."
                  required
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setReviewModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg text-sm hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg text-sm disabled:opacity-50"
                >
                  {submitting ? 'Recording...' : 'Submit Determination'}
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
