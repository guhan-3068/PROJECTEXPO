import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles, CheckCircle2, ChevronRight, ChevronLeft, ArrowRight,
  Upload, FileText, AlertCircle, RefreshCw, Download, Shield,
  GraduationCap, Car, Award, Landmark, Building2, Briefcase, CreditCard,
  BookOpen, HelpCircle, Eye, ShieldCheck, MapPin, Building
} from 'lucide-react';
import { applicationsApi, documentsApi, verificationApi } from '../services/api';
import ReadinessBadge from '../components/ReadinessBadge';
import ActionPlanChecklist from '../components/ActionPlanChecklist';

const CATEGORY_ICONS = {
  FIRST_GRADUATE_APPLICATION: GraduationCap,
  COLLEGE_ADMISSION: GraduationCap,
  SCHOOL_ADMISSION: BookOpen,
  DRIVING_LICENSE_APPLICATION: Car,
  SCHOLARSHIP_APPLICATION: Award,
  GOVERNMENT_CERTIFICATE_APPLICATION: Landmark,
  INCOME_CERTIFICATE_APPLICATION: Landmark,
  NATIVITY_CERTIFICATE_APPLICATION: Landmark,
  PAN_CARD_APPLICATION: CreditCard,
  AADHAAR_SERVICES: Shield,
  NGO_REGISTRATION: Building2,
  JOB_APPLICATION: Briefcase,
  BANK_ACCOUNT_OPENING: CreditCard,
  OTHER_APPLICATIONS: FileText,
};

const TN_DISTRICTS = [
  'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli',
  'Erode', 'Vellore', 'Thanjavur', 'Dindigul', 'Kanchipuram', 'Tiruvallur',
  'Cuddalore', 'Villupuram', 'Kanyakumari', 'Namakkal', 'Karur', 'Thoothukudi',
  'Sivaganga', 'Virudhunagar', 'Tenkasi', 'Ramanathapuram', 'Theni', 'Krishnagiri',
  'Dharmapuri', 'Tiruppur', 'Nilgiris', 'Nagapattinam', 'Tiruvarur', 'Pudukkottai',
  'Perambalur', 'Ariyalur', 'Tirupathur', 'Ranipet', 'Chengalpattu', 'Kallakurichi',
  'Mayiladuthurai'
];

const STATES = [
  'Tamil Nadu', 'Central / All India', 'Karnataka', 'Maharashtra',
  'Andhra Pradesh', 'Telangana', 'Kerala', 'Uttar Pradesh', 'Delhi'
];

const CHECK_ITEMS = [
  'Checking correct document category classification...',
  'Extracting required fields & identifying missing values...',
  'Evaluating readability, image resolution & scan quality...',
  'Checking expiry date & validity periods (Lifetime vs Time-limited)...',
  'Analyzing name spelling consistency across documents...',
  'Verifying Date of Birth (DOB) and address alignment...',
  'Confirming mandatory vs conditionally required supporting documents...',
  'Screening for certificate reference numbers, seals, and signatures...',
  'Generating prioritized action plan and readiness score...'
];

const PreCheckWizardPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1); // 1 to 6
  const [profiles, setProfiles] = useState([]);
  const [loadingProfiles, setLoadingProfiles] = useState(true);

  // Step 1: Category Selection
  const [selectedProfileId, setSelectedProfileId] = useState('');
  const [selectedProfile, setSelectedProfile] = useState(null);

  // Step 2: State, District, Authority
  const [selectedState, setSelectedState] = useState('Tamil Nadu');
  const [selectedDistrict, setSelectedDistrict] = useState('Chennai');
  const [issuingAuthority, setIssuingAuthority] = useState('');

  // Step 3: Application instance & Checklist
  const [application, setApplication] = useState(null);
  const [creatingApp, setCreatingApp] = useState(false);

  // Step 4: Documents Upload
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedClaimedCategory, setSelectedClaimedCategory] = useState('');

  // Step 5: Inspection in progress
  const [evaluating, setEvaluating] = useState(false);
  const [evalProgress, setEvalProgress] = useState(0);
  const [activeCheckText, setActiveCheckText] = useState(CHECK_ITEMS[0]);

  // Step 6: Readiness Report
  const [verificationResult, setVerificationResult] = useState(null);
  const [isRechecking, setIsRechecking] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    setLoadingProfiles(true);
    try {
      const data = await applicationsApi.getProfiles();
      setProfiles(data);
      if (data.length > 0) {
        setSelectedProfileId(data[0].id);
        setSelectedProfile(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingProfiles(false);
    }
  };

  const handleSelectProfile = (profile) => {
    setSelectedProfileId(profile.id);
    setSelectedProfile(profile);
    setIssuingAuthority(profile.jurisdiction || 'State Government / Tahsildar');
  };

  // Step 2 -> Step 3: Create Application in DB
  const handleProceedToStep3 = async () => {
    setCreatingApp(true);
    setErrorMsg('');
    try {
      const newApp = await applicationsApi.startApplication(
        selectedProfileId,
        true,
        selectedState,
        selectedDistrict,
        issuingAuthority || selectedProfile?.jurisdiction
      );
      setApplication(newApp);
      setCurrentStep(3);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to initialize pre-check session');
    } finally {
      setCreatingApp(false);
    }
  };

  // Step 4: Upload file
  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length || !application) return;

    setUploading(true);
    setErrorMsg('');
    try {
      const addedDocs = await documentsApi.uploadDocuments(
        application.id,
        files,
        selectedClaimedCategory || null
      );
      setUploadedFiles((prev) => [...prev, ...addedDocs]);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'File upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  // Step 4: Load safe demo documents
  const handleUseDemoDocs = async () => {
    setUploading(true);
    setErrorMsg('');
    try {
      // Find matching demo scenario or default to complete_application
      const newApp = await applicationsApi.loadDemoScenario('complete_application');
      setApplication(newApp);
      setUploadedFiles(newApp.documents || []);
      setCurrentStep(5);
      triggerInspection(newApp.id);
    } catch (err) {
      setErrorMsg('Failed to load demo scenario documents');
    } finally {
      setUploading(false);
    }
  };

  // Step 5: Automated Readiness Inspection
  const triggerInspection = async (appId) => {
    setEvaluating(true);
    setEvalProgress(10);

    // Run automated step animation
    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex += 1;
      if (stepIndex < CHECK_ITEMS.length) {
        setActiveCheckText(CHECK_ITEMS[stepIndex]);
        setEvalProgress(Math.min(90, Math.round(((stepIndex + 1) / CHECK_ITEMS.length) * 100)));
      } else {
        clearInterval(interval);
      }
    }, 280);

    try {
      const res = await verificationApi.runVerification(appId);
      clearInterval(interval);
      setEvalProgress(100);
      setVerificationResult(res);
      setTimeout(() => {
        setEvaluating(false);
        setCurrentStep(6);
      }, 500);
    } catch (err) {
      clearInterval(interval);
      setEvaluating(false);
      setErrorMsg(err.response?.data?.detail || 'Readiness evaluation encounter an issue.');
    }
  };

  // Step 6: Recheck Documents
  const handleRecheck = async () => {
    if (!application) return;
    setIsRechecking(true);
    try {
      const res = await verificationApi.recheckDocuments(application.id);
      setVerificationResult(res);
    } catch (err) {
      alert('Unable to recheck documents. Please verify uploaded files.');
    } finally {
      setIsRechecking(false);
    }
  };

  // Step 6: Download PDF Report
  const handleDownloadPdf = async () => {
    if (!application) return;
    setIsDownloadingPdf(true);
    try {
      await verificationApi.downloadReportBlob(application.id, application.reference_number);
    } catch (err) {
      alert('Failed to download report PDF.');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Breadcrumb & Step Progress Bar */}
      <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="inline-flex items-center space-x-2 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-[#ea580c]" />
              <span>Smart Pre-Application Readiness Engine</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-[#0f2942]">
              Check Everything Before Applying
            </h1>
          </div>

          <div className="flex items-center space-x-2 text-xs font-bold text-slate-600 bg-slate-100 px-3.5 py-1.5 rounded-full self-start sm:self-auto">
            <span>Step {currentStep} of 6</span>
          </div>
        </div>

        {/* Stepper Wizard Bar */}
        <div className="grid grid-cols-6 gap-2 pt-2 border-t border-slate-100">
          {[
            { num: 1, label: '1. Choose Service' },
            { num: 2, label: '2. State & Authority' },
            { num: 3, label: '3. Checklist' },
            { num: 4, label: '4. Upload / Demo' },
            { num: 5, label: '5. Inspection' },
            { num: 6, label: '6. Readiness Report' }
          ].map((s) => (
            <div key={s.num} className="space-y-1">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  currentStep >= s.num ? 'bg-[#0f2942]' : 'bg-slate-200'
                }`}
              />
              <span
                className={`hidden md:block text-[10px] font-bold truncate ${
                  currentStep === s.num ? 'text-[#ea580c]' : 'text-slate-400'
                }`}
              >
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Error notification */}
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* ======================================================== */}
      {/* STEP 1: SELECT APPLICATION CATEGORY                     */}
      {/* ======================================================== */}
      {currentStep === 1 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-1">
            <h2 className="text-base font-extrabold text-[#0f2942]">
              Step 1: Select What You Are Applying For
            </h2>
            <p className="text-xs text-slate-500">
              Choose your scheme or certificate category to load its specific government requirements.
            </p>
          </div>

          {loadingProfiles ? (
            <div className="py-12 text-center text-xs text-slate-400">
              Loading service categories...
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {profiles.map((p) => {
                const IconComponent = CATEGORY_ICONS[p.code] || FileText;
                const isSelected = selectedProfileId === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => handleSelectProfile(p)}
                    className={`p-5 rounded-2xl border cursor-pointer transition flex flex-col justify-between space-y-3 ${
                      isSelected
                        ? 'border-[#0f2942] bg-blue-50/40 ring-2 ring-[#0f2942] shadow-sm'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className={`p-2.5 rounded-xl ${isSelected ? 'bg-[#0f2942] text-white' : 'bg-slate-100 text-slate-700'}`}>
                          <IconComponent className="w-5 h-5" />
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                          {p.jurisdiction}
                        </span>
                      </div>
                      <h3 className="font-extrabold text-sm text-slate-900">
                        {p.name}
                      </h3>
                      <p className="text-xs text-slate-500 line-clamp-2">
                        {p.description}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                      <span className="text-[11px] font-semibold text-slate-500">
                        {p.requirements?.length || 0} Required Docs
                      </span>
                      <span className={`font-bold ${isSelected ? 'text-[#0f2942]' : 'text-slate-400'}`}>
                        {isSelected ? '✓ Selected' : 'Select'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="flex justify-end pt-4">
            <button
              onClick={() => setCurrentStep(2)}
              disabled={!selectedProfileId}
              className="px-6 py-3 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl font-bold text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm disabled:opacity-50"
            >
              <span>Next: State & Authority</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* STEP 2: STATE, DISTRICT & ISSUING AUTHORITY            */}
      {/* ======================================================== */}
      {currentStep === 2 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-1">
            <h2 className="text-base font-extrabold text-[#0f2942]">
              Step 2: Select State, District & Issuing Authority
            </h2>
            <p className="text-xs text-slate-500">
              Government certificate rules and verification authorities vary by state and district.
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-6 max-w-2xl">
            {/* Selected Service Card */}
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-[#0f2942] text-white">
                <Sparkles className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Selected Application
                </span>
                <h3 className="font-extrabold text-sm text-slate-900">
                  {selectedProfile?.name}
                </h3>
              </div>
            </div>

            {/* State Selection */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5 text-brand-600" />
                <span>Applicable State / Jurisdiction</span>
              </label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
              >
                {STATES.map((st) => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </div>

            {/* District Selection */}
            {selectedState === 'Tamil Nadu' ? (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
                  <Building className="w-3.5 h-3.5 text-brand-600" />
                  <span>District in Tamil Nadu</span>
                </label>
                <select
                  value={selectedDistrict}
                  onChange={(e) => setSelectedDistrict(e.target.value)}
                  className="w-full text-xs px-3.5 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                >
                  {TN_DISTRICTS.map((dst) => (
                    <option key={dst} value={dst}>{dst}</option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700">
                  District Name
                </label>
                <input
                  type="text"
                  value={selectedDistrict}
                  onChange={(e) => setSelectedDistrict(e.target.value)}
                  placeholder="Enter your district name..."
                  className="w-full text-xs px-3.5 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
                />
              </div>
            )}

            {/* Issuing Authority */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">
                Designated Issuing Authority
              </label>
              <input
                type="text"
                value={issuingAuthority}
                onChange={(e) => setIssuingAuthority(e.target.value)}
                placeholder="e.g., Tahsildar / Revenue Department, RTO, Anna University DoTE"
                className="w-full text-xs px-3.5 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
              />
              <span className="text-[11px] text-slate-400">
                The office or department where this final application will be submitted.
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4">
            <button
              onClick={() => setCurrentStep(1)}
              className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center space-x-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={handleProceedToStep3}
              disabled={creatingApp}
              className="px-6 py-3 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl font-bold text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm disabled:opacity-50"
            >
              <span>{creatingApp ? 'Preparing Checklist...' : 'View Applicable Checklist'}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* STEP 3: APPLICABLE DOCUMENT CHECKLIST                   */}
      {/* ======================================================== */}
      {currentStep === 3 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-extrabold text-[#0f2942]">
                  Step 3: Documents You Need Before Applying
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Applicable for <strong>{selectedProfile?.name}</strong> in {selectedDistrict}, {selectedState}.
                </p>
              </div>
              <span className="text-xs font-mono font-bold bg-slate-100 px-3 py-1 rounded-full text-slate-700 self-start sm:self-auto">
                Ref: {application?.reference_number}
              </span>
            </div>
          </div>

          {/* Checklist breakdown */}
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200 divide-y divide-slate-100">
            {(selectedProfile?.requirements || []).map((req, i) => {
              const reqType = req.requirement_type || (req.is_mandatory ? 'REQUIRED' : 'OPTIONAL');
              let badgeColor = 'bg-rose-50 text-rose-800 border-rose-200';
              if (reqType === 'CONDITIONALLY_REQUIRED') {
                badgeColor = 'bg-blue-50 text-blue-800 border-blue-200';
              } else if (reqType === 'OPTIONAL') {
                badgeColor = 'bg-slate-100 text-slate-600 border-slate-200';
              }

              return (
                <div key={i} className="py-4 space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-bold flex items-center justify-center">
                      {i + 1}
                    </span>
                    <h3 className="font-extrabold text-sm text-slate-900">
                      {req.display_name}
                    </h3>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}>
                      {reqType.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 pl-7 leading-relaxed">
                    {req.description}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-between pt-4">
            <button
              onClick={() => setCurrentStep(2)}
              className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center space-x-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={() => setCurrentStep(4)}
              className="px-6 py-3 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl font-bold text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm"
            >
              <span>Next: Upload Documents</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* STEP 4: UPLOAD DOCUMENTS OR USE DEMO                   */}
      {/* ======================================================== */}
      {currentStep === 4 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-1">
            <h2 className="text-base font-extrabold text-[#0f2942]">
              Step 4: Upload Your Documents or Test with Safe Demo Files
            </h2>
            <p className="text-xs text-slate-500">
              Upload PDF or clear photo scans of your certificates. You can also test drive with 100% synthetic demo records.
            </p>
          </div>

          {/* Upload Area */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-6">
            <div className="border-2 border-dashed border-slate-300 rounded-2xl p-8 text-center space-y-3 bg-slate-50/50 hover:bg-slate-50 transition">
              <div className="w-12 h-12 mx-auto rounded-2xl bg-blue-100 text-[#0f2942] flex items-center justify-center font-bold">
                <Upload className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="font-extrabold text-sm text-slate-900">
                  Select certificate files from your device
                </h3>
                <p className="text-xs text-slate-500">
                  Supports PDF, JPG, JPEG, and PNG files up to 10 MB per document.
                </p>
              </div>

              <div className="pt-2 flex justify-center">
                <label className="cursor-pointer px-5 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition shadow-sm">
                  <span>Browse & Upload Files</span>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Uploaded Files Count */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700">
                  Uploaded Documents ({uploadedFiles.length}):
                </h4>
                <div className="divide-y divide-slate-100 border border-slate-200 rounded-2xl overflow-hidden bg-slate-50">
                  {uploadedFiles.map((f, i) => (
                    <div key={i} className="p-3 flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span className="font-semibold text-slate-800">{f.original_filename || f.name}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {f.doc_category || 'Attached'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Or Use Safe Demo Documents */}
            <div className="p-5 rounded-2xl bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-orange-700 uppercase tracking-wider">
                  Testing Without Personal Files
                </span>
                <h4 className="font-extrabold text-xs sm:text-sm text-[#0f2942]">
                  Don't have your certificates handy right now?
                </h4>
                <p className="text-xs text-slate-600">
                  Use pre-generated synthetic demo documents (Aadhaar, Smart Family Card, 12th Marksheet, TC) to test drive the entire readiness inspection.
                </p>
              </div>

              <button
                onClick={handleUseDemoDocs}
                disabled={uploading}
                className="px-4 py-2.5 bg-[#ea580c] hover:bg-[#c2410c] text-white rounded-xl text-xs font-bold transition shadow-sm flex items-center space-x-1.5 self-start sm:self-auto flex-shrink-0"
              >
                <Sparkles className="w-4 h-4" />
                <span>{uploading ? 'Loading Demo...' : 'Use Safe Demo Documents'}</span>
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4">
            <button
              onClick={() => setCurrentStep(3)}
              className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center space-x-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={() => {
                setCurrentStep(5);
                triggerInspection(application?.id);
              }}
              disabled={uploadedFiles.length === 0}
              className="px-6 py-3 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl font-bold text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm disabled:opacity-50"
            >
              <span>Run Automated Readiness Check</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* STEP 5: AUTOMATED READINESS INSPECTION ANIMATION         */}
      {/* ======================================================== */}
      {currentStep === 5 && (
        <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-200 text-center space-y-6 max-w-xl mx-auto py-16">
          <div className="w-16 h-16 mx-auto rounded-3xl bg-blue-100 text-[#0f2942] flex items-center justify-center font-bold">
            <RefreshCw className="w-8 h-8 animate-spin text-[#0f2942]" />
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-black text-[#0f2942]">
              Inspecting Your Application Readiness
            </h2>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Running multi-tier OCR, date verification, cross-document name matching, and checklist compliance checks.
            </p>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2 max-w-md mx-auto">
            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden border border-slate-200">
              <div
                className="bg-[#0f2942] h-full transition-all duration-300"
                style={{ width: `${evalProgress}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] font-bold text-slate-500">
              <span>{activeCheckText}</span>
              <span>{evalProgress}%</span>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* STEP 6: COMPLETE READINESS REPORT                        */}
      {/* ======================================================== */}
      {currentStep === 6 && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* Top Banner */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold mb-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Inspection Complete</span>
              </div>
              <h2 className="text-lg sm:text-xl font-black text-[#0f2942]">
                Application Readiness Report
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Service: <strong>{selectedProfile?.name}</strong> | Ref: <strong>{application?.reference_number}</strong>
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={handleDownloadPdf}
                disabled={isDownloadingPdf}
                className="px-4 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-sm disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                <span>{isDownloadingPdf ? 'Downloading...' : 'Download Readiness Report (PDF)'}</span>
              </button>
            </div>
          </div>

          {/* Readiness Status Badge */}
          <ReadinessBadge
            status={verificationResult?.readiness_status || 'Action Required'}
            score={verificationResult?.readiness_score || '0%'}
          />

          {/* Prioritized Checklist & Action Plan */}
          <ActionPlanChecklist
            checklist={verificationResult?.prioritized_checklist || []}
            actionPlan={verificationResult?.action_plan || []}
            onRecheck={handleRecheck}
            isRechecking={isRechecking}
            onOpenUpload={() => setCurrentStep(4)}
          />

          {/* Bottom Action Footer */}
          <div className="p-6 bg-slate-50 rounded-3xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-5 py-2.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-xl text-xs font-bold transition"
            >
              Return to Dashboard
            </button>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/official-services')}
                className="px-4 py-2.5 bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-200 rounded-xl text-xs font-bold transition"
              >
                View Official Portals
              </button>
              <button
                onClick={() => navigate('/correction-guidance')}
                className="px-4 py-2.5 bg-[#ea580c] hover:bg-[#c2410c] text-white rounded-xl text-xs font-bold transition shadow-sm"
              >
                Correction Guidance
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PreCheckWizardPage;
