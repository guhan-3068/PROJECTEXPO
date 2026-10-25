import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DocumentTimelineRecord(Base):
    __tablename__ = "document_timeline_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    doc_category = Column(String(64), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    
    issue_date = Column(String(64), nullable=True)   # Normalized YYYY-MM-DD or DD/MM/YYYY
    expiry_date = Column(String(64), nullable=True)  # Normalized YYYY-MM-DD or DD/MM/YYYY (None if non-expiring)
    
    # Statuses: ACTIVE, EXPIRING_SOON, EXPIRED, NO_EXPIRY, VALIDITY_NEEDS_CONFIRMATION, RENEWAL_IN_PROGRESS
    validity_status = Column(String(64), default="VALIDITY_NEEDS_CONFIRMATION", nullable=False, index=True)
    validity_explanation = Column(Text, nullable=False)
    
    # Configurable notification window: 30, 15, or 7 days
    reminder_days_configured = Column(Integer, default=30, nullable=False)
    is_reminder_enabled = Column(Boolean, default=True, nullable=False)
    
    # Renewal tracking
    previous_document_id = Column(String(36), nullable=True) # ID of prior expired/renewed document
    renewal_date = Column(DateTime, nullable=True)
    renewal_status = Column(String(32), default="NONE", nullable=False) # NONE, IN_PROGRESS, RENEWED_AND_VERIFIED
    comparison_notes = Column(Text, nullable=True) # JSON or markdown string comparing old vs new version
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User")
    document = relationship("UploadedDocument")

    def get_comparison_data(self):
        try:
            return json.loads(self.comparison_notes) if self.comparison_notes else {}
        except Exception:
            return {"notes": self.comparison_notes or ""}
