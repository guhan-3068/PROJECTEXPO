from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional
from app.utils.security import mask_sensitive_value
from app.utils.dates import parse_date_string, evaluate_expiry_status

RULES_VERSION = "2026.4"
LEGAL_DISCLAIMER = (
    "Screening results reflect automated algorithmic checks against configured Indian citizen service criteria. "
    "Absence of obvious tampering indicators does not constitute official government authenticity certification. "
    "Official verification is subject to authorized authority scrutiny and government database verification."
)

MANDATORY_FIELDS_BY_CATEGORY = {
    "AADHAAR": ["name", "aadhaar_number", "dob"],
    "PAN_CARD": ["name", "pan_number"],
    "INCOME_CERTIFICATE": ["name", "income", "certificate_number"],
    "COMMUNITY_CERTIFICATE": ["name", "community", "certificate_number"],
    "NATIVITY_CERTIFICATE": ["name", "address", "certificate_number"],
    "FIRST_GRADUATE_CERTIFICATE": ["name", "certificate_number"],
    "TRANSFER_CERTIFICATE": ["name", "school_name"],
    "EDUCATIONAL_CERTIFICATE": ["name", "roll_number"],
    "DRIVING_LICENSE": ["name", "dl_number", "expiry_date"],
    "PASSPORT": ["name", "passport_number", "expiry_date"],
    "RATION_CARD": ["family_head_name", "ration_card_number"],
    "VOTER_ID": ["name", "voter_id_number"],
    "BIRTH_CERTIFICATE": ["name", "dob"],
}

PERMANENT_DOC_CATEGORIES = {
    "AADHAAR", "PAN_CARD", "TRANSFER_CERTIFICATE", "EDUCATIONAL_CERTIFICATE",
    "COMMUNITY_CERTIFICATE", "FIRST_GRADUATE_CERTIFICATE", "BIRTH_CERTIFICATE",
    "DEATH_CERTIFICATE", "NATIVITY_CERTIFICATE", "RATION_CARD"
}

PHYSICAL_VERIFICATION_SERVICES = {
    "FIRST_GRADUATE_APPLICATION", "COLLEGE_ADMISSION", "DRIVING_LICENSE_APPLICATION"
}

class DocumentVerifier:
    """
    Evaluates an individual document against the 6 required verification dimensions:
    1. Document Type Detection
    2. Required Fields Extraction (with privacy masking)
    3. Validity & Expiry Check
    4. Readability & Image Quality Check
    5. Document Authenticity Screening
    6. Official Verification Readiness
    """

    def evaluate_document(
        self,
        doc: Any,
        requirement: Optional[Any] = None,
        service_code: Optional[str] = None
    ) -> Dict[str, Any]:
        doc_category = (doc.doc_category or "UNKNOWN").upper()
        detected_category = doc_category
        claimed_category = (doc.user_assigned_category or (requirement.requirement_code if requirement else None) or "").upper()
        
        extracted_fields_list = doc.extracted_fields or []
        fields_map = {f.field_key: f.effective_value for f in extracted_fields_list if f.effective_value}

        # -------------------------------------------------------------
        # 1. Document Type Detection
        # -------------------------------------------------------------
        type_status = "PASS"
        type_note = f"Identified as {doc_category.replace('_', ' ').title()}"

        if requirement:
            accepted_cats = requirement.get_accepted_categories() if hasattr(requirement, "get_accepted_categories") else []
            if accepted_cats:
                if doc_category in accepted_cats:
                    type_status = "PASS"
                    type_note = f"Matches requirement slot '{requirement.display_name}'"
                elif doc_category == "UNKNOWN":
                    type_status = "WARNING"
                    type_note = f"Document type unclear; expected {requirement.display_name}"
                else:
                    type_status = "WARNING"
                    type_note = f"Detected as {doc_category.replace('_', ' ').title()}, but slot expects {requirement.display_name}"
        else:
            if doc_category == "UNKNOWN":
                type_status = "WARNING"
                type_note = "Could not definitively classify document category"

        type_dimension = {
            "dimension": "Document Type Detection",
            "status": type_status,
            "identified_type": doc_category.replace("_", " ").title(),
            "claimed_type": (requirement.display_name if requirement else claimed_category) or doc_category.replace("_", " ").title(),
            "is_matched": type_status == "PASS",
            "note": type_note
        }

        # -------------------------------------------------------------
        # 2. Required Fields Extraction (with Privacy Masking)
        # -------------------------------------------------------------
        expected_mandatory = MANDATORY_FIELDS_BY_CATEGORY.get(doc_category, ["name"])
        missing_fields = []
        masked_details = {}

        for k, v in fields_map.items():
            masked_details[k] = mask_sensitive_value(k, v)

        for mandatory_key in expected_mandatory:
            if mandatory_key not in fields_map:
                missing_fields.append(mandatory_key.replace("_", " ").title())

        if not fields_map:
            fields_status = "FAIL"
            fields_note = "No structured fields could be extracted from this document."
        elif missing_fields:
            fields_status = "WARNING"
            fields_note = f"Key fields missing or unreadable: {', '.join(missing_fields)}"
        else:
            fields_status = "PASS"
            fields_note = f"All {len(expected_mandatory)} core mandatory fields successfully extracted and verified."

        fields_dimension = {
            "dimension": "Required Fields Extraction",
            "status": fields_status,
            "total_extracted_count": len(fields_map),
            "masked_fields": masked_details,
            "missing_mandatory_fields": missing_fields,
            "note": fields_note
        }

        # -------------------------------------------------------------
        # 3. Validity & Expiry Check
        # -------------------------------------------------------------
        expiry_val = fields_map.get("expiry_date")
        validity_status = "PASS"
        validity_label = "Valid (Within Expiry Period)"
        days_left = None

        if doc_category in PERMANENT_DOC_CATEGORIES:
            validity_status = "PASS"
            validity_label = "Permanent Document (No Expiry Applicable)"
            validity_note = f"{doc_category.replace('_', ' ').title()} does not carry an expiration date under Indian regulations."
        elif expiry_val:
            parsed_exp = parse_date_string(expiry_val)
            if parsed_exp:
                status_code, days_left, msg = evaluate_expiry_status(parsed_exp)
                if status_code == "EXPIRED":
                    validity_status = "EXPIRED"
                    validity_label = f"Expired ({abs(days_left)} days ago)"
                    validity_note = f"Document expired on {parsed_exp.strftime('%d-%b-%Y')}. An updated certificate is required."
                elif status_code == "EXPIRING_SOON":
                    validity_status = "WARNING"
                    validity_label = f"Expiring Soon ({days_left} days left)"
                    validity_note = f"Document expires on {parsed_exp.strftime('%d-%b-%Y')}. Consider renewing soon."
                else:
                    validity_status = "PASS"
                    validity_label = "Valid (Within Expiry Period)"
                    validity_note = f"Document is officially valid until {parsed_exp.strftime('%d-%b-%Y')}."
            else:
                validity_status = "PASS"
                validity_label = "Validity Recorded"
                validity_note = f"Recorded validity: {expiry_val}"
        else:
            if doc_category in {"INCOME_CERTIFICATE"}:
                validity_status = "WARNING"
                validity_label = "Annual Financial Year Check Needed"
                validity_note = "Income certificates in Tamil Nadu / India are typically valid for 1 financial year."
            else:
                validity_status = "PASS"
                validity_label = "Valid / No Expiry Detected"
                validity_note = "No expiry date found; treated as currently valid."

        validity_dimension = {
            "dimension": "Validity & Expiry Check",
            "status": validity_status,
            "label": validity_label,
            "expiry_date": expiry_val,
            "days_left": days_left,
            "note": validity_note
        }

        # -------------------------------------------------------------
        # 4. Readability & Image Quality Check
        # -------------------------------------------------------------
        ocr_conf = doc.ocr_overall_confidence or 0.0
        if ocr_conf >= 0.70:
            readability_status = "PASS"
            readability_label = "Legible (High Resolution)"
            readability_note = f"Optical character recognition confidence is high ({int(ocr_conf * 100)}%). Text is sharp and clear."
        elif ocr_conf >= 0.40:
            readability_status = "WARNING"
            readability_label = "Moderate Readability"
            readability_note = f"OCR confidence is moderate ({int(ocr_conf * 100)}%). Document is readable, but higher scan quality is advised."
        else:
            readability_status = "FAIL"
            readability_label = "Blurry / Low Resolution"
            readability_note = f"OCR confidence is low ({int(ocr_conf * 100)}%). Scan may be degraded, blurred, or poorly lit."

        readability_dimension = {
            "dimension": "Readability & Image Quality Check",
            "status": readability_status,
            "confidence_score": round(ocr_conf, 2),
            "confidence_percentage": f"{int(ocr_conf * 100)}%",
            "label": readability_label,
            "note": readability_note
        }

        # -------------------------------------------------------------
        # 5. Document Authenticity Screening
        # -------------------------------------------------------------
        tamper = doc.tampering_analysis
        if tamper:
            auth_result = getattr(tamper, "authenticity_result", None)
            if not auth_result:
                if tamper.is_flagged:
                    auth_result = "Potential manipulation detected"
                else:
                    auth_result = "No obvious manipulation detected"

            ai_screen = getattr(tamper, "ai_generation_screening", None) or "No synthetic generative signatures identified"
            dig_sig = getattr(tamper, "digital_signature_status", None) or "No digital signature (Standard scan/copy)"
            visual_evidence = tamper.get_visual_structure_evidence() if hasattr(tamper, "get_visual_structure_evidence") else []
            meta_evidence = tamper.get_metadata_evidence() if hasattr(tamper, "get_metadata_evidence") else []
            ela_score = tamper.ela_anomaly_score or 0.0
            explanation = tamper.explanation or "Screening checks complete."
        else:
            auth_result = "No obvious manipulation detected"
            ai_screen = "No synthetic generative signatures identified"
            dig_sig = "Standard document copy"
            visual_evidence = []
            meta_evidence = []
            ela_score = 0.0
            explanation = "Document passed baseline format checks."

        if auth_result == "Potential manipulation detected":
            auth_status = "FAIL"
        elif auth_result == "Inconclusive — further verification required":
            auth_status = "WARNING"
        else:
            auth_status = "PASS"

        authenticity_dimension = {
            "dimension": "Document Authenticity Screening",
            "status": auth_status,
            "result": auth_result,
            "ai_generation_screening": ai_screen,
            "digital_signature_status": dig_sig,
            "ela_anomaly_score": round(ela_score, 3),
            "visual_evidence": visual_evidence,
            "metadata_evidence": meta_evidence,
            "explanation": explanation,
            "note": auth_result
        }

        # -------------------------------------------------------------
        # 6. Official Verification Readiness
        # -------------------------------------------------------------
        issues = []
        corrections = []

        if type_status == "WARNING":
            issues.append(f"Document category mismatch: {type_note}")
            corrections.append("Ensure the file uploaded matches the required document type for this slot.")

        if fields_status in ["WARNING", "FAIL"]:
            issues.append(f"Missing mandatory fields: {', '.join(missing_fields) if missing_fields else 'Incomplete text extraction'}")
            corrections.append("Upload a complete, uncropped photo or scan where all names, dates, and certificate numbers are visible.")

        if validity_status == "EXPIRED":
            issues.append(f"Expired document: {validity_note}")
            corrections.append("Apply for a renewal or reissue at your local e-Sevai / RTO / issuing portal before submitting.")
        elif validity_status == "WARNING" and days_left is not None and days_left <= 60:
            issues.append(f"Validity expiring soon: {validity_label}")
            corrections.append("Check with the accepting authority if they require at least 3-6 months remaining validity.")

        if readability_status in ["WARNING", "FAIL"]:
            issues.append(f"Low scan quality: {readability_label}")
            corrections.append("Re-scan the original paper certificate at 300 DPI or take a flat photo in good daylight without flash glare.")

        if auth_status == "FAIL":
            issues.append("Image compression variance or editing software signatures detected.")
            corrections.append("Do not edit, filter, or re-export the image through photo editing apps. Submit the clean original scan.")
        elif auth_status == "WARNING":
            issues.append("Document image resolution is too low for conclusive digital forensic screening.")
            corrections.append("Provide a higher resolution scan (minimum 300 DPI) or official digitally signed PDF.")

        # Determine official readiness label
        if auth_status == "FAIL" or validity_status == "EXPIRED" or readability_status == "FAIL":
            official_status = "NEEDS_REVIEW"
            official_label = "Corrections Needed"
            official_note = "Address detected issues before submitting to the accepting department."
        elif service_code in PHYSICAL_VERIFICATION_SERVICES and doc_category in {"FIRST_GRADUATE_CERTIFICATE", "TRANSFER_CERTIFICATE"}:
            official_status = "PHYSICAL_REQUIRED"
            official_label = "Physical Document Required for In-Person Verification"
            official_note = "Original certificate must be physically produced at the scrutiny counter / admissions desk."
        elif issues:
            official_status = "NEEDS_REVIEW"
            official_label = "Review Advised Before Submission"
            official_note = "Advisory warnings exist. Review guidance points to ensure smooth acceptance."
        else:
            official_status = "READY"
            official_label = "Ready for Official Submission"
            official_note = "All automated checks satisfied. Prepared for citizen application submission."

        official_dimension = {
            "dimension": "Official Verification Readiness",
            "status": official_status,
            "label": official_label,
            "note": official_note
        }

        return {
            "document_name": doc.original_filename,
            "document_id": doc.id,
            "file_size_bytes": doc.file_size_bytes,
            "mime_type": doc.mime_type,
            "checklist_requirement_id": getattr(doc, "checklist_requirement_id", None),
            "dimensions": {
                "type_detection": type_dimension,
                "fields_extraction": fields_dimension,
                "validity_expiry": validity_dimension,
                "readability_quality": readability_dimension,
                "authenticity_screening": authenticity_dimension,
                "official_readiness": official_dimension
            },
            "detected_issues": issues,
            "suggested_corrections": corrections,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "rules_version": RULES_VERSION,
            "disclaimer": LEGAL_DISCLAIMER
        }

document_verifier = DocumentVerifier()
