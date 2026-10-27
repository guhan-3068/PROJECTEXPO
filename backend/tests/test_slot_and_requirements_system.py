import pytest
from app.services.document_verifier import document_verifier
from app.utils.security import mask_aadhaar_number, mask_pan_number, mask_sensitive_value
from app.services.tampering_detector import tampering_detector
from app.services.citizen_profiles_data import INDIAN_CITIZEN_PROFILES_ENRICHED

class DummyField:
    def __init__(self, key, val):
        self.field_key = key
        self.effective_value = val

class DummyTamper:
    def __init__(self, flagged=False, risk="LOW", auth="No obvious manipulation detected"):
        self.is_flagged = flagged
        self.risk_level = risk
        self.authenticity_result = auth
        self.ai_generation_screening = "No synthetic generative signatures identified"
        self.digital_signature_status = "No digital signature"
        self.ela_anomaly_score = 4.2
        self.explanation = "Format normal"

class DummyDoc:
    def __init__(self, cat="AADHAAR", filename="my_aadhaar.jpg", conf=0.92, flagged=False):
        self.id = "doc-uuid-1"
        self.original_filename = filename
        self.file_size_bytes = 102400
        self.mime_type = "image/jpeg"
        self.doc_category = cat
        self.user_assigned_category = cat
        self.ocr_overall_confidence = conf
        self.extracted_fields = [
            DummyField("name", "Muthu Kumar"),
            DummyField("aadhaar_number", "987654321098"),
            DummyField("dob", "15/08/1995")
        ]
        self.tampering_analysis = DummyTamper(flagged=flagged)

def test_six_dimensions_evaluation():
    doc = DummyDoc(cat="AADHAAR", conf=0.92, flagged=False)
    eval_res = document_verifier.evaluate_document(doc)

    assert "dimensions" in eval_res
    dims = eval_res["dimensions"]

    # 1. Type detection
    assert dims["type_detection"]["status"] == "PASS"
    assert dims["type_detection"]["identified_type"] == "Aadhaar"

    # 2. Fields extraction with privacy masking
    assert dims["fields_extraction"]["status"] == "PASS"
    masked = dims["fields_extraction"]["masked_fields"]
    assert masked["aadhaar_number"] == "XXXX-XXXX-1098"

    # 3. Validity & Expiry
    assert dims["validity_expiry"]["status"] == "PASS"
    assert "Permanent" in dims["validity_expiry"]["label"]

    # 4. Readability
    assert dims["readability_quality"]["status"] == "PASS"
    assert "High Resolution" in dims["readability_quality"]["label"]

    # 5. Authenticity Screening
    assert dims["authenticity_screening"]["status"] == "PASS"
    assert dims["authenticity_screening"]["result"] in [
        "No obvious manipulation detected",
        "Potential manipulation detected",
        "Inconclusive — further verification required"
    ]

    # 6. Official Verification Readiness
    assert dims["official_readiness"]["status"] == "READY"
    assert eval_res["rules_version"] == "2026.4"

def test_privacy_masking_rules():
    assert mask_aadhaar_number("123456789012") == "XXXX-XXXX-9012"
    assert mask_pan_number("ABCDE1234F") == "AB***4F"
    assert mask_sensitive_value("phone", "9876543210") == "XXXXXX3210"

def test_enriched_profiles_have_full_metadata():
    assert len(INDIAN_CITIZEN_PROFILES_ENRICHED) == 14
    for p in INDIAN_CITIZEN_PROFILES_ENRICHED:
        assert p.get("official_source_url") is not None
        assert p.get("status") == "Current"
        assert len(p.get("requirements", [])) >= 4
        for r in p["requirements"]:
            assert "alternative_documents" in r
            assert "validity_rules" in r
            assert "accepted_formats" in r
            assert "official_source_url" in r
