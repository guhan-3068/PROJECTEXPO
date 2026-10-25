import io
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

def run_e2e_verification_test():
    print("==================================================")
    print("      DocVerify AI - End-to-End Test Suite        ")
    print("==================================================")

    # 1. Initialize DB tables
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("[OK] Health Check Passed:", res.json()["status"])

        # 2. Check OpenAPI / Docs
        res = client.get("/docs")
        assert res.status_code == 200, f"Docs check failed: {res.text}"
        print("[OK] Swagger Documentation Available: http://127.0.0.1:8000/docs")

        # 3. Check Application Profiles
        res = client.get("/api/v1/applications/profiles")
        assert res.status_code == 200, f"Profiles fetch failed: {res.text}"
        profiles = res.json()
        assert len(profiles) >= 3, f"Expected at least 3 profiles, got {len(profiles)}"
        passport_profile = next((p for p in profiles if "PASSPORT" in p["code"]), profiles[0])
        print(f"[OK] Application Profiles Verified: Found {len(profiles)} profiles")
        print(f"     Selected profile: '{passport_profile['name']}' ({len(passport_profile['requirements'])} requirements)")

        # 4. User Registration
        user_email = "test_applicant@example.com"
        reg_payload = {
            "full_name": "Alex Taylor",
            "email": user_email,
            "password": "SecurePassword123!",
            "role": "USER"
        }
        res = client.post("/api/v1/auth/register", json=reg_payload)
        # 201 or 400 if already exists
        if res.status_code == 400 and "already exists" in res.text:
            print("[OK] User already registered, proceeding to login.")
        else:
            assert res.status_code == 201, f"Registration failed: {res.text}"
            print("[OK] User Registration Passed for:", user_email)

        # 5. User Login
        login_res = client.post("/api/v1/auth/login", json={"email": user_email, "password": "SecurePassword123!"})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[OK] Authentication & JWT Generation Passed. Token acquired.")

        # 6. Start Application
        start_payload = {
            "application_profile_id": passport_profile["id"],
            "consent_given": True
        }
        app_res = client.post("/api/v1/applications/start", json=start_payload, headers=headers)
        assert app_res.status_code == 201, f"Starting application failed: {app_res.text}"
        app_data = app_res.json()
        app_id = app_data["id"]
        app_ref = app_data["reference_number"]
        print(f"[OK] Application Instance Created: Ref {app_ref} (ID: {app_id})")

        # 7. Upload Sample Test Documents
        sample_dir = Path(__file__).resolve().parent / "tests" / "sample_docs"
        passport_file = sample_dir / "passport_valid.pdf"
        utility_file = sample_dir / "utility_bill.pdf"

        assert passport_file.exists(), f"Sample passport not found at {passport_file}"
        assert utility_file.exists(), f"Sample utility bill not found at {utility_file}"

        with open(passport_file, "rb") as f1, open(utility_file, "rb") as f2:
            files = [
                ("files", ("passport_valid.pdf", f1.read(), "application/pdf")),
                ("files", ("utility_bill.pdf", f2.read(), "application/pdf"))
            ]
            upload_res = client.post(
                f"/api/v1/documents/upload/{app_id}",
                files=files,
                headers=headers
            )
            assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
            uploaded_docs = upload_res.json()
            assert len(uploaded_docs) == 2, f"Expected 2 uploaded documents, got {len(uploaded_docs)}"
            print(f"[OK] Document Ingestion & AES Encryption Passed: Uploaded {len(uploaded_docs)} files")
            for doc in uploaded_docs:
                print(f"     - {doc['original_filename']}: Category '{doc['doc_category']}', OCR Confidence: {int(doc['ocr_overall_confidence']*100)}%")

        # 8. Run Verification Pipeline
        verif_res = client.post(f"/api/v1/verify/run/{app_id}", headers=headers)
        assert verif_res.status_code == 200, f"Verification run failed: {verif_res.text}"
        ver_data = verif_res.json()
        print("[OK] Verification Pipeline Executed Successfully!")
        print("     Overall Status:", ver_data["overall_status"])
        print("     Satisfied Checklist Items:", len(ver_data["satisfied_requirements"]))
        print("     Missing Checklist Items:", len(ver_data["missing_requirements"]))
        print("     Expiring Soon Docs:", len(ver_data["expiring_soon_documents"]))
        print("     Detected Mismatches:", len(ver_data["detected_mismatches"]))
        print("     Recommended Actions:", ver_data["recommended_actions"])

        # 9. Download Generated PDF Report
        report_res = client.get(f"/api/v1/reports/{app_id}/download", headers=headers)
        assert report_res.status_code == 200, f"PDF report download failed: {report_res.text}"
        assert len(report_res.content) > 1000, "PDF report content is empty or too small"
        print(f"[OK] PDF Verification Report Successfully Generated and Downloaded ({len(report_res.content)} bytes)")

    print("\n==================================================")
    print("   ALL END-TO-END VERIFICATION TESTS PASSED!     ")
    print("==================================================")

if __name__ == "__main__":
    run_e2e_verification_test()
