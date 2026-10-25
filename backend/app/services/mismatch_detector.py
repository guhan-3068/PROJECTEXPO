import re
from typing import List, Dict, Any, Tuple
from app.models.document import UploadedDocument
from app.config import settings

def calculate_levenshtein(s1: str, s2: str) -> int:
    """Computes basic Levenshtein edit distance."""
    if len(s1) < len(s2):
        return calculate_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def string_similarity(s1: str, s2: str) -> float:
    """Computes normalized similarity [0.0, 1.0] between two strings."""
    s1_clean = re.sub(r"[^a-z0-9]", "", s1.lower())
    s2_clean = re.sub(r"[^a-z0-9]", "", s2.lower())
    if not s1_clean and not s2_clean:
        return 1.0
    if not s1_clean or not s2_clean:
        return 0.0
    if s1_clean == s2_clean:
        return 1.0
    
    # Try rapidfuzz if available
    try:
        from rapidfuzz import fuzz
        return fuzz.token_sort_ratio(s1, s2) / 100.0
    except ImportError:
        pass

    # Fallback token set & Levenshtein
    tokens1 = set(s1.lower().split())
    tokens2 = set(s2.lower().split())
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union) if union else 0.0

    dist = calculate_levenshtein(s1_clean, s2_clean)
    max_len = max(len(s1_clean), len(s2_clean))
    lev_ratio = 1.0 - (dist / max_len)

    return max(jaccard, lev_ratio)

class MismatchDetector:
    """
    Cross-document identity verification engine.
    Detects discrepancies across multiple submitted documents while accounting
    for acceptable variations (e.g. name order, middle initial).
    """

    def detect_mismatches(self, documents: List[UploadedDocument]) -> List[Dict[str, Any]]:
        mismatches = []
        if len(documents) < 2:
            return mismatches

        # Extract field values by document
        doc_fields: Dict[str, Dict[str, str]] = {}
        doc_names: Dict[str, str] = {}

        for doc in documents:
            doc_names[doc.id] = doc.original_filename
            fields_map = {}
            for field in doc.extracted_fields:
                val = field.effective_value
                if val:
                    fields_map[field.field_key] = val
            doc_fields[doc.id] = fields_map

        # Pairwise comparison across documents
        doc_ids = list(doc_fields.keys())
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                id_a, id_b = doc_ids[i], doc_ids[j]
                fields_a, fields_b = doc_fields[id_a], doc_fields[id_b]

                # 1. Compare Full Names
                if "full_name" in fields_a and "full_name" in fields_b:
                    val_a = fields_a["full_name"]
                    val_b = fields_b["full_name"]
                    sim = string_similarity(val_a, val_b)

                    if sim < 0.99:  # Not completely identical
                        if sim >= settings.SIMILARITY_THRESHOLD:
                            # Minor OCR variation or middle initial abbreviation
                            mismatches.append({
                                "field_key": "full_name",
                                "display_field": "Full Name",
                                "document_a_id": id_a,
                                "document_a_name": doc_names[id_a],
                                "document_a_value": val_a,
                                "document_b_id": id_b,
                                "document_b_name": doc_names[id_b],
                                "document_b_value": val_b,
                                "similarity_score": round(sim, 2),
                                "mismatch_type": "ACCEPTABLE_VARIATION",
                                "requires_manual_review": False,
                                "explanation": f"Minor spelling or name order difference (Similarity: {int(sim*100)}%). Evaluated as likely consistent."
                            })
                        else:
                            # Significant name mismatch
                            mismatches.append({
                                "field_key": "full_name",
                                "display_field": "Full Name",
                                "document_a_id": id_a,
                                "document_a_name": doc_names[id_a],
                                "document_a_value": val_a,
                                "document_b_id": id_b,
                                "document_b_name": doc_names[id_b],
                                "document_b_value": val_b,
                                "similarity_score": round(sim, 2),
                                "mismatch_type": "NAME_MISMATCH",
                                "requires_manual_review": True,
                                "explanation": f"Significant name mismatch between documents ('{val_a}' vs '{val_b}'). Requires manual verification."
                            })

                # 2. Compare Date of Birth (DOB)
                if "dob" in fields_a and "dob" in fields_b:
                    dob_a = fields_a["dob"]
                    dob_b = fields_b["dob"]
                    if dob_a != dob_b:
                        mismatches.append({
                            "field_key": "dob",
                            "display_field": "Date of Birth",
                            "document_a_id": id_a,
                            "document_a_name": doc_names[id_a],
                            "document_a_value": dob_a,
                            "document_b_id": id_b,
                            "document_b_name": doc_names[id_b],
                            "document_b_value": dob_b,
                            "similarity_score": 0.0,
                            "mismatch_type": "CONFLICTING_DOB",
                            "requires_manual_review": True,
                            "explanation": f"Date of Birth differs between documents ('{dob_a}' vs '{dob_b}'). Requires manual verification."
                        })

        return mismatches

mismatch_detector = MismatchDetector()
