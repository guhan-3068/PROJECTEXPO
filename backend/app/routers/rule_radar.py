from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user, require_admin
from app.services.rule_radar_service import rule_radar_service

router = APIRouter(prefix="/rule-radar", tags=["Rule Change Radar"])

@router.get("/updates")
def get_regulatory_updates(
    state: Optional[str] = Query(None, description="Filter by state (e.g. 'Tamil Nadu')"),
    department: Optional[str] = Query(None, description="Filter by department"),
    profile_code: Optional[str] = Query(None, description="Filter by application type code"),
    status: Optional[str] = Query(None, description="Filter by status (New Official Update, Requirement Changed, No Confirmed Change, Verification Required)"),
    only_verified: Optional[bool] = Query(None, description="Only verified official notices"),
    db: Session = Depends(get_db)
):
    """
    Returns regulatory updates matching citizen search and filter criteria.
    """
    return rule_radar_service.get_updates(
        db=db,
        state=state,
        department=department,
        profile_code=profile_code,
        status=status,
        only_verified=only_verified
    )

@router.get("/notifications")
def get_dashboard_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Surfaces high-priority alerts when verified regulatory updates affect the user's active applications.
    """
    return rule_radar_service.get_user_notifications(user_id=current_user.id, db=db)

@router.get("/compare/{profile_code}")
def compare_requirement_versions(
    profile_code: str,
    db: Session = Depends(get_db)
):
    """
    Compares the current live checklist requirements of a profile against its saved prior version,
    highlighting added, removed, and modified requirements with citizen explanations.
    """
    res = rule_radar_service.compare_requirements(profile_code=profile_code, db=db)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/updates/{update_id}")
def get_update_details(
    update_id: str,
    db: Session = Depends(get_db)
):
    upd = rule_radar_service.get_update_by_id(update_id=update_id, db=db)
    if not upd:
        raise HTTPException(status_code=404, detail="Regulatory update not found")
    return upd

@router.post("/admin/create-update")
def admin_create_regulatory_update(
    data: Dict[str, Any],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-managed regulatory update registration.
    """
    try:
        return rule_radar_service.admin_create_update(data=data, is_admin=True, db=db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/admin/verify/{update_id}")
def admin_verify_regulatory_update(
    update_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin manual verification of pending regulatory updates.
    """
    try:
        return rule_radar_service.admin_verify_update(update_id=update_id, is_admin=True, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
