import os
import pytest
from pathlib import Path
from app.services.field_extractor import field_extractor, mask_sensitive_value
from app.services.expiry_detector import expiry_detector, NON_EXPIRING_CATEGORIES
from app.services.requirement_checker import requirement_checker
from app.services.demo_service import demo_service
from app.services.report_generator import report_generator
from app.models.application import ChecklistRequirement
from app.models.document import UploadedDocument
from app.routers.applications import INDIAN_CITIZEN_PROFILES

def test_indian_document_classification():
    # 1. Aadhaar
    aadhaar_sample = "GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA Mera Aadhaar 9482 1048 4921"
    cat, conf = field_extractor.classify_document(aadhaar_sample)
    assert cat == "AADHAAR"
    assert conf >= 0.8

    # 2. PAN Card
    pan_sample = "INCOME TAX DEPARTMENT GOVT OF INDIA PERMANENT ACCOUNT NUMBER CARD ABCDE1234F"
    cat, conf = field_extractor.classify_document(pan_sample)
    assert cat == "PAN_CARD"
    assert conf >= 0.70

    # 3. Smart Family Card / Ration Card
    ration_sample = "TAMIL NADU CIVIL SUPPLIES AND CONSUMER PROTECTION SMART FAMILY CARD TNEPDS Card No 02/G/0192834"
    cat, conf = field_extractor.classify_document(ration_sample)
    assert cat == "RATION_CARD"
    assert conf >= 0.8

    # 4. First Graduate Certificate
    fg_sample = "GOVERNMENT OF TAMIL NADU HIGHER EDUCATION FIRST GRADUATE CERTIFICATE No graduate in family"
    cat, conf = field_extractor.classify_document(fg_sample)
    assert cat == "FIRST_GRADUATE_CERTIFICATE"

    # 5. Income Certificate
    inc_sample = "GOVERNMENT OF TAMIL NADU REVENUE DEPARTMENT INCOME CERTIFICATE Tahsildar Annual Income Rs. 72000"
    cat, conf = field_extractor.classify_document(inc_sample)
    assert cat == "INCOME_CERTIFICATE"

def test_sensitive_value_masking():
    # Aadhaar masking
    assert mask_sensitive_value("aadhaar", "9482 1048 4921") == "XXXX-XXXX-4921"
    assert mask_sensitive_value("doc_number", "948210484921") == "XXXX-XXXX-4921"

    # PAN masking
    assert mask_sensitive_value("doc_number", "ABCDE1234F") == "AB***4F"

    # Bank Account masking
    assert mask_sensitive_value("bank_account", "928410498192") == "******8192"

def test_indian_non_expiring_categories():
    assert "AADHAAR" in NON_EXPIRING_CATEGORIES
    assert "PAN_CARD" in NON_EXPIRING_CATEGORIES
    assert "COMMUNITY_CERTIFICATE" in NON_EXPIRING_CATEGORIES
    assert "FIRST_GRADUATE_CERTIFICATE" in NON_EXPIRING_CATEGORIES
    assert "TRANSFER_CERTIFICATE" in NON_EXPIRING_CATEGORIES
    assert "EDUCATIONAL_CERTIFICATE" in NON_EXPIRING_CATEGORIES
    assert "RATION_CARD" in NON_EXPIRING_CATEGORIES

def test_all_14_indian_profiles_configured():
    assert len(INDIAN_CITIZEN_PROFILES) >= 14
    expected_codes = [
        "FIRST_GRADUATE_APPLICATION",
        "COLLEGE_ADMISSION",
        "SCHOOL_ADMISSION",
        "DRIVING_LICENSE_APPLICATION",
        "SCHOLARSHIP_APPLICATION",
        "GOVERNMENT_CERTIFICATE_APPLICATION",
        "INCOME_CERTIFICATE_APPLICATION",
        "NATIVITY_CERTIFICATE_APPLICATION",
        "PAN_CARD_APPLICATION",
        "AADHAAR_SERVICES",
        "NGO_REGISTRATION",
        "JOB_APPLICATION",
        "BANK_ACCOUNT_OPENING",
        "OTHER_APPLICATIONS"
    ]
    configured_codes = [p["code"] for p in INDIAN_CITIZEN_PROFILES]
    for code in expected_codes:
        assert code in configured_codes, f"Missing profile code {code}"

def test_report_generation_valid_pdf():
    pdf_path = report_generator.generate_pdf_report(
        application_ref="TEST-REF-9999",
        profile_name="First Graduate Application",
        jurisdiction="Tamil Nadu, India",
        applicant_name="Aarav S. Kumar",
        overall_status="COMPLETE",
        satisfied_items=[
            {
                "display_name": "Aadhaar Card",
                "requirement_type": "REQUIRED",
                "is_mandatory": True,
                "reason": "Satisfied by sample_aadhaar.pdf (AADHAAR)"
            }
        ],
        missing_items=[],
        expired_docs=[],
        expiring_soon_docs=[],
        mismatches=[],
        tampering_flags=[],
        recommended_actions=["All required documents present."],
        uploaded_documents_summary=[
            {
                "filename": "sample_aadhaar.pdf",
                "category": "AADHAAR",
                "confidence": 95,
                "extracted_text": "Name: Aarav S. Kumar, Aadhaar: XXXX-XXXX-4921"
            }
        ]
    )
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
