import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

const ExpiryBadge = ({ status, daysRemaining, expiryDate }) => {
  switch (status) {
    case 'VALID':
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-500" />
          Valid {daysRemaining ? `(${daysRemaining}d left)` : ''}
        </span>
      );
    case 'EXPIRING_SOON':
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">
          <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-500" />
          Expiring Soon ({daysRemaining} days left)
        </span>
      );
    case 'EXPIRED':
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
          <XCircle className="w-3.5 h-3.5 mr-1 text-rose-500" />
          EXPIRED {expiryDate ? `(${expiryDate})` : ''}
        </span>
      );
    case 'MANUAL_VERIFICATION_REQUIRED':
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
          <AlertTriangle className="w-3.5 h-3.5 mr-1 text-purple-500" />
          Manual Review Req.
        </span>
      );
    case 'EXPIRY_DATE_NOT_FOUND':
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
          <HelpCircle className="w-3.5 h-3.5 mr-1 text-slate-400" />
          No Expiry Date
        </span>
      );
  }
};

export default ExpiryBadge;
