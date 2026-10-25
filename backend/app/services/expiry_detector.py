from datetime import date
from typing import List, Dict, Any, Optional
from app.models.document import UploadedDocument
from app.utils.dates import parse_date_string, evaluate_expiry_status
from app.config import settings

# Categories that typically do not have expiry dates (lifetime / permanent in India)
NON_EXPIRING_CATEGORIES = {
    "BIRTH_CERTIFICATE",
    "DEATH_CERTIFICATE",
    "APPLICATION_FORM",
    "AADHAAR",
    "NATIONAL_ID",
    "PAN_CARD",
    "COMMUNITY_CERTIFICATE",
    "CASTE_CERTIFICATE",
    "FIRST_GRADUATE_CERTIFICATE",
    "TRANSFER_CERTIFICATE",
    "EDUCATIONAL_CERTIFICATE",
    "RATION_CARD",
    "DISABILITY_CERTIFICATE",
    "BONAFIDE_CERTIFICATE"
}

class ExpiryDetector:
    """
    Evaluates temporal document validity.
    Guarantees deterministic date calculation with zero hallucinated dates.
    """

    def analyze_documents(
        self,
        documents: List[UploadedDocument],
        warning_days: Optional[int] = None,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analyzes expiry for a collection of documents.
        Returns:
            {
                "expired": [ExpiryDetail],
                "expiring_soon": [ExpiryDetail],
                "valid": [ExpiryDetail],
                "not_found": [ExpiryDetail],
                "all_details": [ExpiryDetail]
            }
        """
        days_threshold = warning_days or settings.EXPIRY_WARNING_DAYS
        ref_date = reference_date or date.today()

        expired = []
        expiring_soon = []
        valid = []
        not_found = []
        all_details = []

        for doc in documents:
            # 1. Locate expiry_date field in extracted fields
            expiry_field = None
            for field in doc.extracted_fields:
                if field.field_key == "expiry_date":
                    expiry_field = field
                    break

            category = doc.doc_category.upper()
            
            if expiry_field and expiry_field.effective_value:
                raw_exp = expiry_field.effective_value
                parsed_date = parse_date_string(raw_exp)
                if parsed_date:
                    status, remaining_days, msg = evaluate_expiry_status(
                        parsed_date,
                        warning_days=days_threshold,
                        reference_date=ref_date
                    )
                    item = {
                        "document_id": doc.id,
                        "document_name": doc.original_filename,
                        "doc_category": doc.doc_category,
                        "expiry_date": parsed_date.isoformat(),
                        "status": status,
                        "days_until_expiry": remaining_days,
                        "message": msg
                    }
                    all_details.append(item)
                    if status == "EXPIRED":
                        expired.append(item)
                    elif status == "EXPIRING_SOON":
                        expiring_soon.append(item)
                    else:
                        valid.append(item)
                    continue
                else:
                    # Date string was present but ambiguous / unparseable
                    item = {
                        "document_id": doc.id,
                        "document_name": doc.original_filename,
                        "doc_category": doc.doc_category,
                        "expiry_date": raw_exp,
                        "status": "MANUAL_VERIFICATION_REQUIRED",
                        "days_until_expiry": None,
                        "message": f"Expiry date '{raw_exp}' is ambiguous and requires human verification"
                    }
                    all_details.append(item)
                    continue

            # No expiry field found
            if category in NON_EXPIRING_CATEGORIES:
                item = {
                    "document_id": doc.id,
                    "document_name": doc.original_filename,
                    "doc_category": doc.doc_category,
                    "expiry_date": None,
                    "status": "VALID",
                    "days_until_expiry": None,
                    "message": f"{doc.doc_category.replace('_', ' ').title()} is a non-expiring document type"
                }
                valid.append(item)
                all_details.append(item)
            else:
                item = {
                    "document_id": doc.id,
                    "document_name": doc.original_filename,
                    "doc_category": doc.doc_category,
                    "expiry_date": None,
                    "status": "EXPIRY_DATE_NOT_FOUND",
                    "days_until_expiry": None,
                    "message": "No expiry date found in document text"
                }
                not_found.append(item)
                all_details.append(item)

        return {
            "expired": expired,
            "expiring_soon": expiring_soon,
            "valid": valid,
            "not_found": not_found,
            "all_details": all_details
        }

expiry_detector = ExpiryDetector()
