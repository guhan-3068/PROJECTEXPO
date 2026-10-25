import json
from app.services.requirement_checker import requirement_checker
from app.models.application import ChecklistRequirement
from app.models.document import UploadedDocument

def test_incomplete_application():
    req1 = ChecklistRequirement(
        requirement_code="PROOF_OF_ID",
        display_name="Proof of Identity",
        is_mandatory=True,
        accepted_categories=json.dumps(["PASSPORT", "NATIONAL_ID"])
    )
    req2 = ChecklistRequirement(
        requirement_code="PROOF_OF_ADDRESS",
        display_name="Proof of Address",
        is_mandatory=True,
        accepted_categories=json.dumps(["UTILITY_BILL", "BANK_STATEMENT"])
    )
    req3 = ChecklistRequirement(
        requirement_code="APPLICATION_FORM",
        display_name="Application Form",
        is_mandatory=True,
        accepted_categories=json.dumps(["APPLICATION_FORM"])
    )

    # User uploads only Passport and Utility Bill
    doc1 = UploadedDocument(id="doc-1", doc_category="PASSPORT", original_filename="passport.pdf")
    doc2 = UploadedDocument(id="doc-2", doc_category="UTILITY_BILL", original_filename="bill.pdf")

    res = requirement_checker.evaluate_requirements([req1, req2, req3], [doc1, doc2])

    assert res["is_complete"] is False
    assert res["has_missing_mandatory"] is True
    assert len(res["satisfied"]) == 2
    assert len(res["missing"]) == 1
    assert res["missing"][0]["requirement_code"] == "APPLICATION_FORM"
    assert len(res["recommended_actions"]) == 1
    assert "Application Form" in res["recommended_actions"][0]

def test_complete_application():
    req1 = ChecklistRequirement(
        requirement_code="PROOF_OF_ID",
        display_name="Proof of Identity",
        is_mandatory=True,
        accepted_categories=json.dumps(["PASSPORT"])
    )
    doc1 = UploadedDocument(id="doc-1", doc_category="PASSPORT", original_filename="passport.pdf")

    res = requirement_checker.evaluate_requirements([req1], [doc1])
    assert res["is_complete"] is True
    assert len(res["satisfied"]) == 1
    assert len(res["missing"]) == 0
