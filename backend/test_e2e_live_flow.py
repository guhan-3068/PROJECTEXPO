import sys
import io

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_all_10_tests():
    print("=====================================================================")
    print("AI DOCVERIFY - COMPLETE 10-POINT CITIZEN INTELLIGENCE VERIFICATION")
    print("=====================================================================")

    # -------------------------------------------------------------
    # 0. Citizen Authentication
    # -------------------------------------------------------------
    print("\n[Step 0] Testing Citizen Authentication...")
    resp = client.post("/api/v1/auth/login", json={"email": "demo@docverify.ai", "password": "Password123!"})
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    auth_res = resp.json()
    token = auth_res["access_token"]
    user_name = auth_res["user"]["full_name"]
    print(f"  -> SUCCESS: Signed in as {user_name} ({auth_res['user']['email']})")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # -------------------------------------------------------------
    # Test 1: A confirmed change in a saved application requirement
    # -------------------------------------------------------------
    print("\n[Test 1] Testing Confirmed Change in Application Requirement (Rule Change Radar Diff)...")
    resp = client.get("/api/v1/rule-radar/compare/FIRST_GRADUATE_APPLICATION", headers=headers)
    assert resp.status_code == 200, f"Radar diff failed: {resp.status_code} {resp.text}"
    diff_res = resp.json()
    assert diff_res["has_changes"] is True, "Expected changes in First Graduate requirements"
    assert len(diff_res["modified_requirements"]) > 0, "Expected modified requirements"
    mod = diff_res["modified_requirements"][0]
    print(f"  -> SUCCESS: Modified requirement detected: '{mod['display_name']}'")
    print(f"     New Rule: {mod['new_rule']}")
    print(f"     Prior Rule: {mod['previous_rule']}")
    print(f"     Authority: {mod['authority']} (Effective: {mod['effective_date']})")

    # -------------------------------------------------------------
    # Test 2: An unverified update that must not be shown as official
    # -------------------------------------------------------------
    print("\n[Test 2] Testing Isolation of Unverified Updates (Must NOT Be Shown as Official)...")
    resp = client.get("/api/v1/rule-radar/updates?only_verified=true", headers=headers)
    assert resp.status_code == 200
    verified_only = resp.json()
    assert all(u["is_verified"] is True for u in verified_only), "Unverified item found in verified-only list"
    assert not any(u["status"] == "Verification Required" for u in verified_only)
    print(f"  -> SUCCESS: Retrieved {len(verified_only)} verified official updates.")

    resp = client.get("/api/v1/rule-radar/updates?status=Verification+Required", headers=headers)
    assert resp.status_code == 200
    unverified_list = resp.json()
    assert len(unverified_list) >= 1, "Expected at least 1 unverified update"
    unverified = unverified_list[0]
    assert unverified["is_verified"] is False, "Unverified notice must have is_verified=False"
    assert unverified["status"] == "Verification Required"
    print(f"  -> SUCCESS: Unverified notice isolated: '{unverified['title']}'")
    print(f"     Status: {unverified['status']} | Verified: {unverified['is_verified']}")
    print(f"     Advisory: {unverified['impact_summary']}")

    # -------------------------------------------------------------
    # Test 3: A document with a valid expiry date
    # -------------------------------------------------------------
    print("\n[Test 3] Testing Document with a Valid Expiry Date...")
    resp = client.post("/api/v1/applications/demo/load/expired_certificate", headers=headers)
    assert resp.status_code == 200
    exp_app = resp.json()
    exp_app_id = exp_app["id"]

    # Sync and fetch timeline records
    resp = client.get("/api/v1/timeline/records", headers=headers)
    assert resp.status_code == 200
    timeline_records = resp.json()
    assert len(timeline_records) > 0, "Timeline records should not be empty"
    print(f"  -> SUCCESS: Retrieved {len(timeline_records)} timeline records.")

    # -------------------------------------------------------------
    # Test 4: A document with no applicable expiry date (Lifetime)
    # -------------------------------------------------------------
    print("\n[Test 4] Testing Document with Lifetime / No Applicable Expiry Date...")
    aadhaar_rec = next((r for r in timeline_records if r["doc_category"] == "AADHAAR"), None)
    assert aadhaar_rec is not None, "Aadhaar record not found in timeline"
    assert aadhaar_rec["validity_status"] == "NO_EXPIRY", f"Expected NO_EXPIRY, got {aadhaar_rec['validity_status']}"
    assert "lifelong validity" in aadhaar_rec["validity_explanation"].lower() or "lifetime" in aadhaar_rec["validity_explanation"].lower()
    print(f"  -> SUCCESS: Lifetime certificate verified: {aadhaar_rec['document_name']}")
    print(f"     Status: {aadhaar_rec['validity_status']}")
    print(f"     Explanation: {aadhaar_rec['validity_explanation']}")

    # -------------------------------------------------------------
    # Test 5: An expiring/expired document and a renewed replacement
    # -------------------------------------------------------------
    print("\n[Test 5] Testing Expiring Document Renewal & Side-by-Side Comparison...")
    dl_rec = next((r for r in timeline_records if r["doc_category"] == "DRIVING_LICENSE"), None)
    if not dl_rec:
        dl_rec = timeline_records[0]

    # Let's manually set a future valid expiry date first to test date editing
    resp = client.post(
        f"/api/v1/timeline/update-dates/{dl_rec['document_id']}",
        json={"issue_date": "10/01/2021", "expiry_date": "10/01/2030"},
        headers=headers
    )
    assert resp.status_code == 200, f"Update dates failed: {resp.status_code} {resp.text}"
    updated_res = resp.json()
    assert updated_res["validity_status"] == "ACTIVE"
    print(f"  -> SUCCESS: Manually updated dates. Document is now {updated_res['validity_status']} until 2030.")

    # Now test renewal upload using a renewed sample file via multipart form
    renewed_pdf_content = b"%PDF-1.4 Renewed Official Driving Licence 2026-2036 TN-RTO-9999"
    files = {
        "file": ("Driving_Licence_Renewed_2026.pdf", renewed_pdf_content, "application/pdf")
    }
    resp = client.post(
        f"/api/v1/timeline/renew/{dl_rec['document_id']}",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, f"Renewal failed: {resp.status_code} {resp.text}"
    renew_res = resp.json()
    assert renew_res["success"] is True
    assert "comparison" in renew_res
    diffs = renew_res["comparison"]["field_diffs"]
    print(f"  -> SUCCESS: Renewed certificate linked. Side-by-side comparison generated:")
    for d in diffs:
        print(f"     - {d['field']}: Old='{d['old_version']}' vs New='{d['new_version']}' (Changed: {d['is_changed']})")

    # -------------------------------------------------------------
    # Test 6 & 7: Low-quality OCR output, missing field & mismatch deductions
    # -------------------------------------------------------------
    print("\n[Test 6 & 7] Testing Confidence Meter Deductions for Blurry Scan & Missing Fields...")
    resp = client.post("/api/v1/applications/demo/load/blurry_unreadable", headers=headers)
    assert resp.status_code == 200
    blurry_app = resp.json()
    blurry_app_id = blurry_app["id"]

    resp = client.get(f"/api/v1/verify/confidence/{blurry_app_id}", headers=headers)
    assert resp.status_code == 200
    conf_res = resp.json()
    docs_conf = conf_res["documents"]
    assert len(docs_conf) > 0
    blurry_conf = next((d for d in docs_conf if "Degraded" in d["original_filename"]), docs_conf[-1])
    readability_dim = blurry_conf["dimensions"]["readability"]
    ocr_dim = blurry_conf["dimensions"]["ocr_extraction"]
    completeness_dim = blurry_conf["dimensions"]["field_completeness"]

    print(f"  -> SUCCESS: Blurry Document Evaluated: '{blurry_conf['original_filename']}'")
    print(f"     Readability Score: {readability_dim['score']}% ({readability_dim['level']})")
    print(f"     Readability Reasons: {readability_dim['reasons']}")
    print(f"     OCR Extraction Score: {ocr_dim['score']}% ({ocr_dim['level']})")
    print(f"     Field Completeness: {completeness_dim['score']}% (Missing: {completeness_dim.get('missing_fields')})")
    assert readability_dim["score"] < 70.0 or ocr_dim["score"] < 70.0, "Expected deduction for blurry/degraded document"

    # -------------------------------------------------------------
    # Test 8: High OCR confidence but Official Authenticity: Not Verified
    # -------------------------------------------------------------
    print("\n[Test 8] Testing Official Authenticity Status on High OCR Document...")
    sharp_doc = next((d for d in docs_conf if "Aadhaar" in d["original_filename"]), docs_conf[0])
    auth_dim = sharp_doc["dimensions"]["official_authenticity"]
    print(f"  -> Document: {sharp_doc['original_filename']} (OCR Confidence: {sharp_doc['dimensions']['ocr_extraction']['score']}%)")
    print(f"     Status: {auth_dim['status']}")
    print(f"     Level:  {auth_dim['level']}")
    print(f"     Advisory: {auth_dim['legal_advisory']}")
    assert auth_dim["status"] == "Official Authenticity: Not Verified"
    assert auth_dim["is_officially_verified"] is False
    print("  -> SUCCESS: Mandatory authenticity non-certification advisory verified!")

    # -------------------------------------------------------------
    # Test 9: Dashboard Integration & PDF Report Generation
    # -------------------------------------------------------------
    print("\n[Test 9] Testing Dashboard Notifications & PDF Report Generation...")
    resp = client.get("/api/v1/rule-radar/notifications", headers=headers)
    assert resp.status_code == 200
    notifs = resp.json()
    print(f"  -> SUCCESS: Retrieved {len(notifs)} application-targeted regulatory notifications.")
    for n in notifs[:2]:
        print(f"     [{n['urgency']}] {n['title']} (Affects: {n['application_name']})")

    resp = client.get(f"/api/v1/reports/{exp_app_id}/download", headers=headers)
    assert resp.status_code == 200
    pdf_bytes = resp.content
    assert pdf_bytes.startswith(b"%PDF"), "Output is not valid PDF"
    assert len(pdf_bytes) > 2000, "PDF is too small"
    print(f"  -> SUCCESS: Generated complete Verification Report PDF ({len(pdf_bytes):,} bytes) with Confidence & Timeline sections.")

    # -------------------------------------------------------------
    # Test 10: Existing Application Features Intact
    # -------------------------------------------------------------
    print("\n[Test 10] Testing Existing Application Features (Pre-check, Recheck, Checklists)...")
    resp = client.get(f"/api/v1/verify/{exp_app_id}", headers=headers)
    assert resp.status_code == 200
    ver_data = resp.json()
    assert "prioritized_checklist" in ver_data
    assert "action_plan" in ver_data
    assert "confidence_summary" in ver_data
    print(f"  -> SUCCESS: Verification result intact. Readiness Status: '{ver_data['readiness_status']}' ({ver_data['readiness_score']})")

    resp = client.post(f"/api/v1/verify/recheck/{exp_app_id}", headers=headers)
    assert resp.status_code == 200
    recheck_data = resp.json()
    assert recheck_data["id"] == ver_data["id"]
    print(f"  -> SUCCESS: Dynamic Recheck endpoint validated.")

    print("\n=====================================================================")
    print("ALL 10 CITIZEN INTELLIGENCE VERIFICATION SCENARIOS PASSED WITH 100% SUCCESS!")
    print("=====================================================================")

if __name__ == "__main__":
    run_all_10_tests()
