import pytest
import uuid
from datetime import datetime, timezone
import json
from app.database import SessionLocal
from app.models.document import UploadedDocument
from app.models.extracted_field import ExtractedField
from app.models.tampering import TamperingAnalysis
from app.models.application import ApplicationProfile, ChecklistRequirement, UserApplication
from app.models.document_timeline import DocumentTimelineRecord
from app.models.user import User
from app.services.confidence_meter_service import confidence_meter_service
from app.services.rule_radar_service import rule_radar_service
from app.services.timeline_service import timeline_service

def test_rule_change_radar_verified_vs_unverified():
    """Test 1 & 2: Regulatory update tracking, verified official sources, and unverified notice isolation."""
    db = SessionLocal()
    try:
        rule_radar_service.seed_initial_records(db)
        
        # 1. Check verified official updates
        verified_updates = rule_radar_service.get_updates(db, only_verified=True)
        assert len(verified_updates) >= 4
        for u in verified_updates:
            assert u["is_verified"] is True
            assert u["status"] in ["New Official Update", "Requirement Changed", "No Confirmed Change"]
            assert "gov" in u["official_source_url"] or "nic" in u["official_source_url"] or "tneaonline" in u["official_source_url"]

        # 2. Check unverified record (must NOT be marked official)
        unverified = rule_radar_service.get_updates(db, status="Verification Required")
        assert len(unverified) >= 1
        unverified_rec = unverified[0]
        assert unverified_rec["is_verified"] is False
        assert "UNVERIFIED" in unverified_rec["impact_summary"]
        assert unverified_rec["status"] == "Verification Required"
    finally:
        db.close()

def test_rule_change_radar_diff_comparison():
    """Test 1 continued: Requirement version diffing highlighting modified/added rules."""
    db = SessionLocal()
    try:
        rule_radar_service.seed_initial_records(db)
        
        diff = rule_radar_service.compare_requirements("FIRST_GRADUATE_APPLICATION", db)
        assert "profile_name" in diff
        assert diff["has_changes"] is True
        assert len(diff["modified_requirements"]) > 0
        mod = diff["modified_requirements"][0]
        assert "FIRST_GRADUATE_CERTIFICATE" in mod["requirement_code"]
        assert "G.O. (Ms) No. 24" in mod["authority"]
        assert len(diff["unchanged_requirements"]) > 0
    finally:
        db.close()

def test_document_timeline_lifecycles():
    """Test 3 & 4: Valid expiry tracking, non-expiring lifetime categories, and Validity Needs Confirmation."""
    # 1. Non-expiring document (Aadhaar, Community Cert)
    st1, expl1, days1 = timeline_service._determine_validity_status("COMMUNITY_CERTIFICATE", None, "2020-05-10")
    assert st1 == "NO_EXPIRY"
    assert "lifetime validity" in expl1.lower()
    assert days1 is None

    # 2. Document with valid future expiry
    future_date = "2028-12-31"
    st2, expl2, days2 = timeline_service._determine_validity_status("DRIVING_LICENSE", future_date, "2020-01-01")
    assert st2 == "ACTIVE"
    assert days2 > 0

    # 3. Document expired
    past_date = "2023-01-01"
    st3, expl3, days3 = timeline_service._determine_validity_status("DRIVING_LICENSE", past_date, "2018-01-01")
    assert st3 == "EXPIRED"
    assert days3 < 0
    assert "expired" in expl3.lower()

    # 4. Unknown category where validity cannot be confirmed
    st4, expl4, days4 = timeline_service._determine_validity_status("MISCELLANEOUS_AFFIDAVIT", None, None)
    assert st4 == "VALIDITY_NEEDS_CONFIRMATION"
    assert "Validity Needs Confirmation" in expl4

def test_confidence_meter_six_dimensions_and_authenticity():
    """Test 6, 7 & 8: Explainable confidence across 6 dimensions, deductions, and mandatory authenticity warning."""
    # Create mock document with high OCR confidence
    doc = UploadedDocument(
        id="test-doc-123",
        original_filename="Aadhaar_Card_Sharp.pdf",
        doc_category="AADHAAR",
        user_assigned_category="AADHAAR",
        file_size_bytes=85000,
        ocr_overall_confidence=0.96,
        raw_text="GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA Aarav Suresh DOB: 14/05/1998 Male 1234 5678 9012"
    )

    fields = [
        ExtractedField(field_key="full_name", raw_value="Aarav Suresh", normalized_value="Aarav Suresh", confidence=0.98),
        ExtractedField(field_key="doc_number", raw_value="XXXX-XXXX-9012", normalized_value="XXXX-XXXX-9012", confidence=0.99),
        ExtractedField(field_key="dob", raw_value="14/05/1998", normalized_value="1998-05-14", confidence=0.95),
        ExtractedField(field_key="gender", raw_value="Male", normalized_value="Male", confidence=0.95)
    ]

    res = confidence_meter_service.calculate_document_confidence(
        doc=doc,
        extracted_fields=fields,
        mismatches=[],
        total_application_docs=1
    )

    dims = res["dimensions"]
    # Check 6 dimensions exist
    assert "type_detection" in dims
    assert "ocr_extraction" in dims
    assert "field_completeness" in dims
    assert "cross_consistency" in dims
    assert "readability" in dims
    assert "official_authenticity" in dims

    # Verify high OCR confidence
    assert dims["ocr_extraction"]["score"] >= 80.0
    assert dims["ocr_extraction"]["level"] == "High Confidence"

    # Verify 100% completeness for Aadhaar
    assert dims["field_completeness"]["score"] == 100.0

    # Verify Single document consistency is "Unable to Determine"
    assert dims["cross_consistency"]["level"] == "Unable to Determine"

    # MANDATORY WARNING CHECK: High OCR does NOT mean official authenticity!
    auth = dims["official_authenticity"]
    assert auth["status"] == "Official Authenticity: Not Verified"
    assert auth["is_officially_verified"] is False
    assert "Automated AI checks evaluate readability" in auth["legal_advisory"]

def test_confidence_meter_low_quality_and_missing_field_deductions():
    """Test 6 & 7: Measurable deductions for degraded image and missing fields."""
    # Degraded blurry document with missing mandatory fields
    degraded_doc = UploadedDocument(
        id="test-doc-blurry",
        original_filename="Degraded_Scan.jpg",
        doc_category="PAN_CARD",
        user_assigned_category="PAN_CARD",
        file_size_bytes=8000, # < 15KB thumbnail
        ocr_overall_confidence=0.22, # very low confidence
        raw_text="INCOME TAX"
    )
    tamper = TamperingAnalysis(
        document_id="test-doc-blurry",
        is_flagged=True,
        risk_level="HIGH",
        explanation="Severe JPEG compression blocking"
    )
    degraded_doc.tampering_analysis = tamper

    # Only 1 field found out of 4 expected for PAN (full_name, father_name, doc_number, dob)
    fields = [
        ExtractedField(field_key="full_name", raw_value="Aarav", normalized_value="Aarav", confidence=0.30)
    ]

    mismatches = [{
        "document_a_id": "test-doc-blurry",
        "document_b_id": "other-doc",
        "requires_manual_review": True,
        "explanation": "Severe mismatch"
    }]

    res = confidence_meter_service.calculate_document_confidence(
        doc=degraded_doc,
        extracted_fields=fields,
        mismatches=mismatches,
        total_application_docs=2
    )

    dims = res["dimensions"]
    # OCR extraction score should be low
    assert dims["ocr_extraction"]["level"] == "Low Confidence"
    # Completeness should be penalized (1 out of 4 = 25%)
    assert dims["field_completeness"]["score"] == 25.0
    assert len(dims["field_completeness"]["missing_fields"]) == 3
    # Readability should be penalized for small file size and tampering flag
    assert dims["readability"]["score"] < 50.0
    # Cross consistency should be low
    assert dims["cross_consistency"]["level"] == "Low Confidence"
    # Overall score should be Low Confidence
    assert res["overall_level"] == "Low Confidence"

def test_document_renewal_side_by_side_comparison():
    """Test 5: Expiring document renewal upload with side-by-side field diff comparison."""
    db = SessionLocal()
    res = {}
    uid = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    try:
        # 1. Create a dummy user and application
        user = db.query(User).filter(User.email == "demo@docverify.ai").first()
        if not user:
            user = User(
                id=uid,
                email="demo@docverify.ai",
                hashed_password="dummy",
                full_name="Demo Citizen",
                role="USER"
            )
            db.add(user)
            db.commit()

        app = db.query(UserApplication).filter(UserApplication.user_id == user.id).first()
        if not app:
            app = UserApplication(
                id=str(uuid.uuid4()),
                user_id=user.id,
                application_profile_code="DRIVING_LICENSE_APPLICATION",
                application_name="Driving Licence Renewal",
                state="Tamil Nadu",
                district="Chennai"
            )
            db.add(app)
            db.commit()

        # 2. Create prior expiring document
        old_doc = UploadedDocument(
            id=doc_id,
            user_application_id=app.id,
            user_id=user.id,
            original_filename="Driving_Licence_Expiring.pdf",
            stored_filename=f"dl_expiring_{doc_id[:8]}.pdf",
            file_path=f"mock/path/{doc_id}.pdf",
            file_size_bytes=45000,
            mime_type="application/pdf",
            file_hash_sha256=f"hash_{doc_id[:16]}",
            is_encrypted=True,
            doc_category="DRIVING_LICENSE",
            user_assigned_category="DRIVING_LICENSE",
            ocr_status="SUCCESS",
            ocr_overall_confidence=0.92,
            raw_text="DRIVING LICENCE NO TN-01-20150001234 AARAV SURESH ISSUE: 10/01/2015 EXPIRY: 10/01/2023"
        )
        db.add(old_doc)
        db.commit()

        # Add fields to old doc
        f1 = ExtractedField(document_id=old_doc.id, field_key="doc_number", raw_value="TN-01-20150001234", normalized_value="TN-01-20150001234", confidence=0.95)
        f2 = ExtractedField(document_id=old_doc.id, field_key="issue_date", raw_value="10/01/2015", normalized_value="2015-01-10", confidence=0.95)
        f3 = ExtractedField(document_id=old_doc.id, field_key="expiry_date", raw_value="10/01/2023", normalized_value="2023-01-10", confidence=0.95)
        f4 = ExtractedField(document_id=old_doc.id, field_key="full_name", raw_value="Aarav Suresh", normalized_value="Aarav Suresh", confidence=0.98)
        db.add_all([f1, f2, f3, f4])
        db.commit()

        # Initial timeline record for old doc
        timeline_service.sync_timeline_for_user(user_id=user.id, db=db)

        # 3. Renew document using upload_renewed_document
        renewed_content = b"%PDF-1.4\nDRIVING LICENCE UNION OF INDIA\nLICENCE NO: TN-01-20260009999\nNAME: AARAV SURESH\nISSUE DATE: 15/02/2026\nVALID TILL / EXPIRY DATE: 15/02/2036\n"
        res = timeline_service.upload_renewed_document(
            old_document_id=old_doc.id,
            file_bytes=renewed_content,
            filename=f"Driving_Licence_Renewed_{doc_id[:6]}.pdf",
            user_id=user.id,
            db=db
        )

        assert res["success"] is True
        assert "comparison" in res
        diffs = res["comparison"]["field_diffs"]
        assert len(diffs) >= 3

        # Verify old timeline record was marked RENEWED
        old_rec = db.query(DocumentTimelineRecord).filter(DocumentTimelineRecord.document_id == old_doc.id).first()
        assert old_rec is not None
        assert old_rec.renewal_status == "RENEWED_AND_VERIFIED"
        assert "Superseded" in old_rec.validity_explanation

        # Verify new timeline record
        new_rec = db.query(DocumentTimelineRecord).filter(DocumentTimelineRecord.document_id == res["new_document_id"]).first()
        assert new_rec is not None
        assert new_rec.previous_document_id == old_doc.id
        assert new_rec.renewal_status == "RENEWED_AND_VERIFIED"
    finally:
        # Cleanup
        to_delete = [doc_id]
        if res.get("new_document_id"):
            to_delete.append(res["new_document_id"])
        db.query(DocumentTimelineRecord).filter(DocumentTimelineRecord.document_id.in_(to_delete)).delete(synchronize_session=False)
        db.query(ExtractedField).filter(ExtractedField.document_id.in_(to_delete)).delete(synchronize_session=False)
        db.query(UploadedDocument).filter(UploadedDocument.id.in_(to_delete)).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_timeline_reminder_and_affected_applications():
    """Test 9: Configurable reminder preference (30, 15, 7 days) and affected applications mapping."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@docverify.ai").first()
        assert user is not None

        # Sync and check timeline records exist
        timeline_service.sync_timeline_for_user(user.id, db)
        records = timeline_service.get_timeline_records(user.id, db)
        if records:
            rec = records[0]
            # Configure 15-day reminder
            updated = timeline_service.set_reminder_preference(
                record_id=rec["id"],
                reminder_days=15,
                is_enabled=True,
                user_id=user.id,
                db=db
            )
            assert updated["reminder_days_configured"] == 15
            assert updated["is_reminder_enabled"] is True

            # Check affected applications
            affected = timeline_service.get_affected_applications(rec["document_id"], db)
            assert isinstance(affected, list)
    finally:
        db.close()

def test_rule_radar_dashboard_notifications():
    """Test 10: Regulatory notifications generated for user's active applications."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@docverify.ai").first()
        assert user is not None

        notifs = rule_radar_service.get_user_notifications(user.id, db)
        assert isinstance(notifs, list)
        # Verify notifications have structured alert keys
        for n in notifs:
            assert "title" in n
            assert "application_name" in n
            assert "urgency" in n
            assert "source_authority" in n
            assert "impact_summary" in n
    finally:
        db.close()

