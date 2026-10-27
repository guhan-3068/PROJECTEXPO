import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import UserApplication, ApplicationProfile, ChecklistRequirement, AdminReview
from app.models.user import User
from app.schemas.admin import AdminReviewRequest, AdminReviewOut, ProfileCreate
from app.schemas.application import (
    ApplicationProfileOut, ChecklistRequirementOut, ChecklistRequirementCreate, ChecklistRequirementUpdate
)
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


# =====================================================================
# Document Requirements Management System (Admin CRUD & Review System)
# =====================================================================

@router.get("/requirements")
def list_requirements(
    profile_id: Optional[str] = None,
    profile_code: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    review_needed_only: bool = False,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(ChecklistRequirement).join(ApplicationProfile)

    if profile_id:
        query = query.filter(ChecklistRequirement.application_profile_id == profile_id)
    if profile_code:
        query = query.filter(ApplicationProfile.code == profile_code.upper())
    if status:
        query = query.filter(ChecklistRequirement.status == status)

    all_reqs = query.order_by(ApplicationProfile.name, ChecklistRequirement.sort_order).all()

    now = datetime.now(timezone.utc)
    results = []
    total_count = len(all_reqs)
    current_count = 0
    review_needed_count = 0
    outdated_count = 0

    for r in all_reqs:
        # Check if periodic review is needed (> 180 days or past next_review_date)
        is_overdue = False
        if r.next_review_date:
            is_overdue = (r.next_review_date if r.next_review_date.tzinfo else r.next_review_date.replace(tzinfo=timezone.utc)) < now
        elif r.last_verified_date:
            last_v = r.last_verified_date if r.last_verified_date.tzinfo else r.last_verified_date.replace(tzinfo=timezone.utc)
            is_overdue = (now - last_v).days > 180

        computed_status = r.status or "Current"
        if is_overdue and computed_status == "Current":
            computed_status = "Review Needed"

        if computed_status == "Current":
            current_count += 1
        elif computed_status == "Review Needed":
            review_needed_count += 1
        elif computed_status == "Outdated":
            outdated_count += 1

        if review_needed_only and computed_status != "Review Needed":
            continue

        if search:
            s_low = search.lower()
            name_match = s_low in (r.display_name or "").lower()
            code_match = s_low in (r.requirement_code or "").lower()
            desc_match = s_low in (r.description or "").lower()
            prof_match = s_low in (r.profile.name or "").lower() if r.profile else False
            if not (name_match or code_match or desc_match or prof_match):
                continue

        results.append({
            "id": r.id,
            "application_profile_id": r.application_profile_id,
            "profile_name": r.profile.name if r.profile else "N/A",
            "profile_code": r.profile.code if r.profile else "N/A",
            "jurisdiction": r.profile.jurisdiction if r.profile else "India",
            "requirement_code": r.requirement_code,
            "display_name": r.display_name,
            "description": r.description,
            "is_mandatory": r.is_mandatory,
            "requirement_type": r.requirement_type or ("REQUIRED" if r.is_mandatory else "OPTIONAL"),
            "accepted_categories": r.get_accepted_categories(),
            "alternative_documents": r.get_alternative_documents(),
            "eligibility_conditions": r.eligibility_conditions,
            "validity_rules": r.validity_rules,
            "accepted_formats": r.accepted_formats or "PDF, JPG, PNG (Max 15MB)",
            "official_source_url": r.official_source_url,
            "last_verified_date": r.last_verified_date,
            "next_review_date": r.next_review_date,
            "status": computed_status,
            "is_review_needed": computed_status == "Review Needed" or is_overdue,
            "sort_order": r.sort_order
        })

    return {
        "stats": {
            "total_requirements": total_count,
            "current_count": current_count,
            "review_needed_count": review_needed_count,
            "outdated_count": outdated_count
        },
        "requirements": results
    }


@router.post("/requirements", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_requirement(
    payload: ChecklistRequirementCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    profile = db.query(ApplicationProfile).filter(ApplicationProfile.id == payload.application_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Target Application Profile not found")

    now = datetime.now(timezone.utc)
    next_review = now + timedelta(days=180)

    req = ChecklistRequirement(
        application_profile_id=profile.id,
        requirement_code=payload.requirement_code.upper().replace(" ", "_"),
        display_name=payload.display_name,
        description=payload.description,
        is_mandatory=payload.is_mandatory,
        requirement_type=payload.requirement_type,
        accepted_categories=json.dumps(payload.accepted_categories or []),
        alternative_documents=json.dumps(payload.alternative_documents or []),
        eligibility_conditions=payload.eligibility_conditions,
        validity_rules=payload.validity_rules,
        accepted_formats=payload.accepted_formats or "PDF, JPG, PNG (Max 15MB)",
        official_source_url=payload.official_source_url,
        last_verified_date=payload.last_verified_date or now,
        next_review_date=payload.next_review_date or next_review,
        status=payload.status or "Current",
        sort_order=payload.sort_order or 0
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return {
        "message": "Requirement created successfully",
        "id": req.id,
        "requirement_code": req.requirement_code,
        "display_name": req.display_name,
        "status": req.status
    }


@router.put("/requirements/{requirement_id}", response_model=Dict[str, Any])
def update_requirement(
    requirement_id: str,
    payload: ChecklistRequirementUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    req = db.query(ChecklistRequirement).filter(ChecklistRequirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if payload.display_name is not None:
        req.display_name = payload.display_name
    if payload.description is not None:
        req.description = payload.description
    if payload.is_mandatory is not None:
        req.is_mandatory = payload.is_mandatory
    if payload.requirement_type is not None:
        req.requirement_type = payload.requirement_type
    if payload.accepted_categories is not None:
        req.accepted_categories = json.dumps(payload.accepted_categories)
    if payload.alternative_documents is not None:
        req.set_alternative_documents(payload.alternative_documents)
    if payload.eligibility_conditions is not None:
        req.eligibility_conditions = payload.eligibility_conditions
    if payload.validity_rules is not None:
        req.validity_rules = payload.validity_rules
    if payload.accepted_formats is not None:
        req.accepted_formats = payload.accepted_formats
    if payload.official_source_url is not None:
        req.official_source_url = payload.official_source_url
    if payload.sort_order is not None:
        req.sort_order = payload.sort_order

    if payload.status is not None:
        req.status = payload.status
        if payload.status == "Current":
            now = datetime.now(timezone.utc)
            req.last_verified_date = now
            req.next_review_date = now + timedelta(days=180)

    db.commit()
    db.refresh(req)

    return {
        "message": "Requirement updated successfully",
        "id": req.id,
        "display_name": req.display_name,
        "status": req.status,
        "last_verified_date": req.last_verified_date
    }


@router.delete("/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_requirement(
    requirement_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    req = db.query(ChecklistRequirement).filter(ChecklistRequirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    db.delete(req)
    db.commit()
    return None


@router.post("/requirements/{requirement_id}/verify", response_model=Dict[str, Any])
def mark_requirement_verified(
    requirement_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    req = db.query(ChecklistRequirement).filter(ChecklistRequirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    now = datetime.now(timezone.utc)
    req.last_verified_date = now
    req.next_review_date = now + timedelta(days=180)
    req.status = "Current"

    db.commit()
    db.refresh(req)

    return {
        "message": "Requirement successfully verified and review cycle reset to 180 days.",
        "id": req.id,
        "display_name": req.display_name,
        "status": req.status,
        "last_verified_date": req.last_verified_date,
        "next_review_date": req.next_review_date
    }


@router.post("/requirements/sync-defaults", response_model=Dict[str, Any])
def sync_default_requirements(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    from app.routers.applications import sync_all_profiles
    sync_all_profiles(db)
    total_reqs = db.query(ChecklistRequirement).count()
    return {
        "message": "Synchronized official default requirements across all Indian citizen service profiles.",
        "total_requirements": total_reqs
    }
