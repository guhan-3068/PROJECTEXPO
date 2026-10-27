import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ApplicationProfile(Base):
    __tablename__ = "application_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    jurisdiction = Column(String(64), nullable=False)  # e.g., US, UK, IN, GLOBAL
    category = Column(String(128), nullable=False)      # e.g., Identity, Travel, Employment, Education
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    official_source_url = Column(String(512), nullable=True)
    last_verified_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    next_review_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    status = Column(String(32), default="Current", nullable=True)  # Current, Review Needed, Outdated
    eligibility_criteria = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    requirements = relationship("ChecklistRequirement", back_populates="profile", cascade="all, delete-orphan", order_by="ChecklistRequirement.sort_order")
    user_applications = relationship("UserApplication", back_populates="profile")

class ChecklistRequirement(Base):
    __tablename__ = "checklist_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_profile_id = Column(String(36), ForeignKey("application_profiles.id", ondelete="CASCADE"), nullable=False)
    requirement_code = Column(String(64), nullable=False)  # e.g., PROOF_OF_IDENTITY, PROOF_OF_ADDRESS, DOB_PROOF, APPLICATION_FORM
    display_name = Column(String(255), nullable=False)     # e.g., Proof of Identity
    description = Column(Text, nullable=True)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    requirement_type = Column(String(32), default="REQUIRED", nullable=False)  # REQUIRED, CONDITIONALLY_REQUIRED, OPTIONAL
    accepted_categories = Column(Text, nullable=False, default="[]")  # JSON-serialized list of doc types
    min_validity_days = Column(Integer, default=0, nullable=False)
    allow_manual_override = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    # Dynamic Requirement Management Fields (Indian Citizen Portal)
    alternative_documents = Column(Text, nullable=False, default="[]")  # JSON-serialized list of alternative doc names
    eligibility_conditions = Column(Text, nullable=True)                 # e.g., "Family income < 2.5 LPA; First graduate in family"
    validity_rules = Column(Text, nullable=True)                         # e.g., "Valid for 1 financial year; annual renewal required"
    accepted_formats = Column(String(128), default="PDF, JPG, JPEG, PNG (Max 15MB)", nullable=True)
    official_source_url = Column(String(512), nullable=True)             # e.g., "https://www.tnesevai.tn.gov.in"
    last_verified_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    next_review_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    status = Column(String(32), default="Current", nullable=True)       # Current, Review Needed, Outdated

    profile = relationship("ApplicationProfile", back_populates="requirements")

    def get_accepted_categories(self):
        try:
            return json.loads(self.accepted_categories)
        except Exception:
            return []

    def set_accepted_categories(self, categories):
        self.accepted_categories = json.dumps(categories)

    def get_alternative_documents(self):
        try:
            return json.loads(self.alternative_documents) if self.alternative_documents else []
        except Exception:
            return []

    def set_alternative_documents(self, alts):
        self.alternative_documents = json.dumps(alts)

class UserApplication(Base):
    __tablename__ = "user_applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_profile_id = Column(String(36), ForeignKey("application_profiles.id"), nullable=False)
    reference_number = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(String(32), default="DRAFT", nullable=False)  # DRAFT, SUBMITTED, INCOMPLETE, REVIEW_REQUIRED, APPROVED, REJECTED
    readiness_status = Column(String(64), default="Action Required", nullable=True)  # Ready for Next Step, Action Required, Needs Manual Review, Official Verification Pending
    state = Column(String(64), default="Tamil Nadu", nullable=True)
    district = Column(String(64), default="Chennai", nullable=True)
    issuing_authority = Column(String(128), nullable=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    profile = relationship("ApplicationProfile", back_populates="user_applications")
    documents = relationship("UploadedDocument", back_populates="application", cascade="all, delete-orphan")
    verification_result = relationship("VerificationResult", back_populates="application", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("AdminReview", back_populates="application", cascade="all, delete-orphan")

class AdminReview(Base):
    __tablename__ = "admin_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_application_id = Column(String(36), ForeignKey("user_applications.id", ondelete="CASCADE"), nullable=False)
    admin_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    previous_status = Column(String(32), nullable=False)
    new_status = Column(String(32), nullable=False)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    application = relationship("UserApplication", back_populates="reviews")
    admin = relationship("User")
