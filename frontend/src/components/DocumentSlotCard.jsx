import React, { useState, useRef } from 'react';
import {
  FileText, Upload, RefreshCw, Trash2, CheckCircle, AlertTriangle,
  ExternalLink, Eye, Info, ShieldCheck, Clock, FileCheck, HelpCircle,
  Loader2, Cpu, KeyRound
} from 'lucide-react';
import ForensicAuditModal from './ForensicAuditModal';
import { documentsApi } from '../services/api';

const DocumentSlotCard = ({
  slot,
  applicationId,
  onUploadSuccess,
  onRemoveSuccess,
  isVerifyingAll
}) => {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [auditModalOpen, setAuditModalOpen] = useState(false);
  const [auditData, setAuditData] = useState(null);
  const [loadingAudit, setLoadingAudit] = useState(false);

  const req = slot.requirement || {};
  const doc = slot.uploaded_document;
  const isUploaded = !!doc;
  const evaluation = doc?.evaluation || {};
  const dims = evaluation?.dimensions || {};

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setErrorMsg('');
    try {
      const updatedDoc = await documentsApi.uploadSlotDocument(
        applicationId,
        req.id,
        file,
        req.requirement_code
      );
      if (onUploadSuccess) {
        onUploadSuccess(req.id, updatedDoc);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Failed to upload document to this slot.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleTriggerUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleRemove = async () => {
    if (!doc?.id) return;
    if (!window.confirm(`Are you sure you want to remove the document uploaded for "${req.display_name}"?`)) {
      return;
    }
    try {
      await documentsApi.deleteDocument(doc.id);
      if (onRemoveSuccess) {
        onRemoveSuccess(req.id, doc.id);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to remove document.');
    }
  };

  const handleViewAudit = async () => {
    if (!doc?.id) return;
    setLoadingAudit(true);
    try {
      const data = await documentsApi.getDocumentAudit(doc.id);
      setAuditData(data);
      setAuditModalOpen(true);
    } catch (err) {
      alert('Failed to retrieve forensic scorecard.');
    } finally {
      setLoadingAudit(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 KB';
    if (bytes >= 1048576) {
      return `${(bytes / 1048576).toFixed(1)} MB`;
    }
    return `${Math.round(bytes / 1024)} KB`;
  };

  // Requirement status badge
  const reqType = req.requirement_type || (req.is_mandatory ? 'REQUIRED' : 'OPTIONAL');
  let typeBadge = (
    <span className="text-[11px] font-black px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
      Mandatory / Required
    </span>
  );
  if (reqType === 'CONDITIONALLY_REQUIRED') {
    typeBadge = (
      <span className="text-[11px] font-black px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
        Conditionally Required
      </span>
    );
  } else if (!req.is_mandatory) {
    typeBadge = (
      <span className="text-[11px] font-black px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
        Optional Supporting
      </span>
    );
  }

  // Dimension pill helper
  const renderDimensionPill = (dim, label, statusKey = 'status', labelKey = 'label') => {
    if (!dim) return null;
    const status = dim[statusKey];
    const text = dim[labelKey] || dim.note || status;

    let badgeClass = 'bg-slate-100 text-slate-700 border-slate-200';
    let icon = <Info className="w-3 h-3" />;

    if (status === 'PASS' || status === 'READY') {
      badgeClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
      icon = <CheckCircle className="w-3 h-3 text-emerald-600" />;
    } else if (status === 'WARNING' || status === 'PHYSICAL_REQUIRED' || status === 'EXPIRING_SOON') {
      badgeClass = 'bg-amber-50 text-amber-800 border-amber-200';
      icon = <AlertTriangle className="w-3 h-3 text-amber-600" />;
    } else if (status === 'FAIL' || status === 'EXPIRED' || status === 'NEEDS_REVIEW') {
      badgeClass = 'bg-rose-50 text-rose-800 border-rose-200';
      icon = <AlertTriangle className="w-3 h-3 text-rose-600" />;
    }

    return (
      <div className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-semibold ${badgeClass}`}>
        {icon}
        <span className="font-bold text-slate-600">{label}:</span>
        <span className="truncate max-w-[140px]">{text}</span>
      </div>
    );
  };

  // Authenticity pill strictly displaying one of the 3 outcomes
  const authenticityResult = doc?.authenticity_result || dims.authenticity_screening?.result || 'No obvious manipulation detected';
  let authPillClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
  let authIcon = <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />;
  if (authenticityResult === 'Potential manipulation detected') {
    authPillClass = 'bg-rose-50 text-rose-800 border-rose-200';
    authIcon = <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />;
  } else if (authenticityResult === 'Inconclusive — further verification required') {
    authPillClass = 'bg-amber-50 text-amber-800 border-amber-200';
    authIcon = <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />;
  }

  return (
    <div className={`bg-white rounded-2xl border transition-all duration-200 overflow-hidden shadow-sm hover:shadow-md ${
      isUploaded
        ? slot.slot_status === 'PASSING'
          ? 'border-emerald-200'
          : slot.slot_status === 'NEEDS_REVIEW'
          ? 'border-amber-200'
          : 'border-rose-200'
        : 'border-slate-200'
    }`}>
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.jpg,.jpeg,.png"
      />

      {/* Card Header */}
      <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            {typeBadge}
            <span className="text-[11px] font-mono font-bold text-slate-400">
              #{req.sort_order || 1}
            </span>
            {req.status === 'Review Needed' && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                Rule Under Periodic Review
              </span>
            )}
          </div>
          <h3 className="text-base font-black text-slate-900 tracking-tight">
            {req.display_name}
          </h3>
          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
            {req.description}
          </p>
        </div>

        {/* Slot State Status Pill */}
        <div className="self-start md:self-center">
          {isUploaded ? (
            <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold ${
              slot.slot_status === 'PASSING'
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                : slot.slot_status === 'NEEDS_REVIEW'
                ? 'bg-amber-100 text-amber-800 border border-amber-200'
                : 'bg-rose-100 text-rose-800 border border-rose-200'
            }`}>
              {slot.slot_status === 'PASSING' ? (
                <>
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Uploaded & Passing</span>
                </>
              ) : slot.slot_status === 'NEEDS_REVIEW' ? (
                <>
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Needs Manual Review</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                  <span>Action Required</span>
                </>
              )}
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>Slot Awaiting Document</span>
            </span>
          )}
        </div>
      </div>

      {/* Requirement Details Bar */}
      <div className="bg-slate-50/70 px-5 py-3 border-b border-slate-100 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        {/* Alternative documents accepted */}
        <div>
          <span className="font-bold text-slate-500 block text-[11px] uppercase tracking-wider">
            Alternatives Accepted
          </span>
          <span className="text-slate-800 font-medium line-clamp-2">
            {req.alternative_documents && req.alternative_documents.length > 0
              ? req.alternative_documents.join(', ')
              : 'Official certificate required (No alternatives permitted)'}
          </span>
        </div>

        {/* Validity & Expiry Rules */}
        <div>
          <span className="font-bold text-slate-500 block text-[11px] uppercase tracking-wider">
            Validity & Expiry Rules
          </span>
          <span className="text-slate-800 font-medium line-clamp-2">
            {req.validity_rules || 'Permanent validity or as certified by issuing authority'}
          </span>
        </div>

        {/* Accepted Formats */}
        <div>
          <span className="font-bold text-slate-500 block text-[11px] uppercase tracking-wider">
            Accepted Formats
          </span>
          <span className="text-slate-800 font-medium">
            {req.accepted_formats || 'PDF, JPG, JPEG, PNG (Max 5MB)'}
          </span>
        </div>

        {/* Official Source Link */}
        <div>
          <span className="font-bold text-slate-500 block text-[11px] uppercase tracking-wider">
            Official Issuing Authority
          </span>
          {req.official_source_url ? (
            <a
              href={req.official_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#0f2942] hover:text-[#ea580c] font-bold inline-flex items-center space-x-1 underline decoration-slate-300"
            >
              <span className="truncate max-w-[140px]">{req.official_source_url.replace(/^https?:\/\//, '')}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
            </a>
          ) : (
            <span className="text-slate-500">Authorized e-District / e-Sevai</span>
          )}
        </div>
      </div>

      {/* Card Body: Empty vs Uploaded */}
      <div className="p-5">
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {!isUploaded ? (
          /* Empty Slot: Upload Button & Guidance */
          <div className="border-2 border-dashed border-slate-200 hover:border-[#0f2942] rounded-xl p-6 text-center transition bg-slate-50/50 hover:bg-slate-50 group">
            <div className="w-12 h-12 rounded-2xl bg-white shadow-sm border border-slate-200 flex items-center justify-center mx-auto mb-3 group-hover:scale-105 transition">
              <Upload className="w-6 h-6 text-[#0f2942]" />
            </div>
            <h4 className="text-sm font-black text-slate-800 mb-1">
              Upload Document for {req.display_name}
            </h4>
            <p className="text-xs text-slate-500 max-w-md mx-auto mb-4">
              Select your scanned PDF or clean photographic image. Sensitive document identifiers will be encrypted at rest and masked.
            </p>
            <button
              onClick={handleTriggerUpload}
              disabled={isUploading}
              className="inline-flex items-center space-x-2 px-5 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white text-xs font-bold rounded-xl shadow-sm transition disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-orange-400" />
                  <span>Processing Upload & OCR...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 text-white" />
                  <span>Choose File to Upload</span>
                </>
              )}
            </button>
          </div>
        ) : (
          /* Uploaded Slot: Full Scorecard & Controls */
          <div className="space-y-4">
            {/* File Header Row */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-[#0f2942]" />
                </div>
                <div>
                  <h4 className="text-sm font-black text-slate-900 truncate max-w-xs md:max-w-md">
                    {doc.original_filename}
                  </h4>
                  <p className="text-xs text-slate-500">
                    {formatFileSize(doc.file_size_bytes)} &bull; Uploaded {new Date(doc.created_at).toLocaleDateString()} &bull;
                    <span className="text-emerald-700 font-semibold ml-1">🔒 AES-256 Encrypted</span>
                  </p>
                </div>
              </div>

              {/* Action Buttons: Replace & Remove */}
              <div className="flex items-center space-x-2 self-start sm:self-center">
                <button
                  onClick={handleTriggerUpload}
                  disabled={isUploading}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 text-xs font-bold text-slate-700 transition disabled:opacity-50"
                  title="Replace with a renewed or higher-quality document"
                >
                  <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${isUploading ? 'animate-spin' : ''}`} />
                  <span>Replace</span>
                </button>

                <button
                  onClick={handleRemove}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-xs font-bold text-rose-700 transition"
                  title="Remove this document from slot"
                >
                  <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                  <span>Remove</span>
                </button>

                <button
                  onClick={handleViewAudit}
                  disabled={loadingAudit}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 text-xs font-bold text-indigo-700 transition"
                  title="View complete 6-dimension forensic audit"
                >
                  {loadingAudit ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                  ) : (
                    <Eye className="w-3.5 h-3.5 text-indigo-600" />
                  )}
                  <span>View Full Audit</span>
                </button>
              </div>
            </div>

            {/* 6 Verification Status Pills */}
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                Automated Verification Dimensions
              </span>
              <div className="flex flex-wrap gap-2">
                {/* 1. Type Detection */}
                {renderDimensionPill(dims.type_detection, 'Type', 'status', 'identified_type')}

                {/* 2. Required Fields */}
                {renderDimensionPill(dims.fields_extraction, 'Fields', 'status', 'note')}

                {/* 3. Expiry Check */}
                {renderDimensionPill(dims.validity_expiry, 'Expiry', 'status', 'label')}

                {/* 4. Readability & Quality */}
                {renderDimensionPill(dims.readability_quality, 'Quality', 'status', 'label')}

                {/* 5. Document Authenticity Screening strictly showing one of 3 outcomes */}
                <div className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-semibold ${authPillClass}`}>
                  {authIcon}
                  <span className="font-bold text-slate-600">Authenticity:</span>
                  <span>{authenticityResult}</span>
                </div>

                {/* 6. Official Verification Readiness */}
                {renderDimensionPill(dims.official_readiness, 'Official Readiness', 'status', 'label')}
              </div>
            </div>

            {/* Extracted Document Details (Sensitive Details Masked) */}
            {dims.fields_extraction?.masked_fields && Object.keys(dims.fields_extraction.masked_fields).length > 0 && (
              <div className="bg-slate-50/70 rounded-xl border border-slate-200 p-3">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                  Extracted Document Details (Privacy Masked)
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                  {Object.entries(dims.fields_extraction.masked_fields).map(([k, v]) => (
                    <div key={k} className="bg-white p-2 rounded-lg border border-slate-200/80">
                      <span className="text-[10px] text-slate-500 font-bold uppercase block truncate">
                        {k.replace(/_/g, ' ')}
                      </span>
                      <span className="font-mono font-bold text-slate-900 truncate block">
                        {v}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detected Issues & Plain-Language Guidance */}
            {evaluation?.detected_issues && evaluation.detected_issues.length > 0 && (
              <div className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200 text-xs">
                <div className="flex items-center space-x-1.5 text-amber-900 font-bold mb-1">
                  <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                  <span>Detected Issues & Discrepancies</span>
                </div>
                <ul className="list-disc list-inside text-amber-800 space-y-0.5 ml-1">
                  {evaluation.detected_issues.map((iss, i) => (
                    <li key={i}>{iss}</li>
                  ))}
                </ul>

                {evaluation?.suggested_corrections && evaluation.suggested_corrections.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-amber-200 text-amber-900">
                    <span className="font-bold">Correction Guidance:</span>
                    <ul className="list-disc list-inside space-y-0.5 ml-1 mt-0.5 text-amber-800">
                      {evaluation.suggested_corrections.map((corr, i) => (
                        <li key={i}>{corr}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Forensic Audit Scorecard Modal */}
      <ForensicAuditModal
        isOpen={auditModalOpen}
        onClose={() => setAuditModalOpen(false)}
        auditData={auditData}
      />
    </div>
  );
};

export default DocumentSlotCard;
