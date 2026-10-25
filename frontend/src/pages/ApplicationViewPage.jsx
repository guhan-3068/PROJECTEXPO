import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { applicationsApi, documentsApi, verificationApi } from '../services/api';
import ChecklistStatus from '../components/ChecklistStatus';
import DocumentUploader from '../components/DocumentUploader';
import ExpiryBadge from '../components/ExpiryBadge';
import MismatchInspector from '../components/MismatchInspector';
import TamperAlert from '../components/TamperAlert';
import FieldCorrectionModal from '../components/FieldCorrectionModal';
import ReadinessBadge from '../components/ReadinessBadge';
import ActionPlanChecklist from '../components/ActionPlanChecklist';
import ConfidenceMeterModal from '../components/ConfidenceMeterModal';
import {
  FileText, Download, Play, Trash2, Edit3, ArrowLeft,
  CheckCircle, AlertTriangle, ShieldCheck, ExternalLink, Loader2,
  HelpCircle, Eye, Info, Sparkles, MapPin, Building, Gauge
} from 'lucide-react';

const ApplicationViewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
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
      const [appData, docsData] = await Promise.all([
        applicationsApi.getApplication(id),
        documentsApi.getApplicationDocuments(id),
      ]);
      setApplication(appData);
      setDocuments(docsData);

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

  const handleUploadComplete = async (newDocs) => {
    setDocuments((prev) => [...prev, ...newDocs]);
    setStatusMsg('Documents uploaded successfully! Running AI verification checks...');
    await triggerVerification();
    setTimeout(() => setStatusMsg(''), 4000);
  };

  const triggerVerification = async () => {
    setRunningVerif(true);
    setError('');
    try {
      const res = await verificationApi.runVerification(id);
      setVerificationResult(res);
      const updatedApp = await applicationsApi.getApplication(id);
      setApplication(updatedApp);
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

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document from encrypted storage?')) return;
    try {
      await documentsApi.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      await triggerVerification();
    } catch (err) {
      alert('Failed to delete document');
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
    setDocuments((prev) =>
      prev.map((d) => (d.id === updatedDoc.id ? updatedDoc : d))
    );
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

  const overallStatus = application.status || 'DRAFT';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link
          to="/dashboard"
          className="inline-flex items-center text-xs font-bold text-slate-600 hover:text-[#0f2942] transition"
        >
          <ArrowLeft className="w-4 h-4 mr-1 text-slate-500" />
          Back to Citizen Dashboard
        </Link>

        {/* Progress Stepper */}
        <div className="hidden lg:flex items-center space-x-2 text-[11px] font-semibold text-slate-400 bg-white px-4 py-2 rounded-xl border border-slate-200">
          <span className="text-[#0f2942] font-bold">1. Select Application</span>
          <span>&rarr;</span>
          <span className={documents.length > 0 ? 'text-[#0f2942] font-bold' : ''}>2. Upload Documents</span>
          <span>&rarr;</span>
          <span className={verificationResult ? 'text-[#0f2942] font-bold' : ''}>3. AI Verification</span>
          <span>&rarr;</span>
          <span className="text-[#ea580c] font-bold">4. Download Report</span>
        </div>
      </div>

      {/* Main Cockpit Banner */}
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
              <span className="text-slate-500">{documents.length} Document(s) Uploaded</span>
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
            <button
              onClick={triggerVerification}
              disabled={runningVerif || documents.length === 0}
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold shadow-sm transition disabled:opacity-50"
              title="Run automated verification checks on uploaded documents"
            >
              {runningVerif ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-orange-400" />
                  <span>Verifying Documents...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white text-white" />
                  <span>Re-Run Verification</span>
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

            {/* Guaranteed Working PDF Download Button */}
            <button
              onClick={handleDownloadReport}
              disabled={downloadingReport}
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition disabled:opacity-50"
              title="Download official PDF audit report"
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

        {/* Informational Alerts */}
        {downloadSuccess && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2 animate-fadeIn">
            <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>
              <strong>Success!</strong> Your official verification audit report PDF was downloaded successfully.
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

      {/* Official Readiness Status Card */}
      {verificationResult && (
        <ReadinessBadge
          status={verificationResult.readiness_status || application.readiness_status || 'Action Required'}
          score={verificationResult.readiness_score || '0%'}
        />
      )}

      {/* Prioritized Action Plan & Checklist with 9-Point "How to Fix This?" Guidance */}
      {verificationResult && (
        <ActionPlanChecklist
          checklist={verificationResult.prioritized_checklist || []}
          actionPlan={verificationResult.action_plan || []}
          onRecheck={triggerVerification}
          isRechecking={runningVerif}
          onOpenUpload={() => {
            const el = document.getElementById('document-uploader-section');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }}
        />
      )}

      {/* Requirement Checklist Section */}
      <ChecklistStatus
        satisfied={verificationResult?.satisfied_requirements || []}
        missing={verificationResult?.missing_requirements || []}
        overallStatus={overallStatus}
        recommendedActions={verificationResult?.recommended_actions || []}
      />

      {/* Document Uploader */}
      <div id="document-uploader-section">
        <DocumentUploader
          applicationId={application.id}
          onUploadComplete={handleUploadComplete}
        />
      </div>

      {/* Uploaded Documents Inventory & Recognized Entities */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <span>Uploaded Documents & OCR Extractions</span>
              <span className="text-xs bg-slate-100 text-slate-700 font-bold px-2 py-0.5 rounded-full">
                {documents.length}
              </span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Inspected through high-precision OCR; sensitive identifiers are masked for privacy
            </p>
          </div>
          <span className="text-[11px] font-semibold text-slate-500 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-lg self-start sm:self-center">
            🔒 AES-256 Encrypted at Rest
          </span>
        </div>

        {documents.length === 0 ? (
          <div className="p-10 text-center text-slate-400 text-xs italic">
            No files uploaded for this application yet. Use the upload box above to add your certificates.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {documents.map((doc) => {
              const expField = doc.extracted_fields?.find((f) => f.field_key === 'expiry_date');
              const expDetails =
                verificationResult?.expired_documents?.find((e) => e.document_id === doc.id) ||
                verificationResult?.expiring_soon_documents?.find((e) => e.document_id === doc.id);

              return (
                <div key={doc.id} className="p-5 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-start space-x-3">
                      <div className="p-3 bg-slate-100 text-[#0f2942] rounded-xl flex-shrink-0 mt-0.5">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-sm text-slate-900 flex flex-wrap items-center gap-2">
                          <span>{doc.original_filename}</span>
                          <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-md bg-[#0f2942]/10 text-[#0f2942] border border-[#0f2942]/20">
                            {doc.doc_category.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <div className="text-xs text-slate-500 mt-1 flex flex-wrap items-center gap-2">
                          <span>{(doc.file_size_bytes / 1024).toFixed(0)} KB</span>
                          <span>&bull;</span>
                          <span>OCR Confidence: {Math.round(doc.ocr_overall_confidence * 100)}%</span>
                          <span>&bull;</span>
                          <span>{doc.mime_type}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 self-start sm:self-center">
                      <ExpiryBadge
                        status={expDetails?.status || (expField ? 'VALID' : 'EXPIRY_DATE_NOT_FOUND')}
                        daysRemaining={expDetails?.days_until_expiry}
                        expiryDate={expField?.effective_value}
                      />
                      <a
                        href={documentsApi.downloadDocumentUrl(doc.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="p-2 text-slate-500 hover:text-[#0f2942] hover:bg-slate-100 rounded-lg transition"
                        title="View Decrypted File in Browser"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                        title="Delete Document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Extracted Fields Grid */}
                  <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200">
                    <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                      <span>Recognized Entities & Values</span>
                      <span className="text-[10px] text-slate-400 font-normal">
                        Click pencil icon on any field to correct OCR mistakes
                      </span>
                    </div>

                    {doc.extracted_fields && doc.extracted_fields.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
                        {doc.extracted_fields.map((f) => (
                          <div
                            key={f.id}
                            className="p-2.5 bg-white rounded-xl border border-slate-200 text-xs space-y-1 relative group hover:border-slate-300 transition"
                          >
                            <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase font-bold">
                              <span>{f.field_key.replace(/_/g, ' ')}</span>
                              <button
                                onClick={() => openCorrection(doc.id, f)}
                                className="text-slate-400 hover:text-brand-600 p-0.5"
                                title="Correct this OCR field"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                            <div className="font-bold text-slate-900 truncate">
                              {f.effective_value || '<Not detected>'}
                            </div>
                            {f.is_user_corrected && (
                              <span className="inline-block text-[9px] bg-purple-50 text-purple-700 px-1.5 py-0.2 rounded font-bold border border-purple-200">
                                Corrected by User
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400 italic">No text entities recognized by OCR.</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

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
