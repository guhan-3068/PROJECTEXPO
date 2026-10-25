from typing import List, Dict, Any
from app.models.application import ChecklistRequirement
from app.models.document import UploadedDocument

class RequirementChecker:
    """
    Evaluates applicant documents against the configurable checklist matrix.
    Identifies missing documents, satisfied documents, and generates next actions.
    """

    def evaluate_requirements(
        self,
        requirements: List[ChecklistRequirement],
        uploaded_documents: List[UploadedDocument],
        expired_doc_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates checklist items.
        Returns:
            {
                "is_complete": bool,
                "has_missing_mandatory": bool,
                "satisfied": [ChecklistItemStatus],
                "missing": [ChecklistItemStatus],
                "recommended_actions": [str]
            }
        """
        expired_ids = set(expired_doc_ids or [])
        satisfied_items = []
        missing_items = []
        actions = []

        # Map documents by category
        docs_by_category: Dict[str, List[UploadedDocument]] = {}
        for doc in uploaded_documents:
            cat = doc.doc_category.upper()
            docs_by_category.setdefault(cat, []).append(doc)

        # Track which documents were allocated to avoid double-claiming if desired,
        # but in many jurisdictions a Passport can count for Proof of Identity and DOB proof.
        for req in requirements:
            accepted_cats = [c.upper() for c in req.get_accepted_categories()]
            req_type = getattr(req, "requirement_type", None) or ("REQUIRED" if getattr(req, "is_mandatory", True) else "OPTIONAL")
            
            # Find eligible documents uploaded
            matching_docs = []
            for cat in accepted_cats:
                if cat in docs_by_category:
                    for d in docs_by_category[cat]:
                        if d not in matching_docs:
                            matching_docs.append(d)

            # Check if any matching doc is not expired
            valid_matching_docs = [d for d in matching_docs if d.id not in expired_ids]

            if valid_matching_docs:
                satisfied_items.append({
                    "requirement_code": req.requirement_code,
                    "display_name": req.display_name,
                    "is_mandatory": req.is_mandatory,
                    "requirement_type": req_type,
                    "is_satisfied": True,
                    "matched_document_ids": [d.id for d in valid_matching_docs],
                    "matched_document_names": [d.original_filename for d in valid_matching_docs],
                    "reason": f"Satisfied by {valid_matching_docs[0].original_filename} ({valid_matching_docs[0].doc_category.replace('_', ' ')})"
                })
            else:
                # Document missing or only expired version present
                reason = "Not uploaded"
                if matching_docs:
                    reason = f"Uploaded document ({matching_docs[0].original_filename}) is EXPIRED and cannot satisfy requirement"

                missing_item = {
                    "requirement_code": req.requirement_code,
                    "display_name": req.display_name,
                    "is_mandatory": req.is_mandatory,
                    "requirement_type": req_type,
                    "is_satisfied": False,
                    "matched_document_ids": [],
                    "matched_document_names": [],
                    "reason": reason
                }
                missing_items.append(missing_item)

                if req.is_mandatory and req_type == "REQUIRED":
                    actions.append(f"Upload required document for '{req.display_name}'. Accepted types: {', '.join(c.replace('_', ' ') for c in accepted_cats)}")
                elif req_type == "CONDITIONALLY_REQUIRED":
                    actions.append(f"Upload conditionally required document for '{req.display_name}' if applicable to your application category.")

        mandatory_missing = [m for m in missing_items if m.get("is_mandatory") and m.get("requirement_type") in ("REQUIRED", None)]
        is_complete = len(mandatory_missing) == 0

        return {
            "is_complete": is_complete,
            "has_missing_mandatory": len(mandatory_missing) > 0,
            "satisfied": satisfied_items,
            "missing": missing_items,
            "recommended_actions": actions
        }

requirement_checker = RequirementChecker()
