from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ExtractedFieldOut(BaseModel):
    id: str
    field_key: str
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float = 0.0
    is_user_corrected: bool = False
    corrected_value: Optional[str] = None
    effective_value: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class FieldCorrectionRequest(BaseModel):
    field_key: str
    corrected_value: str = Field(..., min_length=1, max_length=512)
    notes: Optional[str] = None

class TamperingSummaryOut(BaseModel):
    is_flagged: bool
    risk_level: str
    ela_anomaly_score: float
    metadata_software_detected: Optional[str] = None
    detected_anomalies: List[str] = []
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: str
    user_application_id: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    doc_category: str
    user_assigned_category: Optional[str] = None
    ocr_status: str
    ocr_overall_confidence: float
    created_at: datetime
    extracted_fields: List[ExtractedFieldOut] = []
    tampering_analysis: Optional[TamperingSummaryOut] = None

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentOut
