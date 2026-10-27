import axios from 'axios';

// Use explicit IPv127.0.0.1 to avoid Windows IPv6 localhost resolution mismatch
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization Bearer token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('docverify_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to catch 401 unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If unauthorized on general endpoints, clean up and redirect
      if (!error.config.url.includes('/auth/login')) {
        localStorage.removeItem('docverify_token');
        localStorage.removeItem('docverify_user');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (email, password) => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },
  register: async (fullName, email, password, role = 'USER') => {
    const res = await apiClient.post('/auth/register', {
      full_name: fullName,
      email,
      password,
      role,
    });
    return res.data;
  },
  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
};

export const applicationsApi = {
  getProfiles: async () => {
    const res = await apiClient.get('/applications/profiles');
    return res.data;
  },
  startApplication: async (profileId, consentGiven = true, state = 'Tamil Nadu', district = 'Chennai', issuingAuthority = null) => {
    const res = await apiClient.post('/applications/start', {
      application_profile_id: profileId,
      consent_given: consentGiven,
      state,
      district,
      issuing_authority: issuingAuthority,
    });
    return res.data;
  },
  getMyApplications: async () => {
    const res = await apiClient.get('/applications/my');
    return res.data;
  },
  getApplication: async (applicationId) => {
    const res = await apiClient.get(`/applications/${applicationId}`);
    return res.data;
  },
  deleteApplication: async (applicationId) => {
    const res = await apiClient.delete(`/applications/${applicationId}`);
    return res.data;
  },
  getDemoScenarios: async () => {
    const res = await apiClient.get('/applications/demo/scenarios');
    return res.data;
  },
  loadDemoScenario: async (scenarioId) => {
    const res = await apiClient.post(`/applications/demo/load/${scenarioId}`);
    return res.data;
  },
  getSampleFileUrl: (docKey) => {
    return `${API_BASE_URL}/applications/demo/sample-file/${docKey}`;
  },
  getOfficialServices: async (category = null, jurisdiction = null) => {
    const params = {};
    if (category) params.category = category;
    if (jurisdiction) params.jurisdiction = jurisdiction;
    const res = await apiClient.get('/applications/official-services/list', { params });
    return res.data;
  },
  getCorrectionGuides: async () => {
    const res = await apiClient.get('/applications/correction-guides/list');
    return res.data;
  },
  getCorrectionGuide: async (guideId) => {
    const res = await apiClient.get(`/applications/correction-guides/${guideId}`);
    return res.data;
  },
  getApplicationSlots: async (applicationId) => {
    const res = await apiClient.get(`/applications/${applicationId}/slots`);
    return res.data;
  },
};

export const documentsApi = {
  uploadDocuments: async (applicationId, files, claimedCategory = null) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    if (claimedCategory) {
      formData.append('claimed_category', claimedCategory);
    }
    const res = await apiClient.post(`/documents/upload/${applicationId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  uploadSlotDocument: async (applicationId, requirementId, file, claimedCategory = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (claimedCategory) {
      formData.append('claimed_category', claimedCategory);
    }
    const res = await apiClient.post(`/documents/upload-slot/${applicationId}/${requirementId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  getDocumentAudit: async (documentId) => {
    const res = await apiClient.get(`/documents/${documentId}/audit`);
    return res.data;
  },
  getApplicationDocuments: async (applicationId) => {
    const res = await apiClient.get(`/documents/application/${applicationId}`);
    return res.data;
  },
  correctField: async (documentId, fieldKey, correctedValue, notes = '') => {
    const res = await apiClient.put(`/documents/${documentId}/fields`, {
      field_key: fieldKey,
      corrected_value: correctedValue,
      notes,
    });
    return res.data;
  },
  deleteDocument: async (documentId) => {
    const res = await apiClient.delete(`/documents/${documentId}`);
    return res.data;
  },
  downloadDocumentUrl: (documentId) => {
    const token = localStorage.getItem('docverify_token');
    return `${API_BASE_URL}/documents/${documentId}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
  downloadDocumentBlob: async (documentId, filename = 'document.pdf') => {
    const response = await apiClient.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    return true;
  },
};

export const verificationApi = {
  runVerification: async (applicationId) => {
    const res = await apiClient.post(`/verify/run/${applicationId}`);
    return res.data;
  },
  recheckDocuments: async (applicationId) => {
    const res = await apiClient.post(`/verify/recheck/${applicationId}`);
    return res.data;
  },
  getApplicationConfidence: async (applicationId) => {
    const res = await apiClient.get(`/verify/confidence/${applicationId}`);
    return res.data;
  },
  getDocumentConfidence: async (documentId) => {
    const res = await apiClient.get(`/verify/confidence/document/${documentId}`);
    return res.data;
  },
  getVerificationResult: async (applicationId) => {
    const res = await apiClient.get(`/verify/${applicationId}`);
    return res.data;
  },
  downloadReportUrl: (applicationId) => {
    const token = localStorage.getItem('docverify_token');
    return `${API_BASE_URL}/reports/${applicationId}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
  downloadReportBlob: async (applicationId, referenceNumber = 'Audit') => {
    const response = await apiClient.get(`/reports/${applicationId}/download`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `DocVerify_Report_${referenceNumber}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    return true;
  },
};

export const adminApi = {
  listApplications: async (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const res = await apiClient.get('/admin/applications', { params });
    return res.data;
  },
  submitReview: async (applicationId, newStatus, reviewNotes) => {
    const res = await apiClient.post(`/admin/review/${applicationId}`, {
      new_status: newStatus,
      review_notes: reviewNotes,
    });
    return res.data;
  },
  createProfile: async (profilePayload) => {
    const res = await apiClient.post('/admin/profiles', profilePayload);
    return res.data;
  },
  getRequirements: async (filters = {}) => {
    const res = await apiClient.get('/admin/requirements', { params: filters });
    return res.data;
  },
  createRequirement: async (payload) => {
    const res = await apiClient.post('/admin/requirements', payload);
    return res.data;
  },
  updateRequirement: async (requirementId, payload) => {
    const res = await apiClient.put(`/admin/requirements/${requirementId}`, payload);
    return res.data;
  },
  deleteRequirement: async (requirementId) => {
    const res = await apiClient.delete(`/admin/requirements/${requirementId}`);
    return res.data;
  },
  verifyRequirement: async (requirementId) => {
    const res = await apiClient.post(`/admin/requirements/${requirementId}/verify`);
    return res.data;
  },
  syncDefaultRequirements: async () => {
    const res = await apiClient.post('/admin/requirements/sync-defaults');
    return res.data;
  },
};

export const ruleRadarApi = {
  getUpdates: async (filters = {}) => {
    const res = await apiClient.get('/rule-radar/updates', { params: filters });
    return res.data;
  },
  getNotifications: async () => {
    const res = await apiClient.get('/rule-radar/notifications');
    return res.data;
  },
  compareRequirements: async (profileCode) => {
    const res = await apiClient.get(`/rule-radar/compare/${profileCode}`);
    return res.data;
  },
  getUpdateDetails: async (updateId) => {
    const res = await apiClient.get(`/rule-radar/updates/${updateId}`);
    return res.data;
  },
  adminCreateUpdate: async (payload) => {
    const res = await apiClient.post('/rule-radar/admin/create-update', payload);
    return res.data;
  },
  adminVerifyUpdate: async (updateId) => {
    const res = await apiClient.patch(`/rule-radar/admin/verify/${updateId}`);
    return res.data;
  },
};

export const timelineApi = {
  getRecords: async (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const res = await apiClient.get('/timeline/records', { params });
    return res.data;
  },
  updateDates: async (documentId, issueDate, expiryDate) => {
    const res = await apiClient.post(`/timeline/update-dates/${documentId}`, {
      issue_date: issueDate,
      expiry_date: expiryDate,
    });
    return res.data;
  },
  setReminder: async (recordId, reminderDays, isEnabled = true) => {
    const res = await apiClient.patch(`/timeline/reminder/${recordId}`, {
      reminder_days: reminderDays,
      is_enabled: isEnabled,
    });
    return res.data;
  },
  uploadRenewedDocument: async (documentId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post(`/timeline/renew/${documentId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  getAffectedApplications: async (documentId) => {
    const res = await apiClient.get(`/timeline/affected-applications/${documentId}`);
    return res.data;
  },
};

export default apiClient;
