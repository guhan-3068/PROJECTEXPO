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
    alternative_documents: List[str] = []
    eligibility_conditions: Optional[str] = None
    validity_rules: Optional[str] = None
    accepted_formats: Optional[str] = "PDF, JPG, JPEG, PNG (Max 15MB)"
    official_source_url: Optional[str] = None
    status: Optional[str] = "Current"

    @field_validator("accepted_categories", "alternative_documents", mode="before")
    def parse_json_lists(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

class ChecklistRequirementOut(ChecklistRequirementBase):
    id: str
    application_profile_id: str
    last_verified_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    is_review_needed: bool = False

    class Config:
        from_attributes = True

class ChecklistRequirementCreate(ChecklistRequirementBase):
    application_profile_id: str
    last_verified_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

class ChecklistRequirementUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_mandatory: Optional[bool] = None
    requirement_type: Optional[str] = None
    accepted_categories: Optional[List[str]] = None
    alternative_documents: Optional[List[str]] = None
    eligibility_conditions: Optional[str] = None
    validity_rules: Optional[str] = None
    accepted_formats: Optional[str] = None
    official_source_url: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None

class ApplicationProfileBase(BaseModel):
    code: str
    name: str
    jurisdiction: str
    category: str
    description: Optional[str] = None
    is_active: bool = True
    official_source_url: Optional[str] = None
    status: Optional[str] = "Current"
    eligibility_criteria: Optional[str] = None

class ApplicationProfileOut(ApplicationProfileBase):
    id: str
    last_verified_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
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
