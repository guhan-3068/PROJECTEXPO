import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
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
from app.services.document_verifier import document_verifier
from app.services.citizen_profiles_data import INDIAN_CITIZEN_PROFILES_ENRICHED as INDIAN_CITIZEN_PROFILES

router = APIRouter(prefix="/applications", tags=["Applications & Checklists"])

def sync_all_profiles(db: Session):
    """
    Ensures all 14 Indian citizen application categories and their checklists
    are registered in the database with rich verification metadata, alternative documents,
    validity rules, and official source links.
    """
    now = datetime.now(timezone.utc)
    default_next_review = now + timedelta(days=180)

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
                official_source_url=p_data.get("official_source_url"),
                status=p_data.get("status", "Current"),
                eligibility_criteria=p_data.get("eligibility_criteria"),
                last_verified_date=now,
                next_review_date=default_next_review,
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
                    alternative_documents=json.dumps(r.get("alternative_documents", [])),
                    eligibility_conditions=r.get("eligibility_conditions"),
                    validity_rules=r.get("validity_rules"),
                    accepted_formats=r.get("accepted_formats", "PDF, JPG, JPEG, PNG (Max 5MB)"),
                    official_source_url=r.get("official_source_url"),
                    last_verified_date=now,
                    next_review_date=default_next_review,
                    status=r.get("status", "Current"),
                    sort_order=r.get("sort_order", 0)
                )
                db.add(req_obj)
        else:
            if p_data.get("official_source_url"):
                profile.official_source_url = p_data.get("official_source_url")
            if p_data.get("eligibility_criteria"):
                profile.eligibility_criteria = p_data.get("eligibility_criteria")
            if not profile.last_verified_date:
                profile.last_verified_date = now
            if not profile.next_review_date:
                profile.next_review_date = default_next_review
            profile.status = p_data.get("status", "Current")

            existing_reqs_by_code = {r.requirement_code: r for r in profile.requirements}
            for r in reqs:
                code = r["requirement_code"]
                if code not in existing_reqs_by_code:
                    req_obj = ChecklistRequirement(
                        application_profile_id=profile.id,
                        requirement_code=code,
                        display_name=r["display_name"],
                        description=r.get("description"),
                        is_mandatory=r.get("is_mandatory", True),
                        requirement_type=r.get("requirement_type", "REQUIRED" if r.get("is_mandatory", True) else "OPTIONAL"),
                        accepted_categories=json.dumps(r.get("accepted_categories", [])),
                        alternative_documents=json.dumps(r.get("alternative_documents", [])),
                        eligibility_conditions=r.get("eligibility_conditions"),
                        validity_rules=r.get("validity_rules"),
                        accepted_formats=r.get("accepted_formats", "PDF, JPG, JPEG, PNG (Max 5MB)"),
                        official_source_url=r.get("official_source_url"),
                        last_verified_date=now,
                        next_review_date=default_next_review,
                        status=r.get("status", "Current"),
                        sort_order=r.get("sort_order", 0)
                    )
                    db.add(req_obj)
                else:
                    er = existing_reqs_by_code[code]
                    er.display_name = r["display_name"]
                    er.description = r.get("description")
                    er.is_mandatory = r.get("is_mandatory", True)
                    er.requirement_type = r.get("requirement_type", "REQUIRED" if er.is_mandatory else "OPTIONAL")
                    er.accepted_categories = json.dumps(r.get("accepted_categories", []))
                    if r.get("alternative_documents"):
                        er.set_alternative_documents(r.get("alternative_documents", []))
                    if r.get("eligibility_conditions"):
                        er.eligibility_conditions = r.get("eligibility_conditions")
                    if r.get("validity_rules"):
                        er.validity_rules = r.get("validity_rules")
                    if r.get("accepted_formats"):
                        er.accepted_formats = r.get("accepted_formats")
                    if r.get("official_source_url"):
                        er.official_source_url = r.get("official_source_url")
                    if not er.last_verified_date:
                        er.last_verified_date = now
                    if not er.next_review_date:
                        er.next_review_date = default_next_review
                    if not er.status:
                        er.status = "Current"
                    er.sort_order = r.get("sort_order", 0)

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


@router.get("/{application_id}/slots")
def get_application_document_slots(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns each individual requirement slot for an application,
    paired with any uploaded document mapped to that slot and its 6-dimension evaluation.
    """
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    profile = app.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == application_id).all()
    docs_by_req_id = {d.checklist_requirement_id: d for d in docs if d.checklist_requirement_id}
    unmapped_docs = [d for d in docs if not d.checklist_requirement_id]

    slots = []
    for req in profile.requirements:
        mapped_doc = docs_by_req_id.get(req.id)
        if not mapped_doc:
            acc = req.get_accepted_categories()
            for ud in unmapped_docs:
                if (ud.doc_category or "").upper() in acc:
                    mapped_doc = ud
                    break

        doc_out = None
        slot_status = "EMPTY"
        if mapped_doc:
            evaluation = document_verifier.evaluate_document(mapped_doc, req, profile.code)
            t = mapped_doc.tampering_analysis
            doc_out = {
                "id": mapped_doc.id,
                "original_filename": mapped_doc.original_filename,
                "file_size_bytes": mapped_doc.file_size_bytes,
                "mime_type": mapped_doc.mime_type,
                "doc_category": mapped_doc.doc_category,
                "ocr_overall_confidence": mapped_doc.ocr_overall_confidence,
                "created_at": mapped_doc.created_at,
                "evaluation": evaluation,
                "authenticity_result": getattr(t, "authenticity_result", None) or ("Potential manipulation detected" if t and t.is_flagged else "No obvious manipulation detected")
            }
            off_stat = evaluation["dimensions"]["official_readiness"]["status"]
            auth_stat = evaluation["dimensions"]["authenticity_screening"]["status"]
            if auth_stat == "FAIL" or off_stat == "NEEDS_REVIEW":
                slot_status = "ACTION_REQUIRED"
            elif off_stat == "PHYSICAL_REQUIRED" or auth_stat == "WARNING":
                slot_status = "NEEDS_REVIEW"
            else:
                slot_status = "PASSING"

        slots.append({
            "requirement": {
                "id": req.id,
                "requirement_code": req.requirement_code,
                "display_name": req.display_name,
                "description": req.description,
                "is_mandatory": req.is_mandatory,
                "requirement_type": req.requirement_type or ("REQUIRED" if req.is_mandatory else "OPTIONAL"),
                "accepted_categories": req.get_accepted_categories(),
                "alternative_documents": req.get_alternative_documents(),
                "eligibility_conditions": req.eligibility_conditions,
                "validity_rules": req.validity_rules,
                "accepted_formats": req.accepted_formats or "PDF, JPG, JPEG, PNG (Max 5MB)",
                "official_source_url": req.official_source_url,
                "last_verified_date": req.last_verified_date,
                "next_review_date": req.next_review_date,
                "status": req.status or "Current",
                "sort_order": req.sort_order
            },
            "is_uploaded": mapped_doc is not None,
            "slot_status": slot_status,
            "uploaded_document": doc_out
        })

    return {
        "application_id": app.id,
        "profile_name": profile.name,
        "jurisdiction": profile.jurisdiction,
        "slots": slots
    }
