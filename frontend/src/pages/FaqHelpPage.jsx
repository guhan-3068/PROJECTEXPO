import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, ShieldCheck, Sparkles, Phone, ExternalLink, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const FAQS = [
  {
    q: "What if my name has initials in Aadhaar (e.g. 'Aarav S.') but expanded in my 10th marksheet (e.g. 'Aarav Suresh')?",
    a: "In Tamil Nadu and most Indian state education departments, the Class 10 (SSLC / Matriculation) Mark Sheet is the authoritative benchmark for your full name. For admission counseling (such as TNEA or TN Medical Selection), minor initial variations are accepted upon presenting a simple notarized 'One and Same Person' affidavit on non-judicial stamp paper (Rs. 20 / Rs. 50). If you wish to make them identical, you can update your Aadhaar on myAadhaar (myaadhaar.uidai.gov.in) using your 10th mark sheet as Proof of Identity."
  },
  {
    q: "Are documents downloaded from DigiLocker officially valid for college admissions and government jobs?",
    a: "Yes. Under Rule 9A of the Information Technology (Preservation and Retention of Information by Intermediaries Providing Digital Locker Facilities) Rules, 2016, digitally issued documents downloaded from DigiLocker are treated at par with original physical paper certificates. They contain verifiable cryptographic signatures from the issuing board or ministry."
  },
  {
    q: "How long is a Tamil Nadu Income Certificate and Nativity Certificate valid?",
    a: "• Income Certificate: Valid for strictly 1 financial year (or 1 year from the date of issue by the Tahsildar). A new income certificate must be obtained through e-Sevai for each academic year to claim scholarships or fee concessions.\n• Nativity Certificate: Generally has lifetime validity as long as your permanent residence does not change, provided it contains the digital e-District seal and QR code.\n• Community / Caste Certificate: Valid for lifetime."
  },
  {
    q: "What should I do if my document is flagged as 'Blurry / Needs Review'?",
    a: "Do not worry. This is an automated advisory flag to help you prevent official rejection at counseling. Re-scan your original physical document on a flat, well-lit surface at 200–300 DPI without camera flash (flash creates white glare on laminated certificates). Then click 'Replace / Upload' to update the scan."
  },
  {
    q: "What is an official Gazette Notification and when is an Affidavit not enough?",
    a: "A notarized affidavit is usually sufficient for minor spelling errors, initial order changes, or spacing variations. However, for a complete legal name change (e.g. changing from 'Karthik' to 'Vikram') or changing religion/gender, publication in the State Government Gazette (Tamil Nadu Government Press) or Central Gazette of India is legally mandatory."
  },
  {
    q: "Does QUBIX issue official certificates or authenticate them directly with the government?",
    a: "No. QUBIX is an independent pre-submission readiness assistance tool designed to help Indian citizens identify missing files, formatting issues, and expired dates before applying. QUBIX does not issue, modify, approve, or officially authenticate government documents. Official approval is granted solely by the designated government department or university."
  },
  {
    q: "How do I convert an older manual handwritten certificate into a digital e-District certificate?",
    a: "Older paper certificates signed manually by past Tahsildars can be surrendered at your nearest Taluk e-Sevai / Arasu e-Sevai Center. The staff will verify the revenue records and issue a modern, computer-generated e-District certificate with a unique reference number (starting with TN-) and 2D barcode."
  }
];

const HELPLINES = [
  { name: 'UIDAI Aadhaar Helpline', number: '1947', desc: 'Toll-free 24x7 all-India support' },
  { name: 'Income Tax (PAN) Helpdesk', number: '1800 180 1961', desc: 'Toll-free national tax queries' },
  { name: 'Parivahan (Driving Licence / RTO)', number: '0120-4925505', desc: 'Central transport support desk' },
  { name: 'Tamil Nadu CM Helpline (e-Sevai)', number: '1100', desc: 'Tamil Nadu citizen services portal' },
  { name: 'National Scholarship Portal (NSP)', number: '0120-6619540', desc: 'DBT & student scholarship helpline' },
];

const FaqHelpPage = () => {
  const [openIndex, setOpenIndex] = useState(0);

  const toggle = (idx) => {
    setOpenIndex(openIndex === idx ? -1 : idx);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-br from-[#0f2942] via-[#1e3a8a] to-[#0f2942] rounded-3xl p-6 sm:p-8 text-white shadow-md border border-slate-700 space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-semibold text-orange-300 border border-white/10">
          <HelpCircle className="w-3.5 h-3.5 text-orange-400" />
          <span>Citizen Knowledge & Guidance</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
          Frequently Asked Questions & Helpdesk
        </h1>
        <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
          Clear answers to common questions about document validity, name differences, DigiLocker legality, and state revenue certificates.
        </p>
      </div>

      {/* Accordion FAQ */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200 space-y-4">
        <h2 className="text-lg font-black text-[#0f2942] border-b border-slate-100 pb-3">
          Frequently Asked Questions
        </h2>

        <div className="divide-y divide-slate-100">
          {FAQS.map((item, idx) => {
            const isOpen = openIndex === idx;
            return (
              <div key={idx} className="py-4">
                <button
                  onClick={() => toggle(idx)}
                  className="w-full flex items-center justify-between text-left space-x-4 focus:outline-none group"
                >
                  <span className="font-extrabold text-xs sm:text-sm text-slate-900 group-hover:text-brand-600 transition leading-snug">
                    {idx + 1}. {item.q}
                  </span>
                  <div className="p-1 rounded-lg bg-slate-100 text-slate-600 group-hover:bg-slate-200 flex-shrink-0">
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </button>

                {isOpen && (
                  <div className="mt-3 text-xs sm:text-sm text-slate-600 leading-relaxed pl-4 border-l-2 border-[#ea580c] whitespace-pre-line animate-in fade-in duration-150">
                    {item.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Official Government Helplines */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200 space-y-4">
        <h2 className="text-lg font-black text-[#0f2942] border-b border-slate-100 pb-3 flex items-center space-x-2">
          <Phone className="w-5 h-5 text-emerald-600" />
          <span>Official Government Helplines</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {HELPLINES.map((h, i) => (
            <div key={i} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
              <span className="text-xs font-extrabold text-slate-900 line-clamp-1">
                {h.name}
              </span>
              <div className="text-sm font-black text-[#ea580c] font-mono">
                {h.number}
              </div>
              <p className="text-[11px] text-slate-500">
                {h.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Nav Callouts */}
      <div className="p-6 bg-gradient-to-r from-orange-50 via-amber-50 to-emerald-50 rounded-3xl border border-orange-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h3 className="font-extrabold text-sm text-[#0f2942]">
            Need step-by-step correction instructions?
          </h3>
          <p className="text-xs text-slate-600">
            Check our 9-point correction guides with verified government links and Tamil translations.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/correction-guidance"
            className="px-4 py-2.5 bg-[#ea580c] hover:bg-[#c2410c] text-white rounded-xl text-xs font-bold transition shadow-sm"
          >
            Correction Guidance
          </Link>
          <Link
            to="/official-services"
            className="px-4 py-2.5 bg-[#0f2942] hover:bg-[#1e3a8a] text-white rounded-xl text-xs font-bold transition shadow-sm"
          >
            Official Portals
          </Link>
        </div>
      </div>
    </div>
  );
};

export default FaqHelpPage;
