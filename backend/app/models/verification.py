import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_application_id = Column(String(36), ForeignKey("user_applications.id", ondelete="CASCADE"), unique=True, nullable=False)

    # COMPLETE, INCOMPLETE, REVIEW_REQUIRED
    overall_status = Column(String(32), default="INCOMPLETE", nullable=False)
    readiness_status = Column(String(64), default="Action Required", nullable=True)  # Ready for Next Step, Action Required, Needs Manual Review, Official Verification Pending
    readiness_score = Column(String(16), default="0%", nullable=True)

    # JSON structures
    satisfied_requirements = Column(Text, default="[]", nullable=False)
    missing_requirements = Column(Text, default="[]", nullable=False)
    expired_documents = Column(Text, default="[]", nullable=False)
    expiring_soon_documents = Column(Text, default="[]", nullable=False)
    detected_mismatches = Column(Text, default="[]", nullable=False)
    tampering_flags = Column(Text, default="[]", nullable=False)
    recommended_actions = Column(Text, default="[]", nullable=False)
    prioritized_checklist = Column(Text, default="[]", nullable=False)
    action_plan = Column(Text, default="[]", nullable=False)
    confidence_summary = Column(Text, default="{}", nullable=True)

    report_pdf_path = Column(String(512), nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    application = relationship("UserApplication", back_populates="verification_result")

    # JSON getter / setter helpers
    def get_json_field(self, field_name: str):
        val = getattr(self, field_name, "[]")
        try:
            return json.loads(val) if val else []
        except Exception:
            return []

    def set_json_field(self, field_name: str, data):
        setattr(self, field_name, json.dumps(data, default=str))
