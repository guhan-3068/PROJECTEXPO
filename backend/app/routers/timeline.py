from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.timeline_service import timeline_service

router = APIRouter(prefix="/timeline", tags=["Document Timeline & Renewals"])

@router.get("/records")
def get_timeline_records(
    status_filter: Optional[str] = Query(None, description="ACTIVE, EXPIRING_SOON, EXPIRED, NO_EXPIRY, VALIDITY_NEEDS_CONFIRMATION, RENEWAL_IN_PROGRESS"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the user's document timeline, synchronizing with any newly uploaded certificates.
    """
    # Sync first to ensure newly uploaded documents appear
    timeline_service.sync_timeline_for_user(user_id=current_user.id, db=db)
    return timeline_service.get_timeline_records(
        user_id=current_user.id,
        db=db,
        status_filter=status_filter
    )

@router.post("/update-dates/{document_id}")
def update_dates(
    document_id: str,
    payload: Dict[str, Optional[str]],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows citizens to manually review and correct extracted issue and expiry dates.
    """
    issue_date = payload.get("issue_date")
    expiry_date = payload.get("expiry_date")
    try:
        return timeline_service.update_dates_manually(
            document_id=document_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            user_id=current_user.id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/reminder/{record_id}")
def set_reminder(
    record_id: str,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configures citizen reminders before expiry (e.g. 30 days, 15 days, 7 days).
    """
    reminder_days = int(payload.get("reminder_days", 30))
    is_enabled = bool(payload.get("is_enabled", True))
    try:
        return timeline_service.set_reminder_preference(
            record_id=record_id,
            reminder_days=reminder_days,
            is_enabled=is_enabled,
            user_id=current_user.id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/renew/{document_id}")
async def upload_renewed_document(
    document_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows user to upload a renewed replacement document.
    Extracts entities, links old and new document versions, and returns a side-by-side comparison.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        return timeline_service.upload_renewed_document(
            old_document_id=document_id,
            file_bytes=contents,
            filename=file.filename,
            user_id=current_user.id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process renewed document: {e}")

@router.get("/affected-applications/{document_id}")
def get_affected_applications(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Shows which citizen applications are associated with or impacted by this document.
    """
    return timeline_service.get_affected_applications(document_id=document_id, db=db)
