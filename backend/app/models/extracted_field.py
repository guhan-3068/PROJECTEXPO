import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False)
    
    # Standard field keys: full_name, dob, doc_number, expiry_date, issue_date, address, authority
    field_key = Column(String(64), nullable=False)
    raw_value = Column(String(512), nullable=True)
    normalized_value = Column(String(512), nullable=True)
    confidence = Column(Float, default=0.0, nullable=False)

    # Human-in-the-loop correction
    is_user_corrected = Column(Boolean, default=False, nullable=False)
    corrected_value = Column(String(512), nullable=True)
    notes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("UploadedDocument", back_populates="extracted_fields")

    @property
    def effective_value(self) -> str:
        """Returns the user-corrected value if present, else normalized, else raw."""
        if self.is_user_corrected and self.corrected_value is not None:
            return self.corrected_value.strip()
        if self.normalized_value is not None:
            return self.normalized_value.strip()
        return (self.raw_value or "").strip()
