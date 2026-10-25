import React, { useState, useEffect } from 'react';
import {
  Building2, ExternalLink, ShieldAlert, Search, Filter,
  CheckCircle, Globe, Shield, Phone, Sparkles, AlertCircle
} from 'lucide-react';
import { applicationsApi } from '../services/api';

const JURISDICTIONS = ['All', 'Central / All India', 'Tamil Nadu'];
const CATEGORIES = [
  'All',
  'Identity & Citizenship',
  'Tax & Financial Identity',
  'Transport & Licensing',
  'State Revenue & Certificates',
  'Scholarships & Higher Education',
  'College Admission',
  'Digital Document Repository'
];

const OfficialServicesPage = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [confirmUrl, setConfirmUrl] = useState(null);

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    setLoading(true);
    try {
      const data = await applicationsApi.getOfficialServices();
      setServices(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredServices = services.filter((s) => {
    const q = searchQuery.toLowerCase();
    const matchSearch =
      s.name.toLowerCase().includes(q) ||
      s.authority.toLowerCase().includes(q) ||
      s.description.toLowerCase().includes(q) ||
      s.official_url.toLowerCase().includes(q);

    const matchJurisdiction =
      selectedJurisdiction === 'All' ||
      s.jurisdiction.toLowerCase().includes(selectedJurisdiction.toLowerCase());

    const matchCategory =
      selectedCategory === 'All' ||
      s.category.toLowerCase() === selectedCategory.toLowerCase();

    return matchSearch && matchJurisdiction && matchCategory;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-br from-[#0f2942] via-[#1e3a8a] to-[#0f2942] rounded-3xl p-6 sm:p-8 text-white shadow-md border border-slate-700 space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-semibold text-orange-300 border border-white/10">
          <Globe className="w-3.5 h-3.5 text-orange-400" />
          <span>Verified Government Portals Directory</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
          Official Government Services Directory
        </h1>
        <p className="text-xs sm:text-sm text-slate-200 max-w-3xl leading-relaxed">
          Access genuine central and Tamil Nadu state government portals for certificate issuance, demographic updates, Aadhaar corrections, PAN applications, driving licence renewals, and college admissions.
        </p>

        {/* Anti-phishing & Security Alert */}
        <div className="p-3.5 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl text-xs text-orange-200 flex items-start space-x-2">
          <Shield className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Citizen Security Notice:</strong> QUBIX links strictly to official government portals ending in <strong>.gov.in</strong> or authorized statutory agencies. Never enter passwords, OTPs, or Aadhaar biometrics on unauthorized commercial websites.
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search by portal name, department, or service keyword (e.g. Aadhaar, TNeGA, PAN, Sarathi)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-xs pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-[#0f2942] focus:outline-none"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-slate-500 mr-1 flex items-center">
              <Filter className="w-3.5 h-3.5 mr-1" />
              State:
            </span>
            {JURISDICTIONS.map((j) => (
              <button
                key={j}
                onClick={() => setSelectedJurisdiction(j)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                  selectedJurisdiction === j
                    ? 'bg-[#0f2942] text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {j}
              </button>
            ))}
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition ${
                selectedCategory === cat
                  ? 'bg-[#ea580c] text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Portal Grid */}
      {loading ? (
        <div className="py-16 text-center text-slate-500 text-xs">
          Loading verified government directory...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.map((service) => (
            <div
              key={service.id}
              className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:border-brand-500 hover:shadow-md transition flex flex-col justify-between space-y-4 group"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                    {service.jurisdiction}
                  </span>
                  <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                    {service.category}
                  </span>
                </div>

                <div>
                  <h3 className="font-black text-base text-slate-900 group-hover:text-brand-600 transition">
                    {service.name}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-1 font-medium">
                    {service.authority}
                  </p>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed line-clamp-3">
                  {service.description}
                </p>

                {/* Capabilities */}
                <div className="flex flex-wrap gap-1 pt-1">
                  {(service.capabilities || []).map((cap) => (
                    <span
                      key={cap}
                      className="text-[9.5px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200"
                    >
                      {cap.replace('_', ' ')}
                    </span>
                  ))}
                </div>

                {/* Helpdesk */}
                {service.helpdesk && (
                  <div className="flex items-center space-x-1.5 text-[11px] text-slate-500 pt-1">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    <span>{service.helpdesk}</span>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[10px] text-slate-400 font-mono truncate max-w-[150px]">
                  {service.official_url.replace('https://', '').replace('/', '')}
                </span>

                <button
                  onClick={() => setConfirmUrl(service)}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition shadow-sm"
                >
                  <span>Open Website</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* External Navigation Confirmation Modal */}
      {confirmUrl && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-100 text-[#0f2942] flex items-center justify-center font-bold">
              <ExternalLink className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-black text-slate-900">
                Opening Official Government Portal
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                You are about to navigate to an external verified government service website:
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs font-mono text-[#0f2942] break-all font-bold">
              {confirmUrl.official_url}
            </div>

            <p className="text-[11px] text-slate-500 leading-normal">
              Remember: QUBIX is an independent document readiness assistant. You will complete your actual government application directly on the department portal.
            </p>

            <div className="flex items-center space-x-3 pt-2">
              <a
                href={confirmUrl.official_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setConfirmUrl(null)}
                className="flex-1 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold text-center transition shadow-sm flex items-center justify-center space-x-1"
              >
                <span>Proceed to Official Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
              <button
                onClick={() => setConfirmUrl(null)}
                className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OfficialServicesPage;
