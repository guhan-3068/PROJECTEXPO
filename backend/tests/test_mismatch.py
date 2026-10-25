from app.services.mismatch_detector import mismatch_detector
from app.models.document import UploadedDocument
from app.models.extracted_field import ExtractedField

def test_mismatch_detection():
    # Document A
    doc_a = UploadedDocument(id="doc_a", original_filename="passport.pdf")
    doc_a.extracted_fields = [
        ExtractedField(field_key="full_name", raw_value="Johnathan M. Doe", normalized_value="Johnathan M. Doe"),
        ExtractedField(field_key="dob", raw_value="1988-12-04", normalized_value="1988-12-04")
    ]

    # Document B: Conflicting DOB and name mismatch
    doc_b = UploadedDocument(id="doc_b", original_filename="license.pdf")
    doc_b.extracted_fields = [
        ExtractedField(field_key="full_name", raw_value="Robert Doe", normalized_value="Robert Doe"),
        ExtractedField(field_key="dob", raw_value="1992-05-15", normalized_value="1992-05-15")
    ]

    mismatches = mismatch_detector.detect_mismatches([doc_a, doc_b])
    keys = [m["field_key"] for m in mismatches]

    assert "full_name" in keys
    assert "dob" in keys
    dob_mismatch = next(m for m in mismatches if m["field_key"] == "dob")
    assert dob_mismatch["requires_manual_review"] is True
