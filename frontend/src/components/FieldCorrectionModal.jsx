import React, { useState } from 'react';
import { X, Check, Edit3, AlertCircle } from 'lucide-react';
import { documentsApi } from '../services/api';

const FieldCorrectionModal = ({ isOpen, onClose, documentId, field, onFieldUpdated }) => {
  if (!isOpen || !field) return null;

  const [value, setValue] = useState(field.corrected_value || field.effective_value || '');
  const [notes, setNotes] = useState(field.notes || '');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!value.trim()) {
      setError('Value cannot be empty');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const updatedDoc = await documentsApi.correctField(
        documentId,
        field.field_key,
        value.trim(),
        notes.trim()
      );
      onFieldUpdated(updatedDoc);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update field correction');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden border border-slate-200">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Edit3 className="w-5 h-5 text-brand-600" />
            <h3 className="font-bold text-slate-900 text-base">Correct OCR Extraction</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
              Field Type
            </label>
            <div className="text-sm font-semibold text-slate-800 bg-slate-100 px-3 py-2 rounded-lg">
              {field.field_key}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
              Raw Extracted OCR
            </label>
            <div className="text-xs font-mono bg-slate-50 text-slate-600 p-2.5 rounded-lg border border-slate-200 break-all">
              {field.raw_value || '<None detected>'}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Correct Legal Value <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 focus:outline-none"
              placeholder="Enter true verified value"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
              Notes / Justification
            </label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-brand-500 focus:outline-none"
              placeholder="e.g., OCR misread numeral 0 as letter O"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg text-sm hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Check className="w-4 h-4" />
              <span>{submitting ? 'Saving...' : 'Save Correction'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FieldCorrectionModal;
