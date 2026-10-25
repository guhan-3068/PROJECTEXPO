from datetime import date, timedelta
from app.services.expiry_detector import expiry_detector
from app.models.document import UploadedDocument
from app.models.extracted_field import ExtractedField

def test_expiry_classification():
    today = date(2026, 10, 25)

    # Document 1: Expired
    doc_expired = UploadedDocument(id="d1", original_filename="old_doc.pdf", doc_category="PASSPORT")
    doc_expired.extracted_fields = [
        ExtractedField(field_key="expiry_date", raw_value="2024-01-01", normalized_value="2024-01-01")
    ]

    # Document 2: Expiring Soon (30 days from reference)
    soon_date = (today + timedelta(days=20)).isoformat()
    doc_soon = UploadedDocument(id="d2", original_filename="soon_doc.pdf", doc_category="DRIVERS_LICENSE")
    doc_soon.extracted_fields = [
        ExtractedField(field_key="expiry_date", raw_value=soon_date, normalized_value=soon_date)
    ]

    # Document 3: Valid (5 years from reference)
    future_date = (today + timedelta(days=1000)).isoformat()
    doc_valid = UploadedDocument(id="d3", original_filename="valid_doc.pdf", doc_category="PASSPORT")
    doc_valid.extracted_fields = [
        ExtractedField(field_key="expiry_date", raw_value=future_date, normalized_value=future_date)
    ]

    # Document 4: Birth Certificate (Non-expiring)
    doc_birth = UploadedDocument(id="d4", original_filename="birth_cert.pdf", doc_category="BIRTH_CERTIFICATE")
    doc_birth.extracted_fields = []

    res = expiry_detector.analyze_documents(
        [doc_expired, doc_soon, doc_valid, doc_birth],
        warning_days=60,
        reference_date=today
    )

    assert len(res["expired"]) == 1
    assert res["expired"][0]["document_id"] == "d1"
    assert res["expired"][0]["status"] == "EXPIRED"

    assert len(res["expiring_soon"]) == 1
    assert res["expiring_soon"][0]["document_id"] == "d2"
    assert res["expiring_soon"][0]["status"] == "EXPIRING_SOON"

    assert len(res["valid"]) == 2  # doc_valid + non-expiring birth certificate
