from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AdminReviewRequest(BaseModel):
    new_status: str = Field(..., pattern="^(APPROVED|REJECTED|REVIEW_REQUIRED|INCOMPLETE)$")
    review_notes: str = Field(..., min_length=3, max_length=2000)

class AdminReviewOut(BaseModel):
    id: str
    user_application_id: str
    admin_user_id: str
    previous_status: str
    new_status: str
    review_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RequirementCreate(BaseModel):
    requirement_code: str
    display_name: str
    description: Optional[str] = None
    is_mandatory: bool = True
    accepted_categories: List[str]
    min_validity_days: int = 0
    allow_manual_override: bool = True
    sort_order: int = 0

class ProfileCreate(BaseModel):
    code: str
    name: str
    jurisdiction: str
    category: str
    description: Optional[str] = None
    requirements: List[RequirementCreate] = []
