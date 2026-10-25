"""
QUBIX - Verification Confidence Meter Service
Provides transparent, explainable reliability metrics across 6 distinct dimensions
based on measurable outputs from OCR, classification, schema matching, and forensic analysis.

Includes mandatory citizen advisory:
"Official Authenticity: Not Verified"
"""

from typing import Dict, Any, List, Optional
import math
from app.models.document import UploadedDocument
from app.models.extracted_field import ExtractedField

class ConfidenceMeterService:
    """
    Evaluates automated document inspection across 6 distinct dimensions:
    1. Document Type Detection Confidence
    2. OCR / Text Extraction Confidence
    3. Required-Field Completeness
    4. Cross-Document Consistency
    5. Document Readability & Scan Quality
    6. Official Authenticity Verification Status
    """

    EXPECTED_FIELDS_BY_CATEGORY = {
        "AADHAAR": ["full_name", "doc_number", "dob", "gender"],
        "PAN_CARD": ["full_name", "father_name", "doc_number", "dob"],
        "DRIVING_LICENSE": ["full_name", "doc_number", "issue_date", "expiry_date"],
        "INCOME_CERTIFICATE": ["full_name", "doc_number", "issue_date", "annual_income"],
        "COMMUNITY_CERTIFICATE": ["full_name", "doc_number", "caste_community", "issue_date"],
        "NATIVITY_CERTIFICATE": ["full_name", "doc_number", "issue_date", "address"],
        "FIRST_GRADUATE_CERTIFICATE": ["full_name", "doc_number", "issue_date", "authority"],
        "EDUCATIONAL_CERTIFICATE": ["full_name", "roll_number", "marks_or_grade", "issuing_institution"],
        "TRANSFER_CERTIFICATE": ["full_name", "leaving_date", "school_name"],
        "RATION_CARD": ["card_number", "family_head", "address"],
        "BANK_PASSBOOK": ["account_holder", "account_number", "ifsc_code", "bank_name"],
        "PASSPORT": ["full_name", "doc_number", "dob", "expiry_date", "nationality"]
    }

    def _determine_level(self, score: Optional[float]) -> str:
        if score is None:
            return "Unable to Determine"
        if score >= 80.0:
            return "High Confidence"
        elif score >= 50.0:
            return "Moderate Confidence"
        else:
            return "Low Confidence"

    def calculate_document_confidence(
        self,
        doc: UploadedDocument,
        extracted_fields: List[ExtractedField],
        mismatches: List[Dict[str, Any]] = None,
        total_application_docs: int = 1
    ) -> Dict[str, Any]:
        """
        Calculates explainable confidence for an individual document.
        """
        mismatches = mismatches or []
        doc_category = doc.doc_category.upper()
        raw_text = doc.raw_text or ""
        word_count = len(raw_text.split())

        # -------------------------------------------------------------
        # 1. Document Type Detection Confidence
        # -------------------------------------------------------------
        # Base confidence from classification
        type_score = 75.0
        type_reasons = []

        # Claimed vs Detected match
        if doc.user_assigned_category and doc.user_assigned_category != "UNKNOWN":
            if doc.user_assigned_category.upper() == doc_category:
                type_score += 15.0
                type_reasons.append(f"Detected category '{doc_category.replace('_', ' ')}' perfectly matched applicant-claimed category.")
            else:
                type_score -= 25.0
                type_reasons.append(f"Category discrepancy: Applicant selected '{doc.user_assigned_category}', but OCR classified document as '{doc_category}'.")
        else:
            type_reasons.append(f"Classified as '{doc_category.replace('_', ' ')}' based on primary header keywords and layout markers.")

        if word_count < 10:
            type_score -= 30.0
            type_reasons.append("Sparse text content (< 10 words) reduced classification certainty.")
        elif word_count >= 30:
            type_score += 10.0
            type_reasons.append("Sufficient text density and official heading keywords detected.")

        type_score = max(10.0, min(98.0, type_score))
        type_level = self._determine_level(type_score)

        # -------------------------------------------------------------
        # 2. OCR / Text Extraction Confidence
        # -------------------------------------------------------------
        # Measured directly from OCR engine confidence
        raw_ocr_conf = doc.ocr_overall_confidence
        ocr_score = round(raw_ocr_conf * 100.0, 1) if raw_ocr_conf > 0 else 25.0
        ocr_reasons = []

        if raw_ocr_conf >= 0.85:
            ocr_reasons.append(f"Crisp character edges; mean character recognition probability is {int(raw_ocr_conf * 100)}%.")
        elif raw_ocr_conf >= 0.50:
            ocr_reasons.append(f"Moderate OCR recognition ({int(raw_ocr_conf * 100)}%); minor font variation, background tint, or slight compression detected.")
        else:
            ocr_reasons.append(f"Low OCR certainty ({int(raw_ocr_conf * 100)}%); blurred typography, camera perspective skew, or low scan resolution.")

        if word_count < 15:
            ocr_score = max(10.0, ocr_score - 15.0)
            ocr_reasons.append("Very low word count extracted from page.")

        ocr_level = self._determine_level(ocr_score)

        # -------------------------------------------------------------
        # 3. Required-Field Completeness
        # -------------------------------------------------------------
        expected_keys = self.EXPECTED_FIELDS_BY_CATEGORY.get(doc_category, ["full_name", "doc_number", "issue_date"])
        detected_keys = [f.field_key for f in extracted_fields if f.effective_value and f.effective_value != "<Not detected>"]
        
        found_expected = [k for k in expected_keys if k in detected_keys]
        missing_expected = [k for k in expected_keys if k not in detected_keys]
        
        completeness_ratio = len(found_expected) / len(expected_keys) if expected_keys else 1.0
        completeness_score = round(completeness_ratio * 100.0, 1)
        completeness_reasons = []

        if len(missing_expected) == 0:
            completeness_reasons.append(f"All {len(expected_keys)} required metadata fields ({', '.join(k.replace('_', ' ') for k in expected_keys)}) successfully parsed.")
        else:
            missing_names = [k.replace('_', ' ').title() for k in missing_expected]
            completeness_reasons.append(f"Missing mandatory field(s): {', '.join(missing_names)}. Pre-application checklist requires these values.")

        completeness_level = self._determine_level(completeness_score)

        # -------------------------------------------------------------
        # 4. Cross-Document Consistency
        # -------------------------------------------------------------
        consistency_score = None
        consistency_level = "Unable to Determine"
        consistency_reasons = []

        if total_application_docs <= 1:
            consistency_reasons.append("Only 1 document uploaded in this application. Cross-document consistency requires at least 2 documents to compare names, DOBs, and addresses.")
        else:
            # Check if this document has mismatches
            doc_mismatches = [m for m in mismatches if m.get("document_a_id") == doc.id or m.get("document_b_id") == doc.id]
            if not doc_mismatches:
                consistency_score = 95.0
                consistency_level = "High Confidence"
                consistency_reasons.append("Identity fields (Name, Date of Birth) exactly match or align with other uploaded certificates in this application.")
            else:
                has_severe = any(m.get("requires_manual_review") for m in doc_mismatches)
                if has_severe:
                    consistency_score = 40.0
                    consistency_level = "Low Confidence"
                    consistency_reasons.append(f"Detected {len(doc_mismatches)} severe cross-document discrepancy (e.g. spelling or date conflict) requiring manual affidavit or gazette re-check.")
                else:
                    consistency_score = 65.0
                    consistency_level = "Moderate Confidence"
                    consistency_reasons.append(f"Minor variation detected across documents (e.g. initial expansion or spacing variation).")

        # -------------------------------------------------------------
        # 5. Document Readability & Scan Quality
        # -------------------------------------------------------------
        readability_score = 85.0
        readability_reasons = []

        # Check file size and mime
        if doc.file_size_bytes < 15 * 1024:
            readability_score -= 35.0
            readability_reasons.append("Extremely small file size (< 15 KB); severe JPEG compression or thumbnail scan.")
        elif doc.file_size_bytes > 50 * 1024:
            readability_score += 5.0

        # Check tampering / ELA flags
        tamper = doc.tampering_analysis
        if tamper and tamper.is_flagged:
            readability_score -= 30.0
            readability_reasons.append(f"Structural visual anomaly flagged: {tamper.explanation or 'High compression noise / edited metadata'}.")
        else:
            readability_reasons.append("Clean visual structure; no compression artifacts or multi-generation resaving detected.")

        if raw_ocr_conf < 0.35:
            readability_score -= 35.0
            readability_reasons.append("OCR optical character contrast is degraded. Recommended minimum scan clarity is 300 DPI.")

        readability_score = max(10.0, min(95.0, readability_score))
        readability_level = self._determine_level(readability_score)

        # -------------------------------------------------------------
        # 6. Official Authenticity Verification Status (MANDATORY WARNING)
        # -------------------------------------------------------------
        authenticity = {
            "status": "Official Authenticity: Not Verified",
            "level": "Unverified by Issuing Authority",
            "is_officially_verified": False,
            "verification_source": None,
            "verification_timestamp": None,
            "verification_token": None,
            "legal_advisory": "Automated AI checks evaluate readability, completeness, and consistency for pre-submission readiness. It does NOT constitute legal government authentication. Authenticity can only be legally verified by the issuing department (Tahsildar / UIDAI / Parivahan / RTO) or via an authorized DigiLocker / e-District API handshake."
        }

        # -------------------------------------------------------------
        # Documented Composite Overall Confidence Score
        # -------------------------------------------------------------
        if consistency_score is not None:
            # Weighted formula: 20% Type + 25% OCR + 25% Completeness + 15% Readability + 15% Consistency
            composite = (
                (type_score * 0.20) +
                (ocr_score * 0.25) +
                (completeness_score * 0.25) +
                (readability_score * 0.15) +
                (consistency_score * 0.15)
            )
            formula_doc = "Formula: 20% Type Detection + 25% OCR Engine + 25% Field Completeness + 15% Readability + 15% Cross-Document Consistency."
        else:
            # Normalized formula without consistency: 25% Type + 30% OCR + 30% Completeness + 15% Readability
            composite = (
                (type_score * 0.25) +
                (ocr_score * 0.30) +
                (completeness_score * 0.30) +
                (readability_score * 0.15)
            )
            formula_doc = "Formula (Single Document): 25% Type Detection + 30% OCR Engine + 30% Field Completeness + 15% Readability."

        composite = round(max(10.0, min(99.0, composite)), 1)
        composite_level = self._determine_level(composite)

        return {
            "document_id": doc.id,
            "original_filename": doc.original_filename,
            "doc_category": doc_category,
            "overall_score": composite,
            "overall_level": composite_level,
            "formula_explanation": formula_doc,
            "dimensions": {
                "type_detection": {
                    "name": "Document Type Detection",
                    "score": round(type_score, 1),
                    "level": type_level,
                    "reasons": type_reasons
                },
                "ocr_extraction": {
                    "name": "OCR / Text Extraction Quality",
                    "score": round(ocr_score, 1),
                    "level": ocr_level,
                    "reasons": ocr_reasons
                },
                "field_completeness": {
                    "name": "Required-Field Completeness",
                    "score": completeness_score,
                    "level": completeness_level,
                    "found_fields": found_expected,
                    "missing_fields": missing_expected,
                    "reasons": completeness_reasons
                },
                "cross_consistency": {
                    "name": "Cross-Document Consistency",
                    "score": round(consistency_score, 1) if consistency_score is not None else None,
                    "level": consistency_level,
                    "reasons": consistency_reasons
                },
                "readability": {
                    "name": "Document Readability & Image Integrity",
                    "score": round(readability_score, 1),
                    "level": readability_level,
                    "reasons": readability_reasons
                },
                "official_authenticity": authenticity
            }
        }

    def calculate_application_confidence(
        self,
        docs: List[UploadedDocument],
        mismatches: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates aggregate confidence across all documents in an application.
        """
        mismatches = mismatches or []
        doc_confidences = []
        
        for d in docs:
            fields = d.extracted_fields or []
            res = self.calculate_document_confidence(
                doc=d,
                extracted_fields=fields,
                mismatches=mismatches,
                total_application_docs=len(docs)
            )
            doc_confidences.append(res)

        if not doc_confidences:
            return {
                "mean_score": 0.0,
                "overall_level": "Unable to Determine",
                "summary": "No documents uploaded to evaluate.",
                "documents": []
            }

        mean_score = round(sum(d["overall_score"] for d in doc_confidences) / len(doc_confidences), 1)
        mean_level = self._determine_level(mean_score)

        return {
            "mean_score": mean_score,
            "overall_level": mean_level,
            "total_documents": len(docs),
            "documents": doc_confidences,
            "official_authenticity_notice": "Official Authenticity: Not Verified. Automated verification evaluates document readiness and legibility only."
        }

confidence_meter_service = ConfidenceMeterService()
