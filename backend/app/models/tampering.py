import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class TamperingAnalysis(Base):
    __tablename__ = "tampering_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), unique=True, nullable=False)

    is_flagged = Column(Boolean, default=False, nullable=False)
    risk_level = Column(String(32), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH
    authenticity_result = Column(String(64), default="No obvious manipulation detected", nullable=False)  # No obvious manipulation detected, Potential manipulation detected, Inconclusive — further verification required
    ai_generation_screening = Column(String(64), default="No synthetic generative signatures identified", nullable=False)  # No synthetic generative signatures identified, Potential synthetic/generative artifacts detected, Inconclusive
    digital_signature_status = Column(String(64), default="No digital signature (Standard scan/copy)", nullable=False)
    ela_anomaly_score = Column(Float, default=0.0, nullable=False)
    metadata_software_detected = Column(String(255), nullable=True)  # e.g., "Adobe Photoshop 2024", "Canva", "GIMP"
    detected_anomalies = Column(Text, default="[]", nullable=False)  # JSON-encoded list of specific flags
    visual_structure_evidence = Column(Text, default="[]", nullable=False)  # JSON list
    metadata_evidence = Column(Text, default="[]", nullable=False)          # JSON list
    explanation = Column(Text, nullable=True)                       # Explainable reasoning for human reviewer
    ela_artifact_path = Column(String(512), nullable=True)           # Path to visual diff image
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("UploadedDocument", back_populates="tampering_analysis")

    def get_detected_anomalies(self):
        try:
            return json.loads(self.detected_anomalies)
        except Exception:
            return []

    def set_detected_anomalies(self, anomalies):
        self.detected_anomalies = json.dumps(anomalies)

    def get_visual_structure_evidence(self):
        try:
            return json.loads(self.visual_structure_evidence) if self.visual_structure_evidence else []
        except Exception:
            return []

    def set_visual_structure_evidence(self, ev):
        self.visual_structure_evidence = json.dumps(ev)

    def get_metadata_evidence(self):
        try:
            return json.loads(self.metadata_evidence) if self.metadata_evidence else []
        except Exception:
            return []

    def set_metadata_evidence(self, ev):
        self.metadata_evidence = json.dumps(ev)
