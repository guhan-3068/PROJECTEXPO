import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime

class ChecklistRequirementBase(BaseModel):
    requirement_code: str
    display_name: str
    description: Optional[str] = None
    is_mandatory: bool = True
    requirement_type: str = "REQUIRED"  # REQUIRED, CONDITIONALLY_REQUIRED, OPTIONAL
    accepted_categories: List[str] = []
    min_validity_days: int = 0
    allow_manual_override: bool = True
    sort_order: int = 0

    @field_validator("accepted_categories", mode="before")
    def parse_accepted_categories(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

class ChecklistRequirementOut(ChecklistRequirementBase):
    id: str
    application_profile_id: str

    class Config:
        from_attributes = True

class ApplicationProfileBase(BaseModel):
    code: str
    name: str
    jurisdiction: str
    category: str
    description: Optional[str] = None
    is_active: bool = True

class ApplicationProfileOut(ApplicationProfileBase):
    id: str
    requirements: List[ChecklistRequirementOut] = []

    class Config:
        from_attributes = True

class UserApplicationCreate(BaseModel):
    application_profile_id: str
    consent_given: bool = Field(..., description="User consent required to process sensitive documents")
    state: Optional[str] = "Tamil Nadu"
    district: Optional[str] = "Chennai"
    issuing_authority: Optional[str] = None

class UserApplicationOut(BaseModel):
    id: str
    user_id: str
    application_profile_id: str
    reference_number: str
    status: str
    readiness_status: Optional[str] = "Action Required"
    state: Optional[str] = "Tamil Nadu"
    district: Optional[str] = "Chennai"
    issuing_authority: Optional[str] = None
    consent_given: bool
    consent_timestamp: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    profile: Optional[ApplicationProfileOut] = None

    class Config:
        from_attributes = True
