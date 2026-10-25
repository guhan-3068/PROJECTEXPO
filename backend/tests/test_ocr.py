from app.services.field_extractor import field_extractor
from app.utils.dates import parse_date_string

def test_document_classification():
    passport_sample = "REPUBLIC OF VERIFICATION PASSPORT Type: P Nationality: Global Issuing Authority"
    cat, conf = field_extractor.classify_document(passport_sample)
    assert cat == "PASSPORT"
    assert conf > 0.5

    utility_sample = "METROPOLITAN ELECTRIC AND WATER UTILITY BILL Meter No 992 Consumer Account"
    cat2, conf2 = field_extractor.classify_document(utility_sample)
    assert cat2 == "UTILITY_BILL"

def test_field_extraction_rules():
    raw_ocr = (
        "PASSPORT AGENCY\n"
        "Full Name: Johnathan Doe\n"
        "Date of Birth: 1988-12-04\n"
        "Passport Number: P8912441\n"
        "Date of Issue: 2018-05-10\n"
        "Date of Expiry: 2028-05-10\n"
    )
    fields = field_extractor.extract_fields(raw_ocr)
    f_map = {f["field_key"]: f["normalized_value"] for f in fields}

    assert f_map.get("full_name") == "Johnathan Doe"
    assert f_map.get("dob") == "1988-12-04"
    assert f_map.get("doc_number") == "P8912441"
    assert f_map.get("expiry_date") == "2028-05-10"
    assert f_map.get("issue_date") == "2018-05-10"

def test_zero_date_hallucination():
    text_without_dates = "This is a letter confirming employment at TechCorp. Signed, Manager."
    fields = field_extractor.extract_fields(text_without_dates)
    f_map = {f["field_key"]: f for f in fields}
    assert "expiry_date" not in f_map
    assert "dob" not in f_map
