import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import ApplicationProfile, ChecklistRequirement, UserApplication
from app.models.document import UploadedDocument
from app.models.user import User
from app.schemas.application import (
    ApplicationProfileOut, UserApplicationCreate, UserApplicationOut
)
from app.routers.auth import get_current_user
from app.services.demo_service import demo_service
from app.services.storage_service import storage_service
from app.services.guidance_service import guidance_service

router = APIRouter(prefix="/applications", tags=["Applications & Checklists"])

INDIAN_CITIZEN_PROFILES = [
    {
        "code": "FIRST_GRADUATE_APPLICATION",
        "name": "First Graduate Application",
        "jurisdiction": "Tamil Nadu, India",
        "category": "Education / Fee Concession",
        "description": "Fee concession scheme for students who are the first in their immediate family to pursue a college degree.",
        "requirements": [
            {
                "requirement_code": "APPLICANT_MARK_SHEET",
                "display_name": "10th / 12th HSC Mark Sheet",
                "description": "Educational mark sheet demonstrating qualifying examination pass.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["EDUCATIONAL_CERTIFICATE"],
                "sort_order": 1
            },
            {
                "requirement_code": "TRANSFER_CERTIFICATE",
                "display_name": "School / College Transfer Certificate (TC)",
                "description": "Transfer certificate from last studied institution showing conduct & leaving date.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["TRANSFER_CERTIFICATE"],
                "sort_order": 2
            },
            {
                "requirement_code": "FAMILY_SMART_CARD",
                "display_name": "Smart Family Card / Ration Card",
                "description": "Official family card establishing parent and sibling relationships.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD"],
                "sort_order": 3
            },
            {
                "requirement_code": "IDENTITY_PROOF",
                "display_name": "Aadhaar Card / Photo Identity Proof",
                "description": "Government-issued identity proof with applicant photograph.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "NATIONAL_ID", "VOTER_ID"],
                "sort_order": 4
            },
            {
                "requirement_code": "PARENT_EDU_DECLARATION",
                "display_name": "Parent / Sibling Educational Status Declaration",
                "description": "Signed declaration or educational certificates confirming no graduate in immediate family.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["APPLICATION_FORM", "EDUCATIONAL_CERTIFICATE"],
                "sort_order": 5
            },
            {
                "requirement_code": "FIRST_GRADUATE_CERTIFICATE",
                "display_name": "First Graduate Certificate (e-Sevai / Tahsildar)",
                "description": "Certified certificate issued by Revenue Department Tahsildar.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["FIRST_GRADUATE_CERTIFICATE"],
                "sort_order": 6
            },
            {
                "requirement_code": "INCOME_CERTIFICATE",
                "display_name": "Income Certificate",
                "description": "Revenue department income certificate if applying for combined scholarship.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["INCOME_CERTIFICATE"],
                "sort_order": 7
            },
            {
                "requirement_code": "NATIVITY_PROOF",
                "display_name": "Nativity / Residence Proof",
                "description": "Nativity Certificate or residence proof for state domicile verification.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["NATIVITY_CERTIFICATE", "RESIDENCE_CERTIFICATE"],
                "sort_order": 8
            }
        ]
    },
    {
        "code": "COLLEGE_ADMISSION",
        "name": "College Admission",
        "jurisdiction": "Tamil Nadu / All India",
        "category": "Higher Education",
        "description": "Document verification for Engineering (TNEA), Medical, Arts & Science, and PG admissions.",
        "requirements": [
            {
                "requirement_code": "MARK_SHEETS",
                "display_name": "10th and 12th Mark Sheets",
                "description": "SSLC and HSC mark statements or consolidated academic transcript.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["EDUCATIONAL_CERTIFICATE"],
                "sort_order": 1
            },
            {
                "requirement_code": "TRANSFER_CERTIFICATE",
                "display_name": "Transfer Certificate (TC)",
                "description": "Official transfer certificate issued by the previous school/college.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["TRANSFER_CERTIFICATE"],
                "sort_order": 2
            },
            {
                "requirement_code": "IDENTITY_PROOF",
                "display_name": "Aadhaar Card",
                "description": "Aadhaar Card for student identification and APAAR/ABC registration.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "NATIONAL_ID"],
                "sort_order": 3
            },
            {
                "requirement_code": "COMMUNITY_CERTIFICATE",
                "display_name": "Community / Caste Certificate",
                "description": "Required if claiming reservation quota (BC, BCM, MBC, DNC, SC, SCA, ST).",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["COMMUNITY_CERTIFICATE"],
                "sort_order": 4
            },
            {
                "requirement_code": "NATIVITY_CERTIFICATE",
                "display_name": "Nativity Certificate",
                "description": "Required for candidates claiming Tamil Nadu / State domicile quota.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["NATIVITY_CERTIFICATE", "RESIDENCE_CERTIFICATE"],
                "sort_order": 5
            },
            {
                "requirement_code": "FIRST_GRADUATE_CERTIFICATE",
                "display_name": "First Graduate Certificate",
                "description": "Required for tuition fee concession under government scheme.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["FIRST_GRADUATE_CERTIFICATE"],
                "sort_order": 6
            },
            {
                "requirement_code": "INCOME_CERTIFICATE",
                "display_name": "Income Certificate",
                "description": "Required for Post-Matric scholarship or fee waiver schemes.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["INCOME_CERTIFICATE"],
                "sort_order": 7
            }
        ]
    },
    {
        "code": "SCHOOL_ADMISSION",
        "name": "School Admission",
        "jurisdiction": "All India",
        "category": "School Education",
        "description": "Documentation for primary and secondary school admissions (including RTE 25% quota).",
        "requirements": [
            {
                "requirement_code": "BIRTH_PROOF",
                "display_name": "Birth Certificate (Age Proof)",
                "description": "Municipal or Panchayat birth certificate.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BIRTH_CERTIFICATE"],
                "sort_order": 1
            },
            {
                "requirement_code": "RESIDENCE_PROOF",
                "display_name": "Address Proof / Smart Family Card",
                "description": "Smart Family Card, Aadhaar, or EB/utility bill within neighborhood.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD", "AADHAAR", "UTILITY_BILL"],
                "sort_order": 2
            },
            {
                "requirement_code": "TRANSFER_CERTIFICATE",
                "display_name": "Previous School Transfer Certificate (TC)",
                "description": "Required for admissions to classes 2nd standard and above.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["TRANSFER_CERTIFICATE"],
                "sort_order": 3
            },
            {
                "requirement_code": "COMMUNITY_CERTIFICATE",
                "display_name": "Community Certificate",
                "description": "Required for RTE disadvantaged group reservation.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["COMMUNITY_CERTIFICATE"],
                "sort_order": 4
            },
            {
                "requirement_code": "INCOME_CERTIFICATE",
                "display_name": "Income Certificate",
                "description": "Required for RTE weaker section quota (income below threshold).",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["INCOME_CERTIFICATE"],
                "sort_order": 5
            },
            {
                "requirement_code": "PARENT_ID",
                "display_name": "Parent / Guardian Photo ID",
                "description": "Aadhaar Card or Voter ID of parent/guardian.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["AADHAAR", "VOTER_ID", "PAN_CARD"],
                "sort_order": 6
            }
        ]
    },
    {
        "code": "DRIVING_LICENSE_APPLICATION",
        "name": "Driving License Application",
        "jurisdiction": "All India (MoRTH / Parivahan)",
        "category": "Transport",
        "description": "Checklist for Learner's Licence (LLR) and permanent Driving Licence at the RTO.",
        "requirements": [
            {
                "requirement_code": "AGE_PROOF",
                "display_name": "Accepted Age Proof",
                "description": "Birth Certificate, 10th Mark Sheet, or Passport.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BIRTH_CERTIFICATE", "EDUCATIONAL_CERTIFICATE", "PASSPORT"],
                "sort_order": 1
            },
            {
                "requirement_code": "IDENTITY_PROOF",
                "display_name": "Accepted Identity Proof",
                "description": "Aadhaar Card, Voter ID, or PAN Card.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "VOTER_ID", "PAN_CARD", "PASSPORT"],
                "sort_order": 2
            },
            {
                "requirement_code": "ADDRESS_PROOF",
                "display_name": "Accepted Address Proof",
                "description": "Smart Family Card, Aadhaar Card, or utility bill within RTO jurisdiction.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "RATION_CARD", "UTILITY_BILL"],
                "sort_order": 3
            },
            {
                "requirement_code": "LEARNERS_LICENSE",
                "display_name": "Learner's License (LLR)",
                "description": "Valid Learner's License held for at least 30 days before permanent driving test.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["DRIVING_LICENSE"],
                "sort_order": 4
            },
            {
                "requirement_code": "MEDICAL_CERTIFICATE",
                "display_name": "Medical Certificate (Form 1A)",
                "description": "Required for applicants over 40 years of age or transport vehicle category.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["APPLICATION_FORM", "OTHER_SUPPORTING"],
                "sort_order": 5
            }
        ]
    },
    {
        "code": "SCHOLARSHIP_APPLICATION",
        "name": "Scholarship Application",
        "jurisdiction": "All India / State Welfare",
        "category": "Financial Aid & Welfare",
        "description": "Post-Matric, National Scholarship Portal (NSP), and State Department welfare schemes.",
        "requirements": [
            {
                "requirement_code": "INCOME_CERTIFICATE",
                "display_name": "Income Certificate (Tahsildar / Revenue Dept)",
                "description": "Current valid annual income certificate issued by Tahsildar.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["INCOME_CERTIFICATE"],
                "sort_order": 1
            },
            {
                "requirement_code": "COMMUNITY_CERTIFICATE",
                "display_name": "Community / Caste Certificate",
                "description": "Required for SC/ST/OBC/Minority scholarship allocations.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["COMMUNITY_CERTIFICATE"],
                "sort_order": 2
            },
            {
                "requirement_code": "BANK_PASSBOOK",
                "display_name": "Student Bank Passbook / Account Proof",
                "description": "Bank account in student's name seeded with Aadhaar (IFSC visible).",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BANK_PASSBOOK", "BANK_STATEMENT"],
                "sort_order": 3
            },
            {
                "requirement_code": "STUDENT_AADHAAR",
                "display_name": "Student Aadhaar Card",
                "description": "Aadhaar Card for DBT (Direct Benefit Transfer) verification.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR"],
                "sort_order": 4
            },
            {
                "requirement_code": "BONAFIDE_CERTIFICATE",
                "display_name": "Bonafide Student Certificate",
                "description": "Bonafide certificate issued by college/institution for current academic year.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BONAFIDE_CERTIFICATE", "APPLICATION_FORM"],
                "sort_order": 5
            },
            {
                "requirement_code": "PREVIOUS_MARK_SHEET",
                "display_name": "Previous Examination Mark Sheet",
                "description": "10th, 12th, or semester mark statement meeting scholarship percentage criteria.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["EDUCATIONAL_CERTIFICATE"],
                "sort_order": 6
            },
            {
                "requirement_code": "SMART_RATION_CARD",
                "display_name": "Smart Family Card / Ration Card",
                "description": "Family card supporting family composition verification.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["RATION_CARD"],
                "sort_order": 7
            }
        ]
    },
    {
        "code": "GOVERNMENT_CERTIFICATE_APPLICATION",
        "name": "Government Certificate Application",
        "jurisdiction": "All India / e-Sevai",
        "category": "Revenue & Public Services",
        "description": "Citizen checklist for revenue services, certificates, and e-District verification.",
        "requirements": [
            {
                "requirement_code": "PHOTO_IDENTITY",
                "display_name": "Photo Identity Proof (Aadhaar / Voter ID / PAN)",
                "description": "Officially valid photo identification document.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "VOTER_ID", "PAN_CARD", "PASSPORT"],
                "sort_order": 1
            },
            {
                "requirement_code": "ADDRESS_PROOF",
                "display_name": "Address Proof / Smart Family Card",
                "description": "Proof of permanent residence within the administrative circle.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD", "UTILITY_BILL", "AADHAAR"],
                "sort_order": 2
            },
            {
                "requirement_code": "APPLICATION_FORM",
                "display_name": "Self-Declaration / Application Form",
                "description": "Signed citizen declaration format specified by revenue authority.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["APPLICATION_FORM"],
                "sort_order": 3
            },
            {
                "requirement_code": "SUPPORTING_PROOF",
                "display_name": "Supporting Affidavit / Institution Letter",
                "description": "Additional supporting document relevant to the specific certificate requested.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["OTHER_SUPPORTING", "BONAFIDE_CERTIFICATE"],
                "sort_order": 4
            }
        ]
    },
    {
        "code": "INCOME_CERTIFICATE_APPLICATION",
        "name": "Income Certificate Application",
        "jurisdiction": "Tamil Nadu / All India",
        "category": "Revenue Department",
        "description": "Application to obtain an official Tahsildar Income Certificate for fee concessions & welfare schemes.",
        "requirements": [
            {
                "requirement_code": "FAMILY_SMART_CARD",
                "display_name": "Smart Family Card / Ration Card",
                "description": "Family card establishing all earning and dependent members.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD"],
                "sort_order": 1
            },
            {
                "requirement_code": "APPLICANT_AADHAAR",
                "display_name": "Aadhaar Card of Applicant",
                "description": "Aadhaar Card of applicant or family head.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR"],
                "sort_order": 2
            },
            {
                "requirement_code": "SALARY_SLIP_OR_ITR",
                "display_name": "Salary Slip / Employer Certificate / Form 16",
                "description": "Required if any family member is employed in government or organized private sector.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["BANK_STATEMENT", "OTHER_SUPPORTING"],
                "sort_order": 3
            },
            {
                "requirement_code": "SELF_DECLARATION",
                "display_name": "Income Self-Declaration Form",
                "description": "Declaration of annual family income from all sources.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["APPLICATION_FORM"],
                "sort_order": 4
            },
            {
                "requirement_code": "BANK_STATEMENT",
                "display_name": "Bank Passbook / Bank Statement",
                "description": "Passbook copy showing financial transaction history.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["BANK_PASSBOOK", "BANK_STATEMENT"],
                "sort_order": 5
            }
        ]
    },
    {
        "code": "NATIVITY_CERTIFICATE_APPLICATION",
        "name": "Nativity Certificate Application",
        "jurisdiction": "Tamil Nadu / State Revenue",
        "category": "Revenue Department",
        "description": "Application for permanent residence & nativity status for state admissions & government recruitment.",
        "requirements": [
            {
                "requirement_code": "BIRTH_CERTIFICATE",
                "display_name": "Birth Certificate of Applicant",
                "description": "Proof of place of birth within the state.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BIRTH_CERTIFICATE"],
                "sort_order": 1
            },
            {
                "requirement_code": "SCHOOL_TC",
                "display_name": "School Transfer Certificate (TC)",
                "description": "Proof of continuous schooling within Tamil Nadu / the state.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["TRANSFER_CERTIFICATE"],
                "sort_order": 2
            },
            {
                "requirement_code": "SMART_RATION_CARD",
                "display_name": "Smart Family Card / Ration Card",
                "description": "Proof of family residence in the respective taluk/district.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD"],
                "sort_order": 3
            },
            {
                "requirement_code": "PARENT_CERTIFICATE",
                "display_name": "Parent's Nativity / Community Certificate",
                "description": "Supporting parental domicile document if applicant was born outside state.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["NATIVITY_CERTIFICATE", "COMMUNITY_CERTIFICATE"],
                "sort_order": 4
            },
            {
                "requirement_code": "PROPERTY_OR_EB_BILL",
                "display_name": "Property Tax / Electricity (EB) Bill",
                "description": "Electricity bill or property tax receipt for continuous residence proof.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["UTILITY_BILL", "AADHAAR"],
                "sort_order": 5
            }
        ]
    },
    {
        "code": "PAN_CARD_APPLICATION",
        "name": "PAN Card Application",
        "jurisdiction": "All India (Income Tax Dept / NSDL)",
        "category": "Taxation & Identity",
        "description": "Document checklist for Form 49A (New PAN card application or data correction).",
        "requirements": [
            {
                "requirement_code": "IDENTITY_PROOF",
                "display_name": "Proof of Identity (POI)",
                "description": "Aadhaar Card, Passport, or Voter ID.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "PASSPORT", "VOTER_ID", "DRIVING_LICENSE"],
                "sort_order": 1
            },
            {
                "requirement_code": "ADDRESS_PROOF",
                "display_name": "Proof of Address (POA)",
                "description": "Aadhaar Card, Smart Family Card, Bank Statement, or Utility Bill.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "RATION_CARD", "BANK_STATEMENT", "UTILITY_BILL"],
                "sort_order": 2
            },
            {
                "requirement_code": "DOB_PROOF",
                "display_name": "Proof of Date of Birth (DOB)",
                "description": "Birth Certificate, 10th Mark Sheet, or Passport.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BIRTH_CERTIFICATE", "EDUCATIONAL_CERTIFICATE", "PASSPORT", "AADHAAR"],
                "sort_order": 3
            },
            {
                "requirement_code": "FORM_49A_DECLARATION",
                "display_name": "Signed Form 49A Declaration",
                "description": "Form 49A declaration with applicant signatures.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["APPLICATION_FORM"],
                "sort_order": 4
            }
        ]
    },
    {
        "code": "AADHAAR_SERVICES",
        "name": "Aadhaar-Related Services",
        "jurisdiction": "All India (UIDAI)",
        "category": "UIDAI Citizen Services",
        "description": "Document verification for new Aadhaar enrolment, address update, or demographic correction.",
        "requirements": [
            {
                "requirement_code": "PROOF_OF_IDENTITY",
                "display_name": "Proof of Identity (POI)",
                "description": "PAN Card, Passport, Voter ID, or photo Ration Card.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["PAN_CARD", "PASSPORT", "VOTER_ID", "RATION_CARD", "DRIVING_LICENSE"],
                "sort_order": 1
            },
            {
                "requirement_code": "PROOF_OF_ADDRESS",
                "display_name": "Proof of Address (POA)",
                "description": "Smart Family Card, Bank Passbook, or Utility Bill.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD", "BANK_PASSBOOK", "BANK_STATEMENT", "UTILITY_BILL"],
                "sort_order": 2
            },
            {
                "requirement_code": "PROOF_OF_DOB",
                "display_name": "Proof of Date of Birth (PDB)",
                "description": "Birth Certificate or SSLC Mark Sheet (for DOB correction).",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["BIRTH_CERTIFICATE", "EDUCATIONAL_CERTIFICATE", "PASSPORT"],
                "sort_order": 3
            },
            {
                "requirement_code": "PROOF_OF_RELATIONSHIP",
                "display_name": "Proof of Relationship (POR)",
                "description": "Smart Family Card or Birth Certificate (for child enrolment).",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["RATION_CARD", "BIRTH_CERTIFICATE"],
                "sort_order": 4
            }
        ]
    },
    {
        "code": "NGO_REGISTRATION",
        "name": "NGO Registration / NGO Assistance",
        "jurisdiction": "All India (Societies / Trusts / NITI Aayog)",
        "category": "Non-Profit & Social Welfare",
        "description": "Documentation for Trust Deed, Society Registration, Section 8, and NITI Aayog Darpan portal.",
        "requirements": [
            {
                "requirement_code": "CONSTITUTION_DOC",
                "display_name": "Trust Deed / Society Bye-Laws / MOA",
                "description": "Registered deed or memorandum of association of the organization.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["APPLICATION_FORM", "OTHER_SUPPORTING"],
                "sort_order": 1
            },
            {
                "requirement_code": "ENTITY_PAN",
                "display_name": "PAN Card of the NGO / Trustees",
                "description": "Permanent Account Number of trust/society or authorized office bearers.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["PAN_CARD"],
                "sort_order": 2
            },
            {
                "requirement_code": "OFFICE_BEARER_ID",
                "display_name": "Identity Proof of Trustees / Office Bearers",
                "description": "Aadhaar Card or Voter ID of managing trustees and secretary.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "VOTER_ID", "PASSPORT"],
                "sort_order": 3
            },
            {
                "requirement_code": "REGISTERED_OFFICE_ADDRESS",
                "display_name": "Registered Office Address Proof",
                "description": "Electricity bill, property tax receipt, or registered rent agreement.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["UTILITY_BILL", "BANK_STATEMENT"],
                "sort_order": 4
            },
            {
                "requirement_code": "BANK_ACCOUNT_PROOF",
                "display_name": "Bank Account Proof / Cancelled Cheque",
                "description": "Account details in the name of the organization.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["BANK_PASSBOOK", "BANK_STATEMENT"],
                "sort_order": 5
            },
            {
                "requirement_code": "GOVERNING_BODY_LIST",
                "display_name": "List of Governing Body Members",
                "description": "Signed list of office bearers with designations.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["APPLICATION_FORM"],
                "sort_order": 6
            }
        ]
    },
    {
        "code": "JOB_APPLICATION",
        "name": "Job Application",
        "jurisdiction": "All India (Public & Private Sector)",
        "category": "Employment",
        "description": "Candidate document readiness check for state public service, banking, and corporate recruitment.",
        "requirements": [
            {
                "requirement_code": "ACADEMIC_CERTIFICATES",
                "display_name": "Degree / Consolidated Academic Mark Sheet",
                "description": "Graduation degree certificate or 10th/12th/diploma mark sheets.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["EDUCATIONAL_CERTIFICATE"],
                "sort_order": 1
            },
            {
                "requirement_code": "IDENTITY_PROOF",
                "display_name": "Aadhaar Card / National Identity Proof",
                "description": "Aadhaar Card for identity check and background verification.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "PASSPORT", "VOTER_ID"],
                "sort_order": 2
            },
            {
                "requirement_code": "PAN_CARD",
                "display_name": "PAN Card",
                "description": "Mandatory for payroll processing and income tax deduction.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["PAN_CARD"],
                "sort_order": 3
            },
            {
                "requirement_code": "RELIEVING_LETTER",
                "display_name": "Relieving Letter / Service Certificate",
                "description": "Service certificate from previous employer for experienced hires.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["OTHER_SUPPORTING"],
                "sort_order": 4
            },
            {
                "requirement_code": "BANK_ACCOUNT_PROOF",
                "display_name": "Bank Passbook / Cancelled Cheque",
                "description": "Bank account proof for salary direct deposit.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["BANK_PASSBOOK", "BANK_STATEMENT"],
                "sort_order": 5
            },
            {
                "requirement_code": "COMMUNITY_CERTIFICATE",
                "display_name": "Community Certificate",
                "description": "Required for reserved category government recruitment.",
                "is_mandatory": False,
                "requirement_type": "CONDITIONALLY_REQUIRED",
                "accepted_categories": ["COMMUNITY_CERTIFICATE"],
                "sort_order": 6
            }
        ]
    },
    {
        "code": "BANK_ACCOUNT_OPENING",
        "name": "Bank Account Opening",
        "jurisdiction": "All India (RBI KYC Norms)",
        "category": "Banking & Financial Services",
        "description": "Simplified KYC verification for opening Savings, Current, or PM Jan Dhan accounts.",
        "requirements": [
            {
                "requirement_code": "OVD_IDENTITY",
                "display_name": "Officially Valid Document (Aadhaar / Passport / Voter ID)",
                "description": "Officially Valid Document (OVD) for identity under RBI KYC master direction.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "PASSPORT", "VOTER_ID", "DRIVING_LICENSE"],
                "sort_order": 1
            },
            {
                "requirement_code": "PAN_CARD",
                "display_name": "Permanent Account Number (PAN) Card / Form 60",
                "description": "PAN card or Form 60 declaration if PAN is not yet allotted.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["PAN_CARD", "APPLICATION_FORM"],
                "sort_order": 2
            },
            {
                "requirement_code": "ADDRESS_PROOF",
                "display_name": "Proof of Residential Address",
                "description": "Smart Family Card, Aadhaar, or Utility Bill matching current address.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD", "UTILITY_BILL", "AADHAAR"],
                "sort_order": 3
            },
            {
                "requirement_code": "PHOTOGRAPH_AND_FORM",
                "display_name": "Account Opening Form / Photographs",
                "description": "Signed bank account opening application declaration.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["APPLICATION_FORM"],
                "sort_order": 4
            }
        ]
    },
    {
        "code": "OTHER_APPLICATIONS",
        "name": "Other Applications",
        "jurisdiction": "All India / Custom",
        "category": "General Document Verification",
        "description": "General multi-document audit, expiration scan, and cross-document identity alignment.",
        "requirements": [
            {
                "requirement_code": "PRIMARY_ID",
                "display_name": "Primary Photo Identification",
                "description": "Aadhaar, PAN Card, Passport, Voter ID, or Driving License.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["AADHAAR", "PAN_CARD", "PASSPORT", "VOTER_ID", "DRIVING_LICENSE"],
                "sort_order": 1
            },
            {
                "requirement_code": "RESIDENCE_PROOF",
                "display_name": "Proof of Address / Residence",
                "description": "Smart Family Card, Utility Bill, or Bank Statement.",
                "is_mandatory": True,
                "requirement_type": "REQUIRED",
                "accepted_categories": ["RATION_CARD", "UTILITY_BILL", "BANK_STATEMENT", "AADHAAR"],
                "sort_order": 2
            },
            {
                "requirement_code": "ACADEMIC_OR_DOB_PROOF",
                "display_name": "Date of Birth or Academic Proof",
                "description": "Birth Certificate, 10th Mark Sheet, or Transfer Certificate.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["BIRTH_CERTIFICATE", "EDUCATIONAL_CERTIFICATE", "TRANSFER_CERTIFICATE"],
                "sort_order": 3
            },
            {
                "requirement_code": "APPLICATION_FORM",
                "display_name": "Supporting Application Form / Affidavit",
                "description": "Service declaration form or supporting affidavit.",
                "is_mandatory": False,
                "requirement_type": "OPTIONAL",
                "accepted_categories": ["APPLICATION_FORM", "OTHER_SUPPORTING"],
                "sort_order": 4
            }
        ]
    }
]

def sync_all_profiles(db: Session):
    """
    Ensures all 14 Indian citizen application categories and their checklists
    are registered in the database.
    """
    for p_data in INDIAN_CITIZEN_PROFILES:
        profile = db.query(ApplicationProfile).filter(ApplicationProfile.code == p_data["code"]).first()
        reqs = p_data.get("requirements", [])

        if not profile:
            profile = ApplicationProfile(
                code=p_data["code"],
                name=p_data["name"],
                jurisdiction=p_data["jurisdiction"],
                category=p_data["category"],
                description=p_data.get("description"),
                is_active=True
            )
            db.add(profile)
            db.flush()

            for r in reqs:
                req_obj = ChecklistRequirement(
                    application_profile_id=profile.id,
                    requirement_code=r["requirement_code"],
                    display_name=r["display_name"],
                    description=r.get("description"),
                    is_mandatory=r.get("is_mandatory", True),
                    requirement_type=r.get("requirement_type", "REQUIRED" if r.get("is_mandatory", True) else "OPTIONAL"),
                    accepted_categories=json.dumps(r.get("accepted_categories", [])),
                    sort_order=r.get("sort_order", 0)
                )
                db.add(req_obj)
        else:
            # Profile exists; ensure requirements match
            existing_codes = {r.requirement_code for r in profile.requirements}
            for r in reqs:
                if r["requirement_code"] not in existing_codes:
                    req_obj = ChecklistRequirement(
                        application_profile_id=profile.id,
                        requirement_code=r["requirement_code"],
                        display_name=r["display_name"],
                        description=r.get("description"),
                        is_mandatory=r.get("is_mandatory", True),
                        requirement_type=r.get("requirement_type", "REQUIRED" if r.get("is_mandatory", True) else "OPTIONAL"),
                        accepted_categories=json.dumps(r.get("accepted_categories", [])),
                        sort_order=r.get("sort_order", 0)
                    )
                    db.add(req_obj)
                else:
                    # Sync requirement_type on existing requirement
                    for er in profile.requirements:
                        if er.requirement_code == r["requirement_code"]:
                            er.requirement_type = r.get("requirement_type", "REQUIRED" if er.is_mandatory else "OPTIONAL")

    db.commit()

def seed_profiles_if_empty(db: Session):
    sync_all_profiles(db)

@router.get("/profiles", response_model=List[ApplicationProfileOut])
def list_application_profiles(db: Session = Depends(get_db)):
    sync_all_profiles(db)
    # Order so Indian profiles are displayed first
    profiles = db.query(ApplicationProfile).filter(ApplicationProfile.is_active == True).all()
    # Sort: put Indian profiles at the top
    indian_codes = [p["code"] for p in INDIAN_CITIZEN_PROFILES]
    sorted_profiles = sorted(
        profiles,
        key=lambda p: (0 if p.code in indian_codes else 1, indian_codes.index(p.code) if p.code in indian_codes else p.name)
    )
    return sorted_profiles

@router.post("/start", response_model=UserApplicationOut, status_code=status.HTTP_201_CREATED)
def start_application(
    payload: UserApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not payload.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Citizen consent is mandatory before processing uploaded documents."
        )

    profile = db.query(ApplicationProfile).filter(ApplicationProfile.id == payload.application_profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified application category not found"
        )

    ref_num = f"IND-{datetime.now(timezone.utc).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    app = UserApplication(
        user_id=current_user.id,
        application_profile_id=profile.id,
        reference_number=ref_num,
        status="DRAFT",
        readiness_status="Action Required",
        state=payload.state or "Tamil Nadu",
        district=payload.district or "Chennai",
        issuing_authority=payload.issuing_authority or profile.jurisdiction,
        consent_given=True,
        consent_timestamp=datetime.now(timezone.utc)
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@router.get("/my", response_model=List[UserApplicationOut])
def get_user_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(UserApplication).filter(UserApplication.user_id == current_user.id).order_by(UserApplication.created_at.desc()).all()
    return apps

@router.get("/demo/scenarios")
def get_demo_scenarios():
    """Returns the 7 pre-configured Indian citizen demo verification test cases."""
    return demo_service.get_all_demo_scenarios()

@router.post("/demo/load/{scenario_id}", response_model=UserApplicationOut)
def load_demo_scenario_endpoint(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates an application, attaches sample demo documents for the scenario,
    runs verification, and produces an audit report for test driving.
    """
    sync_all_profiles(db)
    app = demo_service.load_demo_scenario(scenario_id, current_user, db)
    return app

@router.get("/demo/sample-file/{doc_key}")
def download_sample_demo_file(doc_key: str):
    """
    Allows citizens to download individual synthetic sample PDF files
    to test the upload and OCR flow themselves.
    """
    mapping = {
        "aadhaar": demo_service.get_aadhaar_sample,
        "pan": demo_service.get_pan_sample,
        "ration_card": demo_service.get_ration_card_sample,
        "nativity": demo_service.get_nativity_sample,
        "income_valid": demo_service.get_income_cert_valid,
        "income_expired": demo_service.get_income_cert_expired,
        "first_graduate": demo_service.get_first_graduate_sample,
        "mark_sheet": demo_service.get_mark_sheet_sample,
        "transfer_cert": demo_service.get_transfer_cert_sample,
        "driving_license": demo_service.get_driving_license_sample,
        "bank_passbook": demo_service.get_bank_passbook_sample,
        "blurry": demo_service.get_blurry_sample,
    }
    generator_fn = mapping.get(doc_key.lower())
    if not generator_fn:
        raise HTTPException(status_code=404, detail="Requested sample document not found")

    file_path = generator_fn()
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
        headers={"Content-Disposition": f'attachment; filename="{file_path.name}"'}
    )

@router.get("/official-services/list")
def get_official_services(
    category: Optional[str] = None,
    jurisdiction: Optional[str] = None
):
    """
    Returns curated list of verified official government portal domains
    (Aadhaar, PAN, Parivahan, DigiLocker, e-Sevai, Scholarships, etc.)
    with capability flags and safety advisories.
    """
    return guidance_service.get_all_official_services(category=category, jurisdiction=jurisdiction)

@router.get("/correction-guides/list")
def get_correction_guides():
    """
    Returns the comprehensive library of issue correction guides
    covering step-by-step procedures, authorized authorities, required documents,
    official service links, and Tamil explanations.
    """
    return guidance_service.get_all_correction_guides()

@router.get("/correction-guides/{guide_id}")
def get_correction_guide_by_id(guide_id: str):
    """
    Returns the specific correction guide for a detected issue (name mismatch,
    Aadhaar error, PAN issue, DL renewal, Income cert, blurry scan, etc.).
    """
    guide = guidance_service.get_correction_guide(guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Correction guide not found")
    return guide

@router.get("/{application_id}", response_model=UserApplicationOut)
def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(UserApplication).filter(UserApplication.id == application_id)
    if current_user.role.upper() != "ADMIN":
        query = query.filter(UserApplication.user_id == current_user.id)
    app = query.first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes an application and cleans up encrypted stored documents from disk (Privacy & Data Retention).
    """
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == application_id).all()
    for d in docs:
        try:
            storage_service.delete_document(d.file_path)
        except Exception:
            pass

    db.delete(app)
    db.commit()
    return None
