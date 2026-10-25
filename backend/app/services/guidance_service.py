"""
QUBIX - Guidance Service
Comprehensive official correction guidance & verified government portal registry
specifically curated for Indian Citizens.
"""

from typing import Dict, Any, List, Optional

OFFICIAL_GOVERNMENT_SERVICES: List[Dict[str, Any]] = [
    {
        "id": "uidai_myaadhaar",
        "name": "myAadhaar Citizen Portal (UIDAI)",
        "authority": "Unique Identification Authority of India (UIDAI), Ministry of Electronics & IT",
        "jurisdiction": "Central / All India",
        "category": "Identity & Citizenship",
        "description": "Official portal to update Aadhaar name, address, date of birth, download e-Aadhaar, lock/unlock biometrics, and check PVC card status.",
        "capabilities": ["CORRECTION_UPDATE", "DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://myaadhaar.uidai.gov.in/",
        "helpdesk": "Toll-Free 1947 | help@uidai.gov.in",
        "security_advisory": "UIDAI never sends SMS asking to install unknown APKs or share OTP. Always verify URL starts with https://*.uidai.gov.in"
    },
    {
        "id": "incometax_pan",
        "name": "Income Tax Department e-Filing Portal",
        "authority": "Income Tax Department, Ministry of Finance, Government of India",
        "jurisdiction": "Central / All India",
        "category": "Tax & Financial Identity",
        "description": "Instant e-PAN generation, Aadhaar-PAN linking status, and PAN verification directly with the Central Board of Direct Taxes (CBDT).",
        "capabilities": ["NEW_APPLICATION", "STATUS_TRACKING"],
        "official_url": "https://www.incometax.gov.in/iec/foportal/",
        "helpdesk": "Toll-Free 1800 180 1961 / 1800 103 0025",
        "security_advisory": "Use for verifying PAN linkage and instant digital e-PAN under Section 139A."
    },
    {
        "id": "protean_nsdl_pan",
        "name": "Protean (formerly NSDL) PAN Services",
        "authority": "Protean eGov Technologies Limited (authorized by Income Tax Dept)",
        "jurisdiction": "Central / All India",
        "category": "Tax & Financial Identity",
        "description": "Official facility for Change / Correction in PAN Data (Form CSF), new PAN application (Form 49A), and reprint of physical PAN card.",
        "capabilities": ["NEW_APPLICATION", "CORRECTION_UPDATE", "DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://www.tin-nsdl.com/",
        "helpdesk": "020-27218080 | tininfo@proteantech.in",
        "security_advisory": "Choose 'Changes or Correction in existing PAN Data' to resolve spelling or DOB errors."
    },
    {
        "id": "utiitsl_pan",
        "name": "UTIITSL PAN Online Portal",
        "authority": "UTI Infrastructure Technology And Services Limited (Govt. of India Enterprise)",
        "jurisdiction": "Central / All India",
        "category": "Tax & Financial Identity",
        "description": "Alternate authorized national agency for issuing, updating, correcting, and verifying PAN cards across India.",
        "capabilities": ["NEW_APPLICATION", "CORRECTION_UPDATE", "DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://www.utiitsl.com/",
        "helpdesk": "022-67931300 / 022-67931302",
        "security_advisory": "Verify PAN status or submit paperless digital correction using Aadhaar e-KYC."
    },
    {
        "id": "parivahan_sewa",
        "name": "Parivahan Sewa / Sarathi Portal",
        "authority": "Ministry of Road Transport and Highways (MoRTH), Government of India",
        "jurisdiction": "All India & State Transport Departments",
        "category": "Transport & Licensing",
        "description": "Central portal for Driving Licence renewal, address change, endorsement, Learner's Licence applications, and RTO appointment booking.",
        "capabilities": ["NEW_APPLICATION", "CORRECTION_UPDATE", "DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://parivahan.gov.in/",
        "helpdesk": "0120-4925505 | helpdesk-morth@gov.in",
        "security_advisory": "Select your state (e.g., Tamil Nadu) under 'Driving Licence Related Services' to route to your regional RTO."
    },
    {
        "id": "digilocker",
        "name": "DigiLocker – National Digital Document Wallet",
        "authority": "Ministry of Electronics & IT (MeitY), Government of India",
        "jurisdiction": "Central / All India",
        "category": "Digital Document Repository",
        "description": "Legally valid digital document repository under Rule 9A of IT Rules 2016. Pull authenticated Aadhaar, CBSE/State Mark Sheets, Driving Licences, and Ration Cards.",
        "capabilities": ["DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://www.digilocker.gov.in/",
        "helpdesk": "support@digitallocker.gov.in",
        "security_advisory": "Issued documents from DigiLocker are treated at par with original physical documents as per the IT Act."
    },
    {
        "id": "tnega_esevai",
        "name": "Tamil Nadu e-Sevai Portal (TNeGA)",
        "authority": "Tamil Nadu e-Governance Agency, Information Technology & Digital Services Dept",
        "jurisdiction": "Tamil Nadu",
        "category": "State Revenue & Certificates",
        "description": "Official citizen portal for Revenue Department certificates: Community, Nativity, Income, First Graduate, Deserted Woman, and Legal Heir certificates.",
        "capabilities": ["NEW_APPLICATION", "DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://tnesevai.tn.gov.in/",
        "helpdesk": "Toll-Free 1100 / 1800 425 1333 | tnesevaihelpdesk@tn.gov.in",
        "security_advisory": "Apply online through citizen login or visit your nearest Grama e-Sevai / Arasu e-Sevai Kendra."
    },
    {
        "id": "tn_edistrict",
        "name": "Tamil Nadu e-District Certificate Verification",
        "authority": "Revenue & Disaster Management Department, Government of Tamil Nadu",
        "jurisdiction": "Tamil Nadu",
        "category": "Certificate Verification",
        "description": "Direct portal to verify authenticity and download digitally signed copies of Tahsildar certificates using application/certificate number and QR code.",
        "capabilities": ["STATUS_TRACKING", "DOWNLOAD_REPRINT"],
        "official_url": "https://edistricts.tn.gov.in/revenue/status.html",
        "helpdesk": "1100 (Tamil Nadu CM Helpline)",
        "security_advisory": "Verify certificate reference numbers starting with TN- before submitting for admissions or recruitments."
    },
    {
        "id": "national_scholarship",
        "name": "National Scholarship Portal (NSP)",
        "authority": "Ministry of Electronics & Information Technology, Government of India",
        "jurisdiction": "Central / All India",
        "category": "Scholarships & Higher Education",
        "description": "One-stop platform for Pre-Matric, Post-Matric, Top-Class, and Merit-cum-Means government scholarships across Ministries.",
        "capabilities": ["NEW_APPLICATION", "STATUS_TRACKING"],
        "official_url": "https://scholarships.gov.in/",
        "helpdesk": "0120-6619540 | helpdesk@nsp.gov.in",
        "security_advisory": "Ensure your bank account is seeded with Aadhaar and active on NPCI mapper for Direct Benefit Transfer (DBT)."
    },
    {
        "id": "tnea_admissions",
        "name": "Tamil Nadu Engineering Admissions (TNEA)",
        "authority": "Directorate of Technical Education (DoTE), Chennai",
        "jurisdiction": "Tamil Nadu",
        "category": "College Admission",
        "description": "Official single-window counseling portal for B.E. / B.Tech admissions in Anna University, government, and self-financing engineering colleges in Tamil Nadu.",
        "capabilities": ["NEW_APPLICATION", "STATUS_TRACKING"],
        "official_url": "https://www.tneaonline.org/",
        "helpdesk": "044-22351014 / 044-22351015 | tneahelpdesk@gmail.com",
        "security_advisory": "Upload certificates only in PDF/JPEG within specified sizes during the online certificate upload schedule."
    },
    {
        "id": "passport_seva",
        "name": "Passport Seva Kendra",
        "authority": "Consular, Passport & Visa (CPV) Division, Ministry of External Affairs",
        "jurisdiction": "Central / All India",
        "category": "Identity & Travel",
        "description": "Official portal for fresh passport applications, reissue, Tatkaal appointments, Police Clearance Certificates (PCC), and Surrender Certificates.",
        "capabilities": ["NEW_APPLICATION", "CORRECTION_UPDATE", "STATUS_TRACKING"],
        "official_url": "https://www.passportindia.gov.in/",
        "helpdesk": "Toll-Free 1800 258 1800",
        "security_advisory": "Beware of fake websites charging unauthorized convenience fees. Official domain ends strictly with .gov.in."
    },
    {
        "id": "egazette_india",
        "name": "The Gazette of India (e-Gazette)",
        "authority": "Department of Publication, Ministry of Housing and Urban Affairs",
        "jurisdiction": "Central / All India",
        "category": "Legal & Name Change",
        "description": "Official weekly publication for legal change of name, religion, or gender. Essential legal proof for substantial identity discrepancies across records.",
        "capabilities": ["DOWNLOAD_REPRINT", "STATUS_TRACKING"],
        "official_url": "https://egazette.gov.in/",
        "helpdesk": "011-23810150 | controller-pub@nic.in",
        "security_advisory": "For Tamil Nadu state-level name change, publication is handled through the Tamil Nadu Government Press (Stationery and Printing Dept)."
    }
]

CORRECTION_GUIDES: Dict[str, Dict[str, Any]] = {
    "name_mismatch": {
        "id": "name_mismatch",
        "title": "How to Resolve Name Mismatch Between Documents",
        "title_ta": "ஆவணங்களுக்கு இடையேயான பெயர் முரண்பாட்டை எவ்வாறு சரிசெய்வது?",
        "issue_type": "MISMATCH",
        "summary": "The applicant's name appears with different spelling, initial placement, or order across submitted records.",
        "summary_ta": "விண்ணப்பதாரரின் பெயர் சமர்ப்பிக்கப்பட்ட ஆவணங்களில் எழுத்துப்பிழை அல்லது முதலெழுத்து மாறுபாட்டுடன் உள்ளது.",
        "sections": {
            "what_is_issue": "A discrepancy was detected where your full name, initials, or father's name differs between two official documents (e.g., Aadhaar has initials expanded, while your School Mark Sheet has initial prefix).",
            "what_is_issue_ta": "உங்கள் ஆதார் அட்டை, மதிப்பெண் சான்றிதழ் அல்லது பிற ஆவணங்களில் உள்ள உங்கள் பெயரிலோ அல்லது தந்தையின் பெயரிலோ முதலெழுத்து அல்லது எழுத்துப்பிழை முரண்பாடு உள்ளது கண்டறியப்பட்டுள்ளது.",
            "why_it_causes_problem": "College admission portals, government scholarship committees, and recruiting authorities use automated matching. A name mismatch can result in immediate rejection, verification holds, or demand for an official gazette notification at counseling.",
            "why_it_causes_problem_ta": "கல்லூரி சேர்க்கை மற்றும் அரசு உதவித்தொகை இணையதளங்கள் கணினி சரிபார்ப்பை நம்பியுள்ளன. பெயர் வேறுபாடு இருந்தால் விண்ணப்பம் நிராகரிக்கப்படலாம் அல்லது அசல் சான்றிதழ் சரிபார்ப்பின் போது நிறுத்தி வைக்கப்படலாம்.",
            "which_doc_needs_attention": "Compare your Primary Identity Document (Aadhaar or Class 10/12 Mark Sheet). In Tamil Nadu and most Indian states, the Class 10 SSLC / Matriculation Mark Sheet is treated as the foundational benchmark for name and DOB.",
            "which_doc_needs_attention_ta": "உங்கள் 10-ஆம் வகுப்பு மதிப்பெண் சான்றிதழை அடிப்படையாக வைத்து மற்ற ஆவணங்களுடன் ஒப்பிடுங்கள். பொதுவாக 10-ஆம் வகுப்பு சான்றிதழில் உள்ள பெயரே கல்வித்துறைக்கு அடிப்படையாகும்.",
            "who_is_authorized": "1. UIDAI (for updating Aadhaar to match education records).\n2. Relevant State Board of Education (for school record corrections).\n3. State Government Printing Press (for official Gazette Name Change Notification).\n4. Notary Public (for One and Same Person Affidavit).",
            "who_is_authorized_ta": "1. ஆதார் சேவை மையம் / UIDAI.\n2. அரசு தேர்வுகள் இயக்ககம் (பள்ளி சான்றிதழ் திருத்தம்).\n3. அரசு எழுதுபொருள் மற்றும் அச்சுத்துறை (அரசிதழ் பெயர் மாற்றம்).\n4. நோட்டரி வழக்கறிஞர் (இரு பெயர்களும் ஒருவரே என்பதற்கான உறுதிமொழி பத்திரம்).",
            "official_correction_process": [
                "Step 1: Inspect the original physical certificates to verify if this is an OCR scanning error or an actual difference in official records.",
                "Step 2: If the variation is minor (such as 'Aarav S.' vs 'Aarav Suresh'), obtain a notarized 'One and Same Person' affidavit on non-judicial stamp paper (Rs. 20 / Rs. 50).",
                "Step 3: If your Aadhaar spelling is incorrect, log into myAadhaar (https://myaadhaar.uidai.gov.in/) and submit a Demographic Update using your 10th mark sheet or passport as Proof of Identity (POI).",
                "Step 4: For significant legal name changes, publish a notification in your State Government Gazette (Tamil Nadu e-Gazette or Central Gazette) and retain copies of the gazette issue."
            ],
            "official_correction_process_ta": [
                "படி 1: உங்கள் அசல் ஆவணங்களை நேரில் பார்த்து, இது கணினி ஸ்கேன் பிழையா அல்லது உண்மையான ஆவணப் பிழையா என உறுதி செய்யவும்.",
                "படி 2: சிறிய முதலெழுத்து மாறுபாட்டிற்கு, நோட்டரி வழக்கறிஞரிடம் 'இரு பெயர்களும் ஒருவரே' என்பதற்கான உறுதிமொழிப் பத்திரம் (One and the Same Affidavit) பெறலாம்.",
                "படி 3: ஆதாரில் பிழை இருந்தால் myAadhaar இணையதளத்தில் 10-ஆம் வகுப்பு சான்றிதழை அடையாள சான்றாக இணைத்து ஆன்லைனில் புதுப்பிக்கலாம்.",
                "படி 4: பெரிய பெயர் மாற்றங்களுக்கு தமிழ்நாடு அரசு அரசிதழில் (Gazette) பெயர் மாற்றம் செய்து சான்றிதழ் வைத்திருக்க வேண்டும்."
            ],
            "supporting_docs_needed": [
                "Class 10 / SSLC Mark Sheet with correct name",
                "Aadhaar Card or Passport",
                "Parent's Photo ID (Aadhaar / Voter ID)",
                "Notarized Affidavit on Stamp Paper (if required by counseling authority)"
            ],
            "supporting_docs_needed_ta": [
                "சரியான பெயர் கொண்ட 10-ஆம் வகுப்பு மதிப்பெண் சான்றிதழ்",
                "ஆதார் அட்டை அல்லது கடவுச்சீட்டு",
                "பெற்றோரின் அடையாள அட்டை",
                "நோட்டரி உறுதிமொழி பத்திரம்"
            ],
            "official_service_portal": "https://myaadhaar.uidai.gov.in/",
            "official_service_name": "myAadhaar Demographic Update & State Gazette Office",
            "after_correction": "Once the updated Aadhaar or Gazette copy is issued, download the verified digital e-Aadhaar with valid QR code or keep the original Gazette copy ready for certificate verification.",
            "after_correction_ta": "திருத்தப்பட்ட ஆதார் அட்டை அல்லது அரசிதழ் நகல் கிடைத்தவுடன், புதிய மின்-ஆதாரை பதிவிறக்கம் செய்து வைத்துக்கொள்ளவும்.",
            "what_to_recheck": "Ensure the first name, surname, initials, and father's name match character-for-character with your admission application before clicking final submit."
        }
    },
    "aadhaar_update": {
        "id": "aadhaar_update",
        "title": "How to Correct or Update Aadhaar Card Details",
        "title_ta": "ஆதார் அட்டை விவரங்களை எவ்வாறு திருத்துவது அல்லது புதுப்பிப்பது?",
        "issue_type": "INCORRECT_DETAILS",
        "summary": "Aadhaar number or demographic details (name, date of birth, address) are outdated or contain errors.",
        "summary_ta": "ஆதார் அட்டையில் உள்ள பெயர், பிறந்த தேதி அல்லது முகவரியில் திருத்தம் தேவைப்படுகிறது.",
        "sections": {
            "what_is_issue": "Your Aadhaar record has an inaccurate name, incorrect date of birth, unexpanded initials, or an outdated address.",
            "what_is_issue_ta": "உங்கள் ஆதார் அட்டையில் பெயர், பிறந்த தேதி அல்லது முகவரி தற்போதைய அதிகாரப்பூர்வ ஆவணங்களுடன் பொருந்தவில்லை.",
            "why_it_causes_problem": "National Scholarship Portal (NSP), DigiLocker, Parivahan, and banking KYC verify identity using UIDAI OTP e-KYC. If the Aadhaar data does not match, automated e-KYC authentication will fail.",
            "why_it_causes_problem_ta": "அரசு உதவித்தொகை, வங்கி கணக்கு மற்றும் ஓட்டுநர் உரிமத்திற்கு ஆதாரின் தானியங்கி e-KYC சரிபார்ப்பு கட்டாயம். விவரங்கள் பொருந்தாவிட்டால் விண்ணப்பம் நிராகரிக்கப்படும்.",
            "which_doc_needs_attention": "Aadhaar Card (12-digit Unique Identification Number).",
            "which_doc_needs_attention_ta": "ஆதார் அட்டை (12 இலக்க அடையாள எண்).",
            "who_is_authorized": "Unique Identification Authority of India (UIDAI) and authorized Aadhaar Enrolment Centers / Post Offices / Banks.",
            "who_is_authorized_ta": "இந்திய தனித்துவ அடையாள ஆணையம் (UIDAI) மற்றும் அங்கீகரிக்கப்பட்ட அஞ்சலக / வங்கி ஆதார் சேவை மையங்கள்.",
            "official_correction_process": [
                "Step 1: Check your registered mobile number. If your current mobile number is linked to Aadhaar, log into https://myaadhaar.uidai.gov.in/",
                "Step 2: For Address Update: Select 'Update Address', upload valid proof (Ration Card, Voter ID, Bank Statement, or EB Bill), and pay official fee of Rs. 50.",
                "Step 3: For Name, Date of Birth, or Mobile Number Update: Book an appointment online at https://appointments.uidai.gov.in/ and visit your nearest Aadhaar Seva Kendra or post office.",
                "Step 4: Present your original Class 10 Mark Sheet or Birth Certificate for DOB / Name correction."
            ],
            "official_correction_process_ta": [
                "படி 1: உங்கள் மொபைல் எண் ஆதாருடன் இணைக்கப்பட்டுள்ளதா எனப் பார்த்து, myaadhaar.uidai.gov.in தளத்தில் உள்நுழையவும்.",
                "படி 2: முகவரி மாற்றத்திற்கு: 'Update Address' என்பதை தேர்வு செய்து குடும்ப அட்டை அல்லது மின்சார கட்டண ரசீதை பதிவேற்றவும் (கட்டணம் ரூ. 50).",
                "படி 3: பெயர், பிறந்த தேதி அல்லது மொபைல் எண் மாற்றத்திற்கு: அருகிலுள்ள அஞ்சலக அல்லது வங்கி ஆதார் சேவை மையத்திற்கு நேரில் செல்ல வேண்டும்.",
                "படி 4: 10-ஆம் வகுப்பு சான்றிதழ் அல்லது பிறப்பு சான்றிதழை அசல் ஆவணமாக சமர்ப்பிக்கவும்."
            ],
            "supporting_docs_needed": [
                "Proof of Identity (POI): 10th Mark Sheet, Passport, or PAN Card",
                "Proof of Date of Birth (DOB): Birth Certificate or SSLC Mark Sheet",
                "Proof of Address (POA): Smart Family Card, Electricity Bill, or Bank Passbook"
            ],
            "supporting_docs_needed_ta": [
                "அடையாள சான்று: 10-ஆம் வகுப்பு மதிப்பெண் சான்றிதழ், பான் கார்டு அல்லது பாஸ்போர்ட்",
                "பிறந்த தேதி சான்று: பிறப்பு சான்றிதழ் அல்லது SSLC மதிப்பெண் சான்றிதழ்",
                "முகவரி சான்று: குடும்ப அட்டை, மின் கட்டண ரசீது அல்லது வங்கி பாஸ்புக்"
            ],
            "official_service_portal": "https://myaadhaar.uidai.gov.in/",
            "official_service_name": "myAadhaar Citizen Portal (UIDAI)",
            "after_correction": "Track your Update Request Number (URN) on myAadhaar. Once approved (usually 3 to 15 days), download the revised e-Aadhaar PDF.",
            "after_correction_ta": "URN எண்ணை வைத்து நிலையை கண்காணிக்கவும். திருத்தம் செய்யப்பட்டதும் புதிய இ-ஆதாரை பதிவிறக்கம் செய்து கொள்ளவும்.",
            "what_to_recheck": "Verify that your 12-digit Aadhaar number is active, the QR code is intact, and the updated name matches your other application certificates."
        }
    },
    "pan_correction": {
        "id": "pan_correction",
        "title": "How to Correct PAN Card Details (Form CSF)",
        "title_ta": "பான் கார்டு விவரங்களை எவ்வாறு திருத்துவது?",
        "issue_type": "INCORRECT_DETAILS",
        "summary": "PAN card shows incorrect name spelling, wrong date of birth, or needs father's name update.",
        "summary_ta": "பான் கார்டில் உள்ள பெயர் அல்லது பிறந்த தேதியில் திருத்தம் தேவைப்படுகிறது.",
        "sections": {
            "what_is_issue": "Your 10-character Permanent Account Number (PAN) card contains typographical errors in the applicant's name, parent's name, or date of birth.",
            "what_is_issue_ta": "பான் கார்டில் உள்ள பெயர், பிறந்த தேதி அல்லது தந்தையின் பெயரில் எழுத்துப்பிழை உள்ளது.",
            "why_it_causes_problem": "Under Income Tax regulations, PAN must match Aadhaar for KYC verification, bank account opening, salary processing, and financial assistance. Inconsistent PAN details trigger automated rejection.",
            "why_it_causes_problem_ta": "வங்கி கணக்கு தொடங்குவதற்கும், அரசு உதவித்தொகை பெறுவதற்கும் ஆதார்-பான் இணைப்பு கட்டாயம். விவரங்கள் தவறாக இருந்தால் கணக்கு தொடங்குவது தடைபடும்.",
            "which_doc_needs_attention": "PAN Card (10-character alphanumeric ID, e.g. ABCDE1234F).",
            "which_doc_needs_attention_ta": "பான் கார்டு (10 இலக்க எண்).",
            "who_is_authorized": "Income Tax Department through authorized service providers Protean (NSDL) and UTIITSL.",
            "who_is_authorized_ta": "வருமான வரித்துறை மற்றும் அதன் அங்கீகரிக்கப்பட்ட NSDL (Protean) / UTIITSL நிறுவனங்கள்.",
            "official_correction_process": [
                "Step 1: Open the official Protean PAN portal (https://www.tin-nsdl.com/) or UTIITSL portal (https://www.utiitsl.com/).",
                "Step 2: Under Application Type, select 'Changes or Correction in existing PAN Data / Reprint of PAN Card (No change in existing PAN Data)'.",
                "Step 3: Fill the online Form CSF (Correction Services Form), ensuring you check the box next to the fields you want to change.",
                "Step 4: Authenticate paperless using Aadhaar OTP e-KYC or upload scanned signature and supporting proof.",
                "Step 5: Pay the official government processing fee (Rs. 107 for physical card dispatch within India)."
            ],
            "official_correction_process_ta": [
                "படி 1: அதிகாரப்பூர்வ NSDL (tin-nsdl.com) அல்லது UTIITSL (utiitsl.com) இணையதளத்திற்கு செல்லவும்.",
                "படி 2: 'Changes or Correction in existing PAN Data' என்ற படிவத்தை தேர்ந்தெடுக்கவும்.",
                "படி 3: திருத்த வேண்டிய விவரங்களை பூர்த்தி செய்து, ஆதார் OTP மூலம் மின்-கையொப்பமிடவும்.",
                "படி 4: நிர்ணயிக்கப்பட்ட கட்டணத்தை (ரூ. 107) இணையவழியில் செலுத்தவும்."
            ],
            "supporting_docs_needed": [
                "Copy of existing PAN card or PAN allotment letter",
                "Proof of Identity with correct name (Aadhaar Card or Passport)",
                "Proof of Date of Birth (Birth Certificate or 10th Mark Sheet)"
            ],
            "supporting_docs_needed_ta": [
                "தற்போதைய பான் கார்டு நகல்",
                "சரியான பெயர் கொண்ட ஆதார் அட்டை",
                "பிறந்த தேதி சான்று (பிறப்பு சான்றிதழ் அல்லது 10-ஆம் வகுப்பு மதிப்பெண் சான்றிதழ்)"
            ],
            "official_service_portal": "https://www.tin-nsdl.com/",
            "official_service_name": "Protean (NSDL) TIN Portal / UTIITSL",
            "after_correction": "Track acknowledgment number. Once processed, you will receive an updated digital e-PAN via email, followed by the physical card by post.",
            "after_correction_ta": "ஒப்புகை எண்ணை வைத்து நிலையை அறியலாம். புதிய இ-பான் மின்னஞ்சலில் வரும், அசல் அட்டை தபாலில் வரும்.",
            "what_to_recheck": "Ensure your corrected PAN is linked with your Aadhaar on the Income Tax e-Filing portal (incometax.gov.in)."
        }
    },
    "dl_renewal": {
        "id": "dl_renewal",
        "title": "How to Renew an Expired Driving Licence (Parivahan)",
        "title_ta": "காலாவதியான ஓட்டுநர் உரிமத்தை எவ்வாறு புதுப்பிப்பது?",
        "issue_type": "EXPIRED",
        "summary": "Your Driving Licence or Learner's Licence has crossed its official validity date.",
        "summary_ta": "உங்கள் ஓட்டுநர் உரிமம் அல்லது பழகுநர் உரிமம் காலாவதியாகிவிட்டது.",
        "sections": {
            "what_is_issue": "The uploaded Driving Licence has expired or the 6-month validity period of the Learner's Licence (LLR) has elapsed.",
            "what_is_issue_ta": "உங்கள் ஓட்டுநர் உரிமத்தின் செல்லுபடியாகும் காலம் முடிவடைந்துவிட்டது.",
            "why_it_causes_problem": "Driving with an expired licence is a punishable traffic offense under the Motor Vehicles Act. Transport departments, commercial fleets, and job recruitment portals automatically reject expired licences.",
            "why_it_causes_problem_ta": "காலாவதியான உரிமத்தை வைத்து வாகனம் ஓட்டுவது அல்லது வேலைவாய்ப்பிற்கு விண்ணப்பிப்பது சட்டப்படி குற்றமாகும்.",
            "which_doc_needs_attention": "Driving Licence (DL) / Learner's Licence (LLR).",
            "which_doc_needs_attention_ta": "ஓட்டுநர் உரிமம் (DL).",
            "who_is_authorized": "State Transport Department / Regional Transport Office (RTO) via Ministry of Road Transport and Highways (MoRTH).",
            "who_is_authorized_ta": "மாநில போக்குவரத்து துறை / வட்டார போக்குவரத்து அலுவலகம் (RTO).",
            "official_correction_process": [
                "Step 1: Visit the official central portal https://parivahan.gov.in/ and select 'Online Services' -> 'Driving Licence Related Services'.",
                "Step 2: Choose your state (e.g., Tamil Nadu) and click 'Apply for DL Renewal'.",
                "Step 3: Enter your Driving Licence Number and Date of Birth.",
                "Step 4: Upload Form 1A Medical Certificate (signed by a registered medical practitioner if applicant is above 40 years of age or for transport category).",
                "Step 5: Pay the renewal fee online and download the acknowledgment slip. In contactless states, the renewed DL is dispatched directly by speed post."
            ],
            "official_correction_process_ta": [
                "படி 1: parivahan.gov.in இணையதளத்தில் 'Driving Licence Related Services' செல்லவும்.",
                "படி 2: மாநிலத்தை தேர்வு செய்து (தமிழ்நாடு) 'Apply for DL Renewal' என்பதை கிளிக் செய்யவும்.",
                "படி 3: உரிம எண் மற்றும் பிறந்த தேதியை உள்ளிடவும்.",
                "படி 4: 40 வயதுக்கு மேற்பட்டவர்கள் மருத்துவ சான்றிதழ் (Form 1A) பதிவேற்ற வேண்டும்.",
                "படி 5: அரசு கட்டணத்தை ஆன்லைனில் செலுத்தி ஒப்புகை சீட்டை பெறவும்."
            ],
            "supporting_docs_needed": [
                "Expired Original Driving Licence",
                "Form 1 (Self-declaration) and Form 1A (Medical Certificate if applicable)",
                "Proof of Address (Aadhaar or Smart Family Card)",
                "Passport size photograph"
            ],
            "supporting_docs_needed_ta": [
                "காலாவதியான அசல் ஓட்டுநர் உரிமம்",
                "மருத்துவ சான்றிதழ் (Form 1A - தேவைப்பட்டால்)",
                "முகவரி சான்று (ஆதார் / குடும்ப அட்டை)",
                "புகைப்படம்"
            ],
            "official_service_portal": "https://parivahan.gov.in/",
            "official_service_name": "Parivahan Sewa (MoRTH / Sarathi)",
            "after_correction": "Once renewed, download your digital Driving Licence instantly into your DigiLocker or mParivahan mobile app.",
            "after_correction_ta": "புதுப்பிக்கப்பட்ட உரிமத்தை டிஜிலாக்கர் (DigiLocker) அல்லது mParivahan செயலியில் உடனே பதிவிறக்கம் செய்து கொள்ளலாம்.",
            "what_to_recheck": "Ensure the licence category (MCWG, LMV) and validity dates are correctly reflected before application upload."
        }
    },
    "income_reissue": {
        "id": "income_reissue",
        "title": "How to Obtain or Renew a Valid Income Certificate (Tamil Nadu e-Sevai)",
        "title_ta": "வருமானச் சான்றிதழை எவ்வாறு புதிதாகப் பெறுவது அல்லது புதுப்பிப்பது?",
        "issue_type": "EXPIRED",
        "summary": "Income Certificate has crossed its 1-year financial validity or lacks Tahsildar seal.",
        "summary_ta": "வருமானச் சான்றிதழ் ஒரு வருடம் கடந்து காலாவதியாகிவிட்டது அல்லது வட்டாட்சியர் கையொப்பம் இல்லை.",
        "sections": {
            "what_is_issue": "In Tamil Nadu and most Indian states, Income Certificates are valid for exactly 1 financial year (or 1 year from the date of issuance). An older certificate cannot be used for current academic year scholarships or fee concessions.",
            "what_is_issue_ta": "வருமானச் சான்றிதழ் ஒரு நிதி ஆண்டுக்கு (1 வருடம்) மட்டுமே செல்லுபடியாகும். பழைய சான்றிதழை நடப்பு கல்வி ஆண்டுக்கு பயன்படுத்த முடியாது.",
            "why_it_causes_problem": "Scholarship eligibility, tuition fee waivers, and government quota concessions have strict income ceilings. Submitting an expired income certificate leads to automatic disqualification.",
            "why_it_causes_problem_ta": "அரசு உதவித்தொகை மற்றும் கட்டண சலுகைகளுக்கு வருமான வரம்பு நிர்ணயிக்கப்பட்டுள்ளது. காலாவதியான சான்றிதழ் சமர்ப்பித்தால் உதவித்தொகை நிராகரிக்கப்படும்.",
            "which_doc_needs_attention": "Income Certificate issued by Revenue Department (Tahsildar / Zonal Deputy Tahsildar).",
            "which_doc_needs_attention_ta": "வட்டாட்சியர் அலுவலகம் வழங்கும் வருமானச் சான்றிதழ்.",
            "who_is_authorized": "Tahsildar / Revenue Department, Government of Tamil Nadu (via TNeGA).",
            "who_is_authorized_ta": "வருவாய்த்துறை / வட்டாட்சியர் அலுவலகம் (TNeGA e-Sevai).",
            "official_correction_process": [
                "Step 1: Visit the Tamil Nadu e-Sevai citizen portal (https://tnesevai.tn.gov.in/) or your nearest Arasu e-Sevai Kendra / CSC center.",
                "Step 2: Provide your CAN (Citizen Access Number). If you do not have a CAN, register CAN using Aadhaar and mobile OTP.",
                "Step 3: Select Revenue Department -> 'REV-103 Income Certificate'.",
                "Step 4: Upload supporting proof of income (Salary Certificate / Form 16 from employer, IT Return, or VAO inquiry slip for agricultural / unorganized labor).",
                "Step 5: Pay the official nominal service fee of Rs. 60. The application is verified by the VAO (Village Administrative Officer), Revenue Inspector (RI), and approved by the Tahsildar within 15 working days."
            ],
            "official_correction_process_ta": [
                "படி 1: தமிழ்நாடு இ-சேவை இணையதளம் (tnesevai.tn.gov.in) அல்லது அருகிலுள்ள அரசு இ-சேவை மையத்திற்கு செல்லவும்.",
                "படி 2: CAN எண்ணை பதிவு செய்து கொள்ளவும்.",
                "படி 3: வருவாய்த்துறை -> 'வருமானச் சான்றிதழ் (REV-103)' என்பதை தேர்வு செய்யவும்.",
                "படி 4: ஊதியச் சான்றிதழ், குடும்ப அட்டை மற்றும் ஆதாரை இணைக்கவும் (கட்டணம் ரூ. 60).",
                "படி 5: VAO, வருவாய் ஆய்வாளர் (RI) ஆய்வுக்குப் பிறகு வட்டாட்சியரால் ஒப்புதல் அளிக்கப்பட்டு சான்றிதழ் வழங்கப்படும்."
            ],
            "supporting_docs_needed": [
                "Aadhaar Card of the applicant and family members",
                "Smart Family Card (Ration Card)",
                "Salary Certificate / Payslip / Form 16 / Bank Statement",
                "Self-declaration / Affidavit of annual family income"
            ],
            "supporting_docs_needed_ta": [
                "விண்ணப்பதாரர் மற்றும் குடும்ப உறுப்பினர்களின் ஆதார் அட்டை",
                "ஸ்மார்ட் குடும்ப அட்டை (ரேஷன் கார்டு)",
                "மாத ஊதியச் சான்றிதழ் அல்லது வருமான உறுதிமொழிப் பத்திரம்",
                "வங்கி பாஸ்புக் நகல்"
            ],
            "official_service_portal": "https://tnesevai.tn.gov.in/",
            "official_service_name": "Tamil Nadu e-Sevai Portal (TNeGA)",
            "after_correction": "Download the digitally signed PDF certificate containing the 2D Barcode and digital signature of the Tahsildar from the e-District portal.",
            "after_correction_ta": "வட்டாட்சியரின் மின்னணு கையொப்பம் மற்றும் QR குறியீடு கொண்ட சான்றிதழை பதிவிறக்கம் செய்து கொள்ளவும்.",
            "what_to_recheck": "Ensure the annual family income figure shown on the certificate is within the eligibility threshold of the scheme you are applying for."
        }
    },
    "nativity_reissue": {
        "id": "nativity_reissue",
        "title": "How to Obtain or Verify a Nativity / Domicile Certificate",
        "title_ta": "இருப்பிட / பிறப்பிடச் சான்றிதழை எவ்வாறு பெறுவது?",
        "issue_type": "MISSING_DOC",
        "summary": "Nativity or Residence Certificate is missing or requires Tahsildar e-District endorsement.",
        "summary_ta": "இருப்பிடச் சான்றிதழ் இணைக்கப்படவில்லை அல்லது வட்டாட்சியர் ஒப்புதல் தேவைப்படுகிறது.",
        "sections": {
            "what_is_issue": "A Nativity (Residence) Certificate proving you or your parents are bona fide residents of the state is required for government quotas and state admissions (e.g. TNEA, TN Medical Selection).",
            "what_is_issue_ta": "மாநில ஒதுக்கீட்டு இடங்களுக்கும், அரசு சலுகைகளுக்கும் நீங்கள் அந்த மாநிலத்தை சேர்ந்தவர் என்பதை நிரூபிக்கும் இருப்பிடச் சான்றிதழ் தேவைப்படுகிறது.",
            "why_it_causes_problem": "Candidates without a valid Nativity Certificate are classified as 'Other State' or 'Open Competition (General)', losing valuable home-state reservation benefits and quota counseling seats.",
            "why_it_causes_problem_ta": "இருப்பிடச் சான்றிதழ் இல்லையெனில், நீங்கள் பிற மாநிலத்தவராக கருதப்பட்டு மாநில இடஒதுக்கீடு சலுகைகளை இழக்க நேரிடும்.",
            "which_doc_needs_attention": "Nativity / Domicile Certificate (Revenue Department).",
            "which_doc_needs_attention_ta": "வருவாய்த்துறை வழங்கும் இருப்பிடச் சான்றிதழ்.",
            "who_is_authorized": "Tahsildar / Revenue Department via e-Sevai.",
            "who_is_authorized_ta": "வருவாய்த்துறை / வட்டாட்சியர் அலுவலகம்.",
            "official_correction_process": [
                "Step 1: Open https://tnesevai.tn.gov.in/ or visit your local e-Sevai center.",
                "Step 2: Select 'REV-101 Nativity Certificate' under Revenue Department.",
                "Step 3: Upload applicant's Birth Certificate and School Transfer Certificate (TC) showing schooling in Tamil Nadu.",
                "Step 4: Upload parents' documents (Ration Card, Voter ID, or Parent's School TC).",
                "Step 5: Submit application with official fee (Rs. 60). Verification is completed by the Revenue Inspector and Tahsildar."
            ],
            "official_correction_process_ta": [
                "படி 1: tnesevai.tn.gov.in இணையதளத்திற்கு செல்லவும் அல்லது இ-சேவை மையத்தை அணுகவும்.",
                "படி 2: வருவாய்த்துறை -> 'இருப்பிடச் சான்றிதழ் (REV-101)' என்பதை தேர்ந்தெடுக்கவும்.",
                "படி 3: பிறப்பு சான்றிதழ், பள்ளி மாற்றுச் சான்றிதழ் (TC), குடும்ப அட்டை ஆகியவற்றை இணைக்கவும்.",
                "படி 4: கட்டணம் ரூ. 60 செலுத்தி வட்டாட்சியரின் ஒப்புதல் பெற்ற சான்றிதழை பெறவும்."
            ],
            "supporting_docs_needed": [
                "Applicant's Birth Certificate or School Transfer Certificate (TC)",
                "Smart Family Card (Ration Card)",
                "Aadhaar Card or Voter ID of applicant / parent",
                "Property Tax Receipt / Rental Agreement / EB Bill"
            ],
            "supporting_docs_needed_ta": [
                "விண்ணப்பதாரரின் பிறப்பு சான்றிதழ் அல்லது பள்ளி TC",
                "குடும்ப அட்டை (ரேஷன் கார்டு)",
                "பெற்றோரின் ஆதார் அல்லது வாக்காளர் அட்டை",
                "சொத்து வரி ரசீது அல்லது மின் கட்டண ரசீது"
            ],
            "official_service_portal": "https://tnesevai.tn.gov.in/",
            "official_service_name": "Tamil Nadu e-Sevai Portal (TNeGA)",
            "after_correction": "Download the verified e-District certificate with the unique certificate reference number.",
            "after_correction_ta": "சான்றிதழ் எண்ணுடன் கூடிய டிஜிட்டல் சான்றிதழை பதிவிறக்கம் செய்து கொள்ளவும்.",
            "what_to_recheck": "Verify that your native place and permanent residence address correctly match your application form."
        }
    },
    "blurry_scan": {
        "id": "blurry_scan",
        "title": "How to Replace a Blurry or Unreadable Document Scan",
        "title_ta": "மங்கலான அல்லது தெளிவற்ற ஆவணத்தை எவ்வாறு மாற்றுவது?",
        "issue_type": "UNREADABLE",
        "summary": "Document image resolution is too low, text is smudged, or camera flash has caused glare.",
        "summary_ta": "ஆவணத்தின் தரம் குறைவாக உள்ளது அல்லது எழுத்துக்கள் தெளிவாக தெரியவில்லை.",
        "sections": {
            "what_is_issue": "The automated OCR optical character recognition failed because the document is blurry, skewed, shadows cover key text, or resolution is below the 200 DPI threshold.",
            "what_is_issue_ta": "ஆவணம் மங்கலாகவோ அல்லது நிழல் விழுந்தோ இருப்பதால் கணினியால் எழுத்துக்களை படிக்க முடியவில்லை.",
            "why_it_causes_problem": "Government admissions and verification teams reject illegible scans immediately during document scrutiny because critical details (roll numbers, marks, signatures) cannot be confirmed.",
            "why_it_causes_problem_ta": "மதிப்பெண்கள் அல்லது பதிவு எண் தெளிவாக தெரியாவிட்டால் சரிபார்ப்பு அதிகாரிகள் விண்ணப்பத்தை நிராகரிப்பார்கள்.",
            "which_doc_needs_attention": "The specific document flagged as low-confidence or blurry.",
            "which_doc_needs_attention_ta": "மங்கலாக இருப்பதாக சுட்டிக்காட்டப்பட்ட குறிப்பிட்ட ஆவணம்.",
            "who_is_authorized": "Applicant (you can re-scan your original physical document).",
            "who_is_authorized_ta": "விண்ணப்பதாரரே அசல் ஆவணத்தை மீண்டும் தெளிவாக ஸ்கேன் செய்யலாம்.",
            "official_correction_process": [
                "Step 1: Place your original physical document on a flat, clean surface with uniform daylight or overhead lighting.",
                "Step 2: Do NOT use camera flash, which creates blinding reflections on laminated certificates.",
                "Step 3: Hold the smartphone camera parallel directly above the document without tilting.",
                "Step 4: Use a free scanner app (like Adobe Scan, Microsoft Lens, or your phone's built-in document scanner) to crop precisely to document borders.",
                "Step 5: Export as a clean PDF or sharp JPEG at 200 to 300 DPI (file size between 100 KB and 2 MB)."
            ],
            "official_correction_process_ta": [
                "படி 1: அசல் ஆவணத்தை சமமான மேஜையில் வைத்து, நல்ல வெளிச்சத்தில் வைக்கவும்.",
                "படி 2: கேமரா ஃபிளாஷ் (Flash) பயன்படுத்த வேண்டாம். அது லேமினேஷனில் பளபளப்பை உண்டாக்கும்.",
                "படி 3: ஆவணத்தின் நான்கு மூலைகளும் தெரியும்படி நேராக வைத்து ஸ்கேன் செய்யவும்.",
                "படி 4: Adobe Scan அல்லது Microsoft Lens போன்ற செயலிகளை பயன்படுத்தி PDF ஆக மாற்றவும்.",
                "படி 5: கோப்பு அளவு 100 KB முதல் 2 MB வரை இருக்குமாறு பார்த்துக் கொள்ளவும்."
            ],
            "supporting_docs_needed": [
                "Original Physical Certificate (clean, uncreased)",
                "Document scanner or high-resolution mobile camera"
            ],
            "supporting_docs_needed_ta": [
                "அசல் சான்றிதழ்",
                "தெளிவான கேமரா அல்லது ஸ்கேனர்"
            ],
            "official_service_portal": "https://www.digilocker.gov.in/",
            "official_service_name": "DigiLocker (for downloading original digital PDF)",
            "after_correction": "Click 'Replace / Upload' in the QUBIX cockpit and upload the new clean file.",
            "after_correction_ta": "QUBIX தளத்தில் 'Replace / Upload' கொடுத்து புதிய தெளிவான ஆவணத்தை பதிவேற்றவும்.",
            "what_to_recheck": "Zoom in to 100% on your screen and verify that your name, dates, numbers, and official signatures are crisp and readable."
        }
    },
    "missing_ref_number": {
        "id": "missing_ref_number",
        "title": "How to Fix Missing Certificate Number or Official Seal",
        "title_ta": "சான்றிதழ் எண் அல்லது அரசு முத்திரை விடுபட்டதை எவ்வாறு சரிசெய்வது?",
        "issue_type": "MISSING_FIELD",
        "summary": "Certificate lacks official reference number, issue date, or verifiable digital signature.",
        "summary_ta": "சான்றிதழில் குறிப்பு எண், வழங்கப்பட்ட தேதி அல்லது டிஜிட்டல் கையொப்பம் இல்லை.",
        "sections": {
            "what_is_issue": "The document uploaded appears incomplete, lacks an official serial number (e.g., TN-REV reference number), or the bottom portion containing the issuing officer's signature/seal is cropped out.",
            "what_is_issue_ta": "சான்றிதழின் கீழ் பகுதியில் உள்ள வட்டாட்சியர் முத்திரை அல்லது சான்றிதழ் எண் வெட்டுப்பட்டுள்ளது.",
            "why_it_causes_problem": "Admission and recruiting authorities cannot verify certificates in the state e-District database without a valid certificate reference number.",
            "why_it_causes_problem_ta": "சான்றிதழ் எண் இல்லையென்றால், அரசு இணையதளத்தில் அதன் உண்மைத்தன்மையை சரிபார்க்க முடியாது.",
            "which_doc_needs_attention": "The certificate flagged with missing reference details.",
            "which_doc_needs_attention_ta": "எண் விடுபட்டுள்ள குறிப்பிட்ட சான்றிதழ்.",
            "who_is_authorized": "Issuing Authority (Tahsildar / School Board) or the Applicant (if cropped scan).",
            "who_is_authorized_ta": "சான்றிதழ் வழங்கிய துறை அல்லது விண்ணப்பதாரர்.",
            "official_correction_process": [
                "Step 1: Check your physical paper copy to ensure the full page, including top headers and bottom QR code/signature blocks, is visible.",
                "Step 2: If the document was cropped, re-scan the entire full page from edge to edge.",
                "Step 3: If you have an older handwritten paper certificate without an online number, visit your Taluk e-Sevai center and apply for an Online Digital Certificate by surrendering the legacy paper certificate copy.",
                "Step 4: Verify the certificate number on the Tamil Nadu e-District portal (https://edistricts.tn.gov.in/revenue/status.html)."
            ],
            "official_correction_process_ta": [
                "படி 1: அசல் தாளில் சான்றிதழ் எண் மற்றும் கீழ் உள்ள QR குறியீடு முழுமையாக உள்ளதா என பார்க்கவும்.",
                "படி 2: ஸ்கேன் செய்யும்போது விளிம்புகள் வெட்டப்படாமல் முழு பக்கத்தையும் ஸ்கேன் செய்யவும்.",
                "படி 3: பழைய கையால் எழுதப்பட்ட சான்றிதழ் என்றால், தாலுகா அலுவலகத்தில் கொடுத்து புதிய ஆன்லைன் கணினி சான்றிதழாக மாற்றிக்கொள்ளவும்.",
                "படி 4: edistricts.tn.gov.in தளத்தில் சான்றிதழ் நிலையை சரிபார்க்கவும்."
            ],
            "supporting_docs_needed": [
                "Full-page uncropped certificate copy",
                "Legacy manual certificate (if converting to digital)",
                "Smart Family Card and Aadhaar"
            ],
            "supporting_docs_needed_ta": [
                "முழு பக்க சான்றிதழ் நகல்",
                "பழைய கையெழுத்து சான்றிதழ் (தேவைப்பட்டால்)",
                "குடும்ப அட்டை மற்றும் ஆதார்"
            ],
            "official_service_portal": "https://edistricts.tn.gov.in/revenue/status.html",
            "official_service_name": "Tamil Nadu e-District Verification Portal",
            "after_correction": "Recheck the newly scanned complete PDF in QUBIX.",
            "after_correction_ta": "முழுமையான புதிய சான்றிதழை மீண்டும் பதிவேற்றம் செய்யவும்.",
            "what_to_recheck": "Ensure the 2D Barcode / QR Code, certificate number (e.g. TN-...), and issue date are clearly visible."
        }
    }
}

class GuidanceService:
    def get_all_official_services(self, category: Optional[str] = None, jurisdiction: Optional[str] = None) -> List[Dict[str, Any]]:
        services = OFFICIAL_GOVERNMENT_SERVICES
        if category:
            services = [s for s in services if s.get("category", "").lower() == category.lower()]
        if jurisdiction:
            services = [s for s in services if jurisdiction.lower() in s.get("jurisdiction", "").lower() or "all india" in s.get("jurisdiction", "").lower()]
        return services

    def get_all_correction_guides(self) -> List[Dict[str, Any]]:
        return list(CORRECTION_GUIDES.values())

    def get_correction_guide(self, guide_id: str) -> Optional[Dict[str, Any]]:
        # Check direct key
        if guide_id in CORRECTION_GUIDES:
            return CORRECTION_GUIDES[guide_id]
        
        # Fuzzy key mapping
        key_map = {
            "name": "name_mismatch",
            "mismatch": "name_mismatch",
            "aadhaar": "aadhaar_update",
            "pan": "pan_correction",
            "dl": "dl_renewal",
            "driving": "dl_renewal",
            "expired": "dl_renewal",
            "income": "income_reissue",
            "nativity": "nativity_reissue",
            "blurry": "blurry_scan",
            "unreadable": "blurry_scan",
            "seal": "missing_ref_number",
            "missing_field": "missing_ref_number",
        }
        for k, target in key_map.items():
            if k in guide_id.lower():
                return CORRECTION_GUIDES[target]

        return CORRECTION_GUIDES.get("name_mismatch")

guidance_service = GuidanceService()
