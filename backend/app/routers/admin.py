import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import UserApplication, ApplicationProfile, ChecklistRequirement, AdminReview
from app.models.user import User
from app.schemas.admin import AdminReviewRequest, AdminReviewOut, ProfileCreate
from app.schemas.application import ApplicationProfileOut
from app.routers.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Administrator Review & Config"])

@router.get("/applications")
def list_all_applications(
    status_filter: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(UserApplication)
    if status_filter:
        query = query.filter(UserApplication.status == status_filter.upper())
    apps = query.order_by(UserApplication.created_at.desc()).all()

    results = []
    for app in apps:
        ver = app.verification_result
        results.append({
            "id": app.id,
            "reference_number": app.reference_number,
            "applicant_name": app.user.full_name if app.user else "N/A",
            "applicant_email": app.user.email if app.user else "N/A",
            "profile_name": app.profile.name if app.profile else "N/A",
            "jurisdiction": app.profile.jurisdiction if app.profile else "N/A",
            "status": app.status,
            "document_count": len(app.documents),
            "created_at": app.created_at,
            "has_mismatches": len(ver.get_json_field("detected_mismatches")) > 0 if ver else False,
            "has_tampering_flags": len(ver.get_json_field("tampering_flags")) > 0 if ver else False,
            "has_expired_docs": len(ver.get_json_field("expired_documents")) > 0 if ver else False
        })
    return results

@router.post("/review/{application_id}", response_model=AdminReviewOut)
def submit_admin_review(
    application_id: str,
    payload: AdminReviewRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    review = AdminReview(
        user_application_id=app.id,
        admin_user_id=admin.id,
        previous_status=app.status,
        new_status=payload.new_status,
        review_notes=payload.review_notes
    )
    db.add(review)

    # Update state
    app.status = payload.new_status
    db.commit()
    db.refresh(review)
    return review

@router.post("/profiles", response_model=ApplicationProfileOut, status_code=status.HTTP_201_CREATED)
def create_application_profile(
    payload: ProfileCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(ApplicationProfile).filter(ApplicationProfile.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile code already exists")

    profile = ApplicationProfile(
        code=payload.code,
        name=payload.name,
        jurisdiction=payload.jurisdiction,
        category=payload.category,
        description=payload.description
    )
    db.add(profile)
    db.flush()

    for r in payload.requirements:
        req_obj = ChecklistRequirement(
            application_profile_id=profile.id,
            requirement_code=r.requirement_code,
            display_name=r.display_name,
            description=r.description,
            is_mandatory=r.is_mandatory,
            accepted_categories=json.dumps(r.accepted_categories),
            min_validity_days=r.min_validity_days,
            allow_manual_override=r.allow_manual_override,
            sort_order=r.sort_order
        )
        db.add(req_obj)

    db.commit()
    db.refresh(profile)
    for req in profile.requirements:
        req.accepted_categories = req.get_accepted_categories()
    return profile
