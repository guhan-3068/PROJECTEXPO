"""
DocVerify AI - Document Timeline & Renewal History Service
Manages lifecycle, issue & expiry dates, configurable citizen reminders (30/15/7 days),
and renewal comparisons across Indian citizen documents.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json
import uuid
import re
from sqlalchemy.orm import Session
from app.models.document import UploadedDocument
from app.models.document_timeline import DocumentTimelineRecord
from app.models.application import UserApplication, ChecklistRequirement
from app.models.extracted_field import ExtractedField
from app.services.storage_service import storage_service
from app.services.ocr_engine import ocr_engine
from app.services.field_extractor import field_extractor

# Official validity rules under Indian and Tamil Nadu regulatory frameworks
NON_EXPIRING_CATEGORIES = {
    "AADHAAR": "Under UIDAI regulations, an Aadhaar number and card have lifelong validity and do not expire. Periodic demographic updates are optional unless ordered by UIDAI.",
    "PAN_CARD": "Under CBDT Income Tax Act provisions, a PAN card is permanent and does not expire unless cancelled or surrendered.",
    "COMMUNITY_CERTIFICATE": "Under Tamil Nadu Revenue Department rules, Community / Caste Certificates (BC / MBC / SC / ST) possess lifetime validity.",
    "EDUCATIONAL_CERTIFICATE": "Academic degrees, 10th SSLC and 12th HSC mark statements have permanent lifetime validity.",
    "TRANSFER_CERTIFICATE": "Transfer Certificates (TC) represent an irreversible record of institutional leaving and do not expire.",
    "BIRTH_CERTIFICATE": "Under the Registration of Births and Deaths Act, birth certificates have permanent validity.",
    "DEATH_CERTIFICATE": "Permanent legal record; does not expire.",
    "FIRST_GRADUATE_CERTIFICATE": "Issued once for the family's first college degree candidate; does not require periodic renewal.",
    "DISABILITY_CERTIFICATE": "Permanent disability certificates do not expire unless marked temporary with a review date by a Medical Board."
}

ANNUAL_EXPIRY_CATEGORIES = {
    "INCOME_CERTIFICATE": "Under Tamil Nadu Revenue rules, Income Certificates are strictly valid for 1 Financial Year (April 1 to March 31). Renewal is required annually for scholarships and college fee waivers."
}

MULTI_YEAR_EXPIRY_CATEGORIES = {
    "DRIVING_LICENSE": "Under MoRTH Motor Vehicles Act rules, non-transport licenses are valid for 20 years or until age 40 (subsequently 10 years up to age 50, then 5 years).",
    "PASSPORT": "Regular adult Indian passports are valid for 10 years from the date of issue. Minor passports are valid for 5 years.",
    "RESIDENCE_CERTIFICATE": "State nativity / residence certificates for employment or welfare are valid for 6 months to 1 year depending on specific recruitment notices."
}

class TimelineService:
    """
    Tracks document issuance, expiration, renewal lineage, and application impact.
    """

    def _parse_date_safe(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        date_str = date_str.strip()
        patterns = [
            "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
            "%Y/%m/%d", "%b %d, %Y", "%d %b %Y"
        ]
        for p in patterns:
            try:
                dt = datetime.strptime(date_str, p)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        # Fallback regex for YYYY
        m = re.search(r'\b(20\d{2})\b', date_str)
        if m:
            year = int(m.group(1))
            return datetime(year, 1, 1, tzinfo=timezone.utc)
        return None

    def _determine_validity_status(
        self,
        doc_category: str,
        expiry_date_str: Optional[str],
        issue_date_str: Optional[str],
        reminder_days: int = 30
    ) -> tuple[str, str, Optional[int]]:
        """
        Determines: (status, explanation, days_until_expiry)
        Status is one of:
        - ACTIVE
        - EXPIRING_SOON
        - EXPIRED
        - NO_EXPIRY
        - VALIDITY_NEEDS_CONFIRMATION
        """
        cat = doc_category.upper()

        # 1. Non-expiring documents
        if cat in NON_EXPIRING_CATEGORIES:
            return "NO_EXPIRY", NON_EXPIRING_CATEGORIES[cat], None

        # 2. Document types that have definite expiration periods
        is_annual = cat in ANNUAL_EXPIRY_CATEGORIES
        is_multi_year = cat in MULTI_YEAR_EXPIRY_CATEGORIES

        exp_dt = self._parse_date_safe(expiry_date_str)

        # For Income Certificate, if no expiry date was parsed from text, calculate financial year end from issue date
        if is_annual and not exp_dt and issue_date_str:
            iss_dt = self._parse_date_safe(issue_date_str)
            if iss_dt:
                # If issued in May 2025, FY end is March 31, 2026
                fy_year = iss_dt.year if iss_dt.month <= 3 else iss_dt.year + 1
                exp_dt = datetime(fy_year, 3, 31, 23, 59, 59, tzinfo=timezone.utc)
                expiry_date_str = exp_dt.strftime("%Y-%m-%d")

        if exp_dt:
            now = datetime.now(timezone.utc)
            diff = (exp_dt - now).days

            if diff < 0:
                explanation = f"Expired {abs(diff)} day(s) ago (on {exp_dt.strftime('%d-%b-%Y')}). Check applicable authority rules before submitting; a renewed certificate may be required."
                return "EXPIRED", explanation, diff
            elif diff <= reminder_days:
                explanation = f"Expiring in {diff} day(s) (on {exp_dt.strftime('%d-%b-%Y')}). Approaching renewal cutoff; initiate renewal via e-Sevai or RTO soon."
                return "EXPIRING_SOON", explanation, diff
            else:
                explanation = f"Currently active and valid. Official validity extends until {exp_dt.strftime('%d-%b-%Y')} ({diff} days remaining)."
                return "ACTIVE", explanation, diff

        # If it's supposed to expire but no date was detected
        if is_annual or is_multi_year:
            explanation = "This document category typically has a limited validity period, but no specific expiry date could be extracted from the scan. Validity Needs Confirmation from the issuing authority."
            return "VALIDITY_NEEDS_CONFIRMATION", explanation, None

        # Unknown / Unconfirmed category
        explanation = "Official validity depends on the specific department, scheme guidelines, and issuing authority. Validity Needs Confirmation before application submission."
        return "VALIDITY_NEEDS_CONFIRMATION", explanation, None

    def sync_timeline_for_user(self, user_id: str, db: Session) -> List[Dict[str, Any]]:
        """
        Synchronizes document timeline records with uploaded documents for the user.
        """
        user_docs = db.query(UploadedDocument).filter(UploadedDocument.user_id == user_id).all()
        records = []

        for d in user_docs:
            rec = db.query(DocumentTimelineRecord).filter(DocumentTimelineRecord.document_id == d.id).first()
            
            # Extract issue and expiry fields if present
            issue_field = next((f.effective_value for f in d.extracted_fields if f.field_key == "issue_date" and f.effective_value), None)
            expiry_field = next((f.effective_value for f in d.extracted_fields if f.field_key == "expiry_date" and f.effective_value), None)

            if not rec:
                status, expl, _ = self._determine_validity_status(
                    doc_category=d.doc_category,
                    expiry_date_str=expiry_field,
                    issue_date_str=issue_field,
                    reminder_days=30
                )
                rec = DocumentTimelineRecord(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    document_id=d.id,
                    doc_category=d.doc_category,
                    document_name=d.original_filename,
                    issue_date=issue_field,
                    expiry_date=expiry_field,
                    validity_status=status,
                    validity_explanation=expl,
                    reminder_days_configured=30,
                    is_reminder_enabled=True,
                    renewal_status="NONE"
                )
                db.add(rec)
            else:
                # Update existing record if dates changed
                if not rec.issue_date and issue_field:
                    rec.issue_date = issue_field
                if not rec.expiry_date and expiry_field:
                    rec.expiry_date = expiry_field
                
                status, expl, _ = self._determine_validity_status(
                    doc_category=rec.doc_category,
                    expiry_date_str=rec.expiry_date,
                    issue_date_str=rec.issue_date,
                    reminder_days=rec.reminder_days_configured
                )
                rec.validity_status = status
                rec.validity_explanation = expl

        db.commit()
        return self.get_timeline_records(user_id=user_id, db=db)

    def get_timeline_records(
        self,
        user_id: str,
        db: Session,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns all timeline items for user with calculated days remaining and application linkages.
        """
        query = db.query(DocumentTimelineRecord).filter(DocumentTimelineRecord.user_id == user_id)
        
        if status_filter and status_filter.upper() != "ALL":
            query = query.filter(DocumentTimelineRecord.validity_status == status_filter.upper())

        records = query.order_by(DocumentTimelineRecord.created_at.desc()).all()
        output = []

        now = datetime.now(timezone.utc)
        for r in records:
            exp_dt = self._parse_date_safe(r.expiry_date)
            days_remaining = (exp_dt - now).days if exp_dt else None

            # Find affected applications that include this document
            affected_apps = self.get_affected_applications(document_id=r.document_id, db=db)

            # Previous document info if renewed
            prev_doc_name = None
            if r.previous_document_id:
                prev_doc = db.query(UploadedDocument).filter(UploadedDocument.id == r.previous_document_id).first()
                if prev_doc:
                    prev_doc_name = prev_doc.original_filename

            output.append({
                "id": r.id,
                "document_id": r.document_id,
                "document_name": r.document_name,
                "doc_category": r.doc_category,
                "issue_date": r.issue_date,
                "expiry_date": r.expiry_date,
                "validity_status": r.validity_status,
                "validity_explanation": r.validity_explanation,
                "days_remaining": days_remaining,
                "reminder_days_configured": r.reminder_days_configured,
                "is_reminder_enabled": r.is_reminder_enabled,
                "previous_document_id": r.previous_document_id,
                "previous_document_name": prev_doc_name,
                "renewal_status": r.renewal_status,
                "renewal_date": r.renewal_date.isoformat() if r.renewal_date else None,
                "comparison_data": r.get_comparison_data(),
                "affected_applications": affected_apps,
                "created_at": r.created_at.isoformat()
            })

        return output

    def update_dates_manually(
        self,
        document_id: str,
        issue_date: Optional[str],
        expiry_date: Optional[str],
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Allows citizens to review and manually correct extracted issue/expiry dates.
        """
        rec = db.query(DocumentTimelineRecord).filter(
            DocumentTimelineRecord.document_id == document_id,
            DocumentTimelineRecord.user_id == user_id
        ).first()

        if not rec:
            raise ValueError("Document timeline record not found")

        rec.issue_date = issue_date.strip() if issue_date else None
        rec.expiry_date = expiry_date.strip() if expiry_date else None

        status, expl, _ = self._determine_validity_status(
            doc_category=rec.doc_category,
            expiry_date_str=rec.expiry_date,
            issue_date_str=rec.issue_date,
            reminder_days=rec.reminder_days_configured
        )
        rec.validity_status = status
        rec.validity_explanation = expl
        rec.updated_at = datetime.now(timezone.utc)

        # Also sync extracted field in document
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if doc:
            for f in doc.extracted_fields:
                if f.field_key == "issue_date" and issue_date:
                    f.is_user_corrected = True
                    f.corrected_value = issue_date
                elif f.field_key == "expiry_date" and expiry_date:
                    f.is_user_corrected = True
                    f.corrected_value = expiry_date

        db.commit()
        return {
            "success": True,
            "document_id": document_id,
            "issue_date": rec.issue_date,
            "expiry_date": rec.expiry_date,
            "validity_status": rec.validity_status,
            "validity_explanation": rec.validity_explanation
        }

    def set_reminder_preference(
        self,
        record_id: str,
        reminder_days: int,
        is_enabled: bool,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Configures citizen reminders for 30, 15, or 7 days before expiry."""
        rec = db.query(DocumentTimelineRecord).filter(
            DocumentTimelineRecord.id == record_id,
            DocumentTimelineRecord.user_id == user_id
        ).first()
        if not rec:
            raise ValueError("Record not found")

        rec.reminder_days_configured = reminder_days
        rec.is_reminder_enabled = is_enabled
        
        status, expl, _ = self._determine_validity_status(
            doc_category=rec.doc_category,
            expiry_date_str=rec.expiry_date,
            issue_date_str=rec.issue_date,
            reminder_days=reminder_days
        )
        rec.validity_status = status
        rec.validity_explanation = expl
        db.commit()

        return {
            "id": rec.id,
            "reminder_days_configured": rec.reminder_days_configured,
            "is_reminder_enabled": rec.is_reminder_enabled,
            "validity_status": rec.validity_status
        }

    def upload_renewed_document(
        self,
        old_document_id: str,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Uploads a renewed replacement document, runs OCR, links old & new versions in lineage,
        generates an explainable side-by-side comparison, and replaces/updates application requirements.
        """
        old_doc = db.query(UploadedDocument).filter(
            UploadedDocument.id == old_document_id,
            UploadedDocument.user_id == user_id
        ).first()

        if not old_doc:
            raise ValueError("Prior document record not found")

        # 1. Save renewed document via encrypted storage
        stored_name, enc_path, sha256_hash = storage_service.save_document(filename, file_bytes)
        mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/jpeg"

        # 2. OCR and Field Extraction
        ocr_res = ocr_engine.extract_text(file_bytes, mime_type)
        raw_text = ocr_res.get("raw_text", "")
        ocr_conf = ocr_res.get("confidence", 0.90)

        detected_cat, _ = field_extractor.classify_document(raw_text, old_doc.doc_category)
        fields = field_extractor.extract_fields(raw_text)

        # 3. Create new UploadedDocument record attached to the same application
        new_doc = UploadedDocument(
            id=str(uuid.uuid4()),
            user_application_id=old_doc.user_application_id,
            user_id=user_id,
            original_filename=filename,
            stored_filename=stored_name,
            file_path=enc_path,
            file_size_bytes=len(file_bytes),
            mime_type=mime_type,
            file_hash_sha256=sha256_hash,
            is_encrypted=True,
            doc_category=detected_cat,
            user_assigned_category=old_doc.user_assigned_category,
            ocr_status="SUCCESS",
            ocr_overall_confidence=ocr_conf,
            raw_text=raw_text
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        # Add extracted fields
        for f in fields:
            ef = ExtractedField(
                id=str(uuid.uuid4()),
                document_id=new_doc.id,
                field_key=f["field_key"],
                raw_value=f["raw_value"],
                normalized_value=f["normalized_value"],
                confidence=f["confidence"]
            )
            db.add(ef)
        db.commit()

        # 4. Generate Side-by-Side Comparison
        old_fields = {f.field_key: f.effective_value for f in old_doc.extracted_fields}
        new_fields = {f["field_key"]: f["normalized_value"] or f["raw_value"] for f in fields}

        old_issue = old_fields.get("issue_date", "<Not detected>")
        new_issue = new_fields.get("issue_date", "<Not detected>")
        old_expiry = old_fields.get("expiry_date", "<Not detected>")
        new_expiry = new_fields.get("expiry_date", "<Not detected>")
        old_num = old_fields.get("doc_number", "<Not detected>")
        new_num = new_fields.get("doc_number", "<Not detected>")

        comparison = {
            "comparison_summary": "Renewed certificate uploaded and compared against prior version.",
            "field_diffs": [
                {
                    "field": "Document / Reference Number",
                    "old_version": old_num,
                    "new_version": new_num,
                    "is_changed": old_num != new_num and new_num != "<Not detected>"
                },
                {
                    "field": "Issue Date",
                    "old_version": old_issue,
                    "new_version": new_issue,
                    "is_changed": old_issue != new_issue and new_issue != "<Not detected>"
                },
                {
                    "field": "Expiry Date",
                    "old_version": old_expiry,
                    "new_version": new_expiry,
                    "is_changed": old_expiry != new_expiry and new_expiry != "<Not detected>"
                },
                {
                    "field": "Applicant Name",
                    "old_version": old_fields.get("full_name", "<Not detected>"),
                    "new_version": new_fields.get("full_name", "<Not detected>"),
                    "is_changed": old_fields.get("full_name") != new_fields.get("full_name")
                }
            ],
            "renewal_timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 5. Create new Timeline Record linking to old
        new_status, new_expl, _ = self._determine_validity_status(
            doc_category=new_doc.doc_category,
            expiry_date_str=new_expiry if new_expiry != "<Not detected>" else None,
            issue_date_str=new_issue if new_issue != "<Not detected>" else None,
            reminder_days=30
        )

        # Mark old timeline record as RENEWED
        old_rec = db.query(DocumentTimelineRecord).filter(DocumentTimelineRecord.document_id == old_doc.id).first()
        if old_rec:
            old_rec.renewal_status = "RENEWED_AND_VERIFIED"
            old_rec.validity_explanation = f"Superseded by renewed certificate '{new_doc.original_filename}'."

        new_rec = DocumentTimelineRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            document_id=new_doc.id,
            doc_category=new_doc.doc_category,
            document_name=new_doc.original_filename,
            issue_date=new_issue if new_issue != "<Not detected>" else None,
            expiry_date=new_expiry if new_expiry != "<Not detected>" else None,
            validity_status=new_status,
            validity_explanation=new_expl,
            reminder_days_configured=30,
            is_reminder_enabled=True,
            previous_document_id=old_doc.id,
            renewal_date=datetime.now(timezone.utc),
            renewal_status="RENEWED_AND_VERIFIED",
            comparison_notes=json.dumps(comparison)
        )
        db.add(new_rec)
        db.commit()

        return {
            "success": True,
            "old_document_id": old_doc.id,
            "new_document_id": new_doc.id,
            "new_document_name": new_doc.original_filename,
            "validity_status": new_rec.validity_status,
            "validity_explanation": new_rec.validity_explanation,
            "comparison": comparison
        }

    def get_affected_applications(self, document_id: str, db: Session) -> List[Dict[str, Any]]:
        """
        Determines which citizen applications may be affected if this document is expired or near expiry.
        """
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if not doc:
            return []

        # Find application containing this document
        app = db.query(UserApplication).filter(UserApplication.id == doc.user_application_id).first()
        if not app:
            return []

        # Check if the document matches any mandatory requirement in the application
        profile = app.profile
        affected = []

        if profile:
            for req in profile.requirements:
                cats = [c.upper() for c in req.get_accepted_categories()]
                if doc.doc_category.upper() in cats:
                    affected.append({
                        "application_id": app.id,
                        "reference_number": app.reference_number,
                        "profile_name": profile.name,
                        "jurisdiction": profile.jurisdiction,
                        "requirement_name": req.display_name,
                        "is_mandatory": req.is_mandatory,
                        "impact_description": (
                            f"Mandatory requirement '{req.display_name}' depends on this certificate."
                            if req.is_mandatory else
                            f"Optional/supporting requirement '{req.display_name}' is associated with this document."
                        )
                    })

        return affected

timeline_service = TimelineService()
