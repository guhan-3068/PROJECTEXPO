import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_application_id = Column(String(36), ForeignKey("user_applications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    checklist_requirement_id = Column(String(36), ForeignKey("checklist_requirements.id", ondelete="SET NULL"), nullable=True)
    
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), unique=True, nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(128), nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False)
    is_encrypted = Column(Boolean, default=True, nullable=False)

    doc_category = Column(String(64), default="UNKNOWN", nullable=False)  # PASSPORT, NATIONAL_ID, DRIVERS_LICENSE, UTILITY_BILL, BANK_STATEMENT, BIRTH_CERTIFICATE, APPLICATION_FORM, OTHER
    user_assigned_category = Column(String(64), nullable=True) # Category claimed by user during upload
    ocr_status = Column(String(32), default="PENDING", nullable=False)    # PENDING, PROCESSING, SUCCESS, FAILED
    ocr_overall_confidence = Column(Float, default=0.0, nullable=False)
    raw_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    application = relationship("UserApplication", back_populates="documents")
    user = relationship("User", back_populates="documents")
    extracted_fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    tampering_analysis = relationship("TamperingAnalysis", back_populates="document", uselist=False, cascade="all, delete-orphan")
