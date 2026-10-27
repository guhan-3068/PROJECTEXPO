import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { applicationsApi, documentsApi, verificationApi } from '../services/api';
import DocumentSlotCard from '../components/DocumentSlotCard';
import MismatchInspector from '../components/MismatchInspector';
import TamperAlert from '../components/TamperAlert';
import FieldCorrectionModal from '../components/FieldCorrectionModal';
import ActionPlanChecklist from '../components/ActionPlanChecklist';
import ConfidenceMeterModal from '../components/ConfidenceMeterModal';
import {
  FileText, Download, Play, Trash2, Edit3, ArrowLeft,
  CheckCircle, AlertTriangle, ShieldCheck, ExternalLink, Loader2,
  HelpCircle, Eye, Info, Sparkles, MapPin, Building, Gauge,
  Clock, CheckSquare, AlertCircle, FileCheck2
} from 'lucide-react';

const ApplicationViewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [slots, setSlots] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningVerif, setRunningVerif] = useState(false);
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [activeCorrection, setActiveCorrection] = useState({ isOpen: false, docId: null, field: null });
  const [confidenceModalOpen, setConfidenceModalOpen] = useState(false);
  const [error, setError] = useState('');
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [appData, docsData, slotsData] = await Promise.all([
        applicationsApi.getApplication(id),
        documentsApi.getApplicationDocuments(id),
        applicationsApi.getApplicationSlots(id),
      ]);
      setApplication(appData);
      setDocuments(docsData);
      setSlots(slotsData?.slots || []);

      // Try fetching existing verification result if already run
      try {
        const verData = await verificationApi.getVerificationResult(id);
        setVerificationResult(verData);
      } catch (e) {
        // Not run yet; if documents exist, run verification automatically
        if (docsData && docsData.length > 0) {
          try {
            const verData = await verificationApi.runVerification(id);
            setVerificationResult(verData);
          } catch (verErr) {
            setVerificationResult(null);
          }
        } else {
          setVerificationResult(null);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load application data');
    } finally {
      setLoading(false);
    }
  };

  const handleSlotUploadSuccess = async (requirementId, updatedDoc) => {
    setStatusMsg('Document uploaded to slot successfully! Re-running verification...');
    // Refresh slots and verification
    try {
      const [slotsData, docsData] = await Promise.all([
        applicationsApi.getApplicationSlots(id),
        documentsApi.getApplicationDocuments(id),
      ]);
      setSlots(slotsData?.slots || []);
      setDocuments(docsData);
      await triggerVerification();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSlotRemoveSuccess = async (requirementId, docId) => {
    setStatusMsg('Document removed from slot. Updating checklist...');
    try {
      const [slotsData, docsData] = await Promise.all([
        applicationsApi.getApplicationSlots(id),
        documentsApi.getApplicationDocuments(id),
      ]);
      setSlots(slotsData?.slots || []);
      setDocuments(docsData);
      await triggerVerification();
    } catch (err) {
      console.error(err);
    }
  };

  const triggerVerification = async () => {
    setRunningVerif(true);
    setError('');
    try {
      const res = await verificationApi.runVerification(id);
      setVerificationResult(res);
      const [updatedApp, slotsData] = await Promise.all([
        applicationsApi.getApplication(id),
        applicationsApi.getApplicationSlots(id),
      ]);
      setApplication(updatedApp);
      setSlots(slotsData?.slots || []);
      setStatusMsg('AI Verification analysis completed successfully.');
      setTimeout(() => setStatusMsg(''), 4000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification analysis failed. Please review uploaded files.');
    } finally {
      setRunningVerif(false);
    }
  };

  const handleDownloadReport = async () => {
    setDownloadingReport(true);
    setError('');
    setDownloadSuccess(false);
    try {
      await verificationApi.downloadReportBlob(
        application.id,
        application.reference_number || 'Report'
      );
      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 5000);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
        'Unable to download PDF report. Generating report on demand; please retry in a moment.'
      );
    } finally {
      setDownloadingReport(false);
    }
  };

  const handleDeleteApplication = async () => {
    if (!window.confirm('Delete this entire application and purge all associated encrypted documents from server?')) return;
    try {
      await applicationsApi.deleteApplication(application.id);
      navigate('/dashboard');
    } catch (err) {
      alert('Failed to delete application');
    }
  };

  const openCorrection = (docId, field) => {
    setActiveCorrection({
      isOpen: true,
      docId,
      field,
    });
  };

  const handleFieldUpdated = (updatedDoc) => {
    triggerVerification();
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center text-slate-500 text-sm">
        <Loader2 className="w-9 h-9 animate-spin mx-auto text-[#0f2942] mb-3" />
        <p className="font-semibold text-slate-700">Loading citizen verification cockpit...</p>
        <p className="text-xs text-slate-400 mt-1">Retrieving encrypted documents and compliance checklists</p>
      </div>
    );
  }

  if (!application) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="text-rose-600 font-semibold">{error || 'Application not found'}</p>
        <Link to="/dashboard" className="text-xs text-[#0f2942] font-bold mt-3 inline-block hover:underline">
          &larr; Return to Citizen Dashboard
        </Link>
      </div>
    );
  }

  // Compute Readiness Breakdown Metrics
  const breakdown = verificationResult?.readiness_breakdown || {};
  const requiredCount = breakdown.required_count ?? slots.filter((s) => s.requirement?.is_mandatory).length;
  const uploadedCount = breakdown.uploaded_count ?? slots.filter((s) => s.is_uploaded).length;
  const passingCount = breakdown.passing_count ?? slots.filter((s) => s.slot_status === 'PASSING').length;
  const needsReviewCount = breakdown.needs_review_count ?? slots.filter((s) => s.slot_status === 'NEEDS_REVIEW' || s.slot_status === 'ACTION_REQUIRED').length;
  const missingCount = breakdown.missing_count ?? slots.filter((s) => s.requirement?.is_mandatory && !s.is_uploaded).length;
  const overallReadiness = breakdown.readiness_status || application.readiness_status || (missingCount > 0 ? 'Documents Missing' : 'Action Required');
  const progressText = breakdown.progress_text || `${Math.min(uploadedCount, requiredCount)} of ${requiredCount} required documents uploaded and checked`;
  const progressPct = breakdown.progress_percentage || Math.round((Math.min(uploadedCount, requiredCount) / Math.max(requiredCount, 1)) * 100);

  // Overall readiness status badge design
  let readinessBadgeConfig = {
    bg: 'bg-rose-50 border-rose-200 text-rose-800',
    icon: <AlertTriangle className="w-4 h-4 text-rose-600" />,
    label: overallReadiness,
  };
  if (overallReadiness === 'Ready for Submission Review' || overallReadiness === 'Ready for Next Step') {
    readinessBadgeConfig = {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
      icon: <CheckCircle className="w-4 h-4 text-emerald-600" />,
      label: 'Ready for Submission Review',
    };
  } else if (overallReadiness === 'Verification In Progress') {
    readinessBadgeConfig = {
      bg: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: <Loader2 className="w-4 h-4 animate-spin text-blue-600" />,
      label: 'Verification In Progress',
    };
  } else if (overallReadiness === 'Documents Missing') {
    readinessBadgeConfig = {
      bg: 'bg-amber-50 border-amber-200 text-amber-800',
      icon: <Clock className="w-4 h-4 text-amber-600" />,
      label: 'Documents Missing',
    };
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Breadcrumb & Progress Stepper */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link
          to="/dashboard"
          className="inline-flex items-center text-xs font-bold text-slate-600 hover:text-[#0f2942] transition"
        >
          <ArrowLeft className="w-4 h-4 mr-1 text-slate-500" />
          Back to Citizen Dashboard
        </Link>

        {/* Stepper */}
        <div className="hidden lg:flex items-center space-x-2 text-[11px] font-semibold text-slate-400 bg-white px-4 py-2 rounded-xl border border-slate-200">
          <span className="text-[#0f2942] font-bold">1. Select Application</span>
          <span>&rarr;</span>
          <span className={uploadedCount > 0 ? 'text-[#0f2942] font-bold' : ''}>2. Slot Uploads</span>
          <span>&rarr;</span>
          <span className={verificationResult ? 'text-[#0f2942] font-bold' : ''}>3. AI Screening</span>
          <span>&rarr;</span>
          <span className={overallReadiness.includes('Ready') ? 'text-emerald-600 font-bold' : 'text-[#ea580c] font-bold'}>
            4. Download Report
          </span>
        </div>
      </div>

      {/* Main Service Cockpit Banner */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-[#0f2942] text-white">
                {application.profile?.category || 'Citizen Service'}
              </span>
              <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                {application.profile?.name}
              </h1>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                {application.profile?.jurisdiction}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-2">
              <span className="font-mono font-bold text-slate-800">
                Ref: {application.reference_number}
              </span>
              <span>&bull;</span>
              <span>Consent Recorded: {new Date(application.consent_timestamp || application.created_at).toLocaleDateString()}</span>
              <span>&bull;</span>
              <span className="text-slate-500">{slots.length} Requirement Slots Configured</span>
            </div>

            {(application.state || application.district || application.issuing_authority) && (
              <div className="flex flex-wrap items-center gap-2 mt-2.5 text-xs text-slate-600 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
                {application.state && (
                  <span className="inline-flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>State: <strong className="text-slate-800">{application.state}</strong></span>
                  </span>
                )}
                {application.district && (
                  <span>&bull; District: <strong className="text-slate-800">{application.district}</strong></span>
                )}
                {application.issuing_authority && (
                  <span className="inline-flex items-center space-x-1">
                    <span>&bull;</span>
                    <Building className="w-3.5 h-3.5 text-slate-400" />
                    <span>Authority: <strong className="text-slate-800">{application.issuing_authority}</strong></span>
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Check Everything Before Applying Button */}
            <button
              onClick={triggerVerification}
              disabled={runningVerif || uploadedCount === 0}
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold shadow-sm transition disabled:opacity-50"
              title="Run complete 10-step verification checks on all uploaded documents"
            >
              {runningVerif ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-orange-400" />
                  <span>Checking Everything...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Check Everything Before Applying</span>
                </>
              )}
            </button>

            {/* Confidence Meter Button */}
            <button
              onClick={() => setConfidenceModalOpen(true)}
              disabled={!verificationResult}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-xl text-xs font-bold border border-indigo-200 transition disabled:opacity-50"
              title="Inspect 6-dimension reliability confidence breakdown"
            >
              <Gauge className="w-4 h-4 text-indigo-600" />
              <span>Confidence Meter</span>
            </button>

            {/* Guaranteed Working PDF Download Button with QUBIX branding */}
            <button
              onClick={handleDownloadReport}
              disabled={downloadingReport}
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition disabled:opacity-50"
              title="Download official QUBIX verification audit PDF report"
            >
              {downloadingReport ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Generating PDF...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 text-white" />
                  <span>Download PDF Report</span>
                </>
              )}
            </button>

            <button
              onClick={handleDeleteApplication}
              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition"
              title="Delete this entire application and purge stored files"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Alerts */}
        {downloadSuccess && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2 animate-fadeIn">
            <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>
              <strong>Success!</strong> Your official QUBIX verification audit report PDF was downloaded successfully.
            </span>
          </div>
        )}

        {statusMsg && (
          <div className="mt-4 p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-800 flex items-center space-x-2">
            <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <span>{statusMsg}</span>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* ========================================================= */}
      {/* 6. APPLICATION READINESS DASHBOARD */}
      {/* ========================================================= */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-black uppercase tracking-wider text-[#ea580c]">
              Pre-Application Scrutiny Summary
            </span>
            <h2 className="text-lg font-black text-slate-900 mt-0.5">
              Application Readiness Dashboard
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Deterministic compliance audit against configured government & institutional submission standards
            </p>
          </div>

          {/* Overall Status Pill */}
          <div className={`px-4 py-2 rounded-xl border flex items-center space-x-2 text-xs font-bold ${readinessBadgeConfig.bg}`}>
            {readinessBadgeConfig.icon}
            <div>
              <span className="text-[10px] uppercase tracking-wider opacity-80 block">Overall Status</span>
              <span className="text-sm font-black">{readinessBadgeConfig.label}</span>
            </div>
          </div>
        </div>

        {/* 5 Core Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {/* 1. Required Documents */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Required Documents
            </span>
            <div className="text-2xl font-black text-slate-900 mt-1">
              {requiredCount}
            </div>
            <span className="text-[10px] text-slate-400 mt-0.5 block">Mandatory for service</span>
          </div>

          {/* 2. Uploaded Documents */}
          <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200">
            <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
              Uploaded Documents
            </span>
            <div className="text-2xl font-black text-blue-900 mt-1">
              {uploadedCount}
            </div>
            <span className="text-[10px] text-blue-600 mt-0.5 block">Total files in slots</span>
          </div>

          {/* 3. Passing Documents */}
          <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
            <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block">
              Passing Documents
            </span>
            <div className="text-2xl font-black text-emerald-800 mt-1">
              {passingCount}
            </div>
            <span className="text-[10px] text-emerald-600 mt-0.5 block">Satisfied all checks</span>
          </div>

          {/* 4. Review / Correction Needed */}
          <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200">
            <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider block">
              Needs Review / Action
            </span>
            <div className="text-2xl font-black text-amber-900 mt-1">
              {needsReviewCount}
            </div>
            <span className="text-[10px] text-amber-600 mt-0.5 block">Warnings or defects</span>
          </div>

          {/* 5. Missing Documents */}
          <div className="p-4 rounded-xl bg-rose-50/70 border border-rose-200 col-span-2 sm:col-span-1">
            <span className="text-[11px] font-bold text-rose-700 uppercase tracking-wider block">
              Missing Documents
            </span>
            <div className="text-2xl font-black text-rose-900 mt-1">
              {missingCount}
            </div>
            <span className="text-[10px] text-rose-600 mt-0.5 block">Mandatory pending</span>
          </div>
        </div>

        {/* Progress Bar: "3 of 5 required documents uploaded and checked" */}
        <div className="space-y-1.5 pt-2 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-slate-700">{progressText}</span>
            <span className="text-[#0f2942] font-mono">{progressPct}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                progressPct === 100 ? 'bg-emerald-600' : 'bg-[#0f2942]'
              }`}
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* ========================================================= */}
      {/* 2. DEDICATED INDIVIDUAL DOCUMENT CARDS FOR EACH REQUIREMENT */}
      {/* ========================================================= */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-black text-slate-900 flex items-center space-x-2">
              <FileCheck2 className="w-5 h-5 text-[#0f2942]" />
              <span>Document Requirements & Verification Cockpit</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Upload each certificate into its designated card below. Every document undergoes dedicated OCR field extraction, validity timeline check, and digital tampering screening.
            </p>
          </div>
          <span className="text-xs font-bold text-slate-500 bg-white border border-slate-200 px-3 py-1.5 rounded-xl self-start sm:self-center">
            {slots.length} Individual Requirement Slots
          </span>
        </div>

        {slots.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 text-center text-slate-400 text-sm border border-slate-200">
            No document requirements configured for this profile yet.
          </div>
        ) : (
          <div className="space-y-4">
            {slots.map((slot) => (
              <DocumentSlotCard
                key={slot.requirement.id}
                slot={slot}
                applicationId={application.id}
                onUploadSuccess={handleSlotUploadSuccess}
                onRemoveSuccess={handleSlotRemoveSuccess}
                isVerifyingAll={runningVerif}
              />
            ))}
          </div>
        )}
      </div>

      {/* Prioritized Action Plan & Checklist with 9-Point "How to Fix This?" Guidance */}
      {verificationResult && (
        <ActionPlanChecklist
          checklist={verificationResult.prioritized_checklist || []}
          actionPlan={verificationResult.action_plan || []}
          onRecheck={triggerVerification}
          isRechecking={runningVerif}
          onOpenUpload={() => {
            window.scrollTo({ top: 300, behavior: 'smooth' });
          }}
        />
      )}

      {/* Cross-Document Mismatch Inspector */}
      <MismatchInspector mismatches={verificationResult?.detected_mismatches || []} />

      {/* Forensic Tampering & Structural Anomaly Screening */}
      <TamperAlert tamperingFlags={verificationResult?.tampering_flags || []} />

      {/* OCR Field Correction Modal */}
      <FieldCorrectionModal
        isOpen={activeCorrection.isOpen}
        onClose={() => setActiveCorrection({ isOpen: false, docId: null, field: null })}
        documentId={activeCorrection.docId}
        field={activeCorrection.field}
        onFieldUpdated={handleFieldUpdated}
      />

      {/* Verification Confidence Meter Modal */}
      <ConfidenceMeterModal
        isOpen={confidenceModalOpen}
        onClose={() => setConfidenceModalOpen(false)}
        confidenceData={verificationResult?.confidence_summary}
        documentTitle={application.profile?.name}
      />
    </div>
  );
};

export default ApplicationViewPage;
