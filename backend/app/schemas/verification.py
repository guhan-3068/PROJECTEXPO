from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class ChecklistItemStatus(BaseModel):
    requirement_code: str
    display_name: str
    is_mandatory: bool
    is_satisfied: bool
    matched_document_ids: List[str] = []
    matched_document_names: List[str] = []
    reason: Optional[str] = None

class ExpiryDetail(BaseModel):
    document_id: str
    document_name: str
    doc_category: str
    expiry_date: Optional[str] = None
    status: str  # VALID, EXPIRING_SOON, EXPIRED, EXPIRY_DATE_NOT_FOUND, MANUAL_VERIFICATION_REQUIRED
    days_until_expiry: Optional[int] = None
    message: str

class MismatchDetail(BaseModel):
    field_key: str
    display_field: str
    document_a_id: str
    document_a_name: str
    document_a_value: str
    document_b_id: str
    document_b_name: str
    document_b_value: str
    similarity_score: float
    mismatch_type: str  # SPELLING_VARIATION, CONFLICTING_DATE, CONFLICTING_ID, OCR_NOISE
    requires_manual_review: bool
    explanation: str

class TamperDetail(BaseModel):
    document_id: str
    document_name: str
    risk_level: str
    is_flagged: bool
    ela_score: float
    software_detected: Optional[str] = None
    anomalies: List[str] = []
    explanation: str

class PrioritizedChecklistItem(BaseModel):
    requirement_code: str
    display_name: str
    status: str  # SATISFIED, MISSING, NEEDS_REVIEW
    symbol: str  # [x], [ ], [!]
    detail: str
    is_mandatory: bool = True
    requirement_type: str = "REQUIRED"
    guide_id: Optional[str] = None

class ActionPlanItem(BaseModel):
    id: str
    priority: int
    urgency: str  # CRITICAL, WARNING, INFO
    title: str
    description: str
    issue_type: str
    guide_id: str
    action_label: str = "How to Fix This?"

class VerificationResultOut(BaseModel):
    id: str
    user_application_id: str
    overall_status: str  # COMPLETE, INCOMPLETE, REVIEW_REQUIRED
    readiness_status: str = "Action Required"  # Ready for Next Step, Action Required, Needs Manual Review, Official Verification Pending
    readiness_score: str = "0%"
    satisfied_requirements: List[ChecklistItemStatus] = []
    missing_requirements: List[ChecklistItemStatus] = []
    expired_documents: List[ExpiryDetail] = []
    expiring_soon_documents: List[ExpiryDetail] = []
    detected_mismatches: List[MismatchDetail] = []
    tampering_flags: List[TamperDetail] = []
    recommended_actions: List[str] = []
    prioritized_checklist: List[PrioritizedChecklistItem] = []
    action_plan: List[ActionPlanItem] = []
    confidence_summary: Optional[Dict[str, Any]] = None
    readiness_breakdown: Optional[Dict[str, Any]] = None
    document_evaluations: Optional[Dict[str, Any]] = None
    report_pdf_url: Optional[str] = None
    evaluated_at: datetime

    class Config:
        from_attributes = True
