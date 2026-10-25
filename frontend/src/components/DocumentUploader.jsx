import React, { useState, useRef } from 'react';
import { UploadCloud, File, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { documentsApi } from '../services/api';

const ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png'];
const MAX_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

const DocumentUploader = ({ applicationId, onUploadComplete }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [claimedCategory, setClaimedCategory] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const validateFiles = (fileList) => {
    setError('');
    const valid = [];
    for (const f of fileList) {
      const ext = '.' + f.name.split('.').pop().toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        setError(`File "${f.name}" has an unsupported format. Allowed: PDF, JPG, PNG.`);
        return [];
      }
      if (f.size > MAX_SIZE_BYTES) {
        setError(`File "${f.name}" exceeds 15MB size limit.`);
        return [];
      }
      valid.push(f);
    }
    return valid;
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const valid = validateFiles(Array.from(e.target.files));
      if (valid.length > 0) {
        setSelectedFiles((prev) => [...prev, ...valid]);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const valid = validateFiles(Array.from(e.dataTransfer.files));
      if (valid.length > 0) {
        setSelectedFiles((prev) => [...prev, ...valid]);
      }
    }
  };

  const removeFile = (idx) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    setIsUploading(true);
    setError('');
    try {
      const docs = await documentsApi.uploadDocuments(
        applicationId,
        selectedFiles,
        claimedCategory || null
      );
      setSelectedFiles([]);
      setClaimedCategory('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      onUploadComplete(docs);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please check files and retry.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-bold text-slate-900">Secure Document Ingestion</h3>
          <p className="text-xs text-slate-500">
            Files are verified, encrypted at rest using AES-256, and analyzed via OCR.
          </p>
        </div>
        <div className="w-full sm:w-64">
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Optional Category Hint
          </label>
          <select
            value={claimedCategory}
            onChange={(e) => setClaimedCategory(e.target.value)}
            className="w-full text-xs px-2.5 py-1.5 border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-500 focus:outline-none bg-white font-medium"
          >
            <option value="">Auto-Detect via AI (Recommended)</option>
            <option value="AADHAAR">Aadhaar Card (UIDAI)</option>
            <option value="PAN_CARD">PAN Card (Income Tax)</option>
            <option value="RATION_CARD">Smart Family Card / Ration Card</option>
            <option value="NATIVITY_CERTIFICATE">Nativity Certificate (e-Sevai)</option>
            <option value="COMMUNITY_CERTIFICATE">Community / Caste Certificate</option>
            <option value="INCOME_CERTIFICATE">Income Certificate (Tahsildar)</option>
            <option value="FIRST_GRADUATE_CERTIFICATE">First Graduate Certificate</option>
            <option value="EDUCATIONAL_CERTIFICATE">10th / 12th HSC Mark Sheet / Degree</option>
            <option value="TRANSFER_CERTIFICATE">School / College Transfer Certificate (TC)</option>
            <option value="DRIVING_LICENSE">Driving Licence (Parivahan / RTO)</option>
            <option value="VOTER_ID">Voter ID / EPIC Card</option>
            <option value="BIRTH_CERTIFICATE">Birth Certificate (DOB)</option>
            <option value="BANK_PASSBOOK">Bank Passbook / Account Proof</option>
            <option value="BONAFIDE_CERTIFICATE">Bonafide Student Certificate</option>
            <option value="DISABILITY_CERTIFICATE">Disability Certificate (UDID)</option>
            <option value="PASSPORT">Passport (Republic of India)</option>
            <option value="APPLICATION_FORM">Application Form / Declaration</option>
            <option value="OTHER_SUPPORTING">Other Supporting Document</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Drag & Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition ${
          dragActive
            ? 'border-brand-500 bg-brand-50/50'
            : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileChange}
          className="hidden"
        />
        <UploadCloud className="w-10 h-10 text-slate-400 mx-auto mb-2" />
        <p className="text-sm font-semibold text-slate-800">
          Click to upload or drag & drop files here
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Supports PDF, JPG, JPEG, PNG (Up to 15MB each)
        </p>
      </div>

      {/* Selected File Previews */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2 pt-2">
          <div className="text-xs font-bold text-slate-600 uppercase tracking-wider">
            Ready to Process ({selectedFiles.length})
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {selectedFiles.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-lg bg-slate-100/70 border border-slate-200 text-xs"
              >
                <div className="flex items-center space-x-2 truncate">
                  <File className="w-4 h-4 text-brand-600 flex-shrink-0" />
                  <span className="truncate font-medium text-slate-800">{file.name}</span>
                  <span className="text-slate-400 text-[10px]">
                    ({(file.size / 1024).toFixed(0)} KB)
                  </span>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}
                  className="text-slate-400 hover:text-rose-600 p-1"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="px-5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-sm transition flex items-center space-x-2 disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing OCR & Validation...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Upload & Run OCR ({selectedFiles.length})</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUploader;
