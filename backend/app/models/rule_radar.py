import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RegulatoryUpdate(Base):
    __tablename__ = "regulatory_updates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    profile_code = Column(String(64), nullable=False, index=True) # e.g. FIRST_GRADUATE_APPLICATION, ALL
    category = Column(String(128), nullable=False)                 # Education, Transport, Revenue, etc.
    state = Column(String(64), default="Tamil Nadu", nullable=False, index=True)
    department = Column(String(128), nullable=False)             # Revenue Dept, DoTE, MoRTH, etc.
    
    # Statuses: New Official Update, Requirement Changed, No Confirmed Change, Verification Required
    status = Column(String(64), default="New Official Update", nullable=False, index=True)
    is_verified = Column(Boolean, default=True, nullable=False)  # True = verified official source, False = unverified
    source_authority = Column(String(255), nullable=False)       # Gazette, GO, Notification
    official_source_url = Column(String(512), nullable=True)     # Verified government URL
    effective_date = Column(String(64), nullable=True)           # e.g., "2026-06-01" or "Immediate"
    last_checked_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Change Type: ADDED, REMOVED, MODIFIED, NO_CHANGE
    change_type = Column(String(32), default="MODIFIED", nullable=False)
    previous_requirement = Column(Text, nullable=True)          # JSON or text description of old requirement
    updated_requirement = Column(Text, nullable=False)          # JSON or text description of new requirement
    impact_summary = Column(Text, nullable=False)               # What this change means for citizens
    
    version = Column(String(32), default="2026.1", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def get_previous_requirement_data(self):
        try:
            return json.loads(self.previous_requirement) if self.previous_requirement else {}
        except Exception:
            return {"description": self.previous_requirement or ""}

    def get_updated_requirement_data(self):
        try:
            return json.loads(self.updated_requirement) if self.updated_requirement else {}
        except Exception:
            return {"description": self.updated_requirement or ""}

class ApplicationProfileVersion(Base):
    __tablename__ = "application_profile_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_profile_id = Column(String(36), ForeignKey("application_profiles.id", ondelete="CASCADE"), nullable=False)
    version_tag = Column(String(32), nullable=False)            # e.g., "v1.0-2025", "v2.0-2026"
    requirements_snapshot = Column(Text, nullable=False)        # JSON serialized list of requirements
    changelog = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def get_requirements_snapshot(self):
        try:
            return json.loads(self.requirements_snapshot)
        except Exception:
            return []
