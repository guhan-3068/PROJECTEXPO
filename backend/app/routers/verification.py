from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import UserApplication, ApplicationProfile
from app.models.document import UploadedDocument
from app.models.verification import VerificationResult
from app.models.user import User
from app.schemas.verification import VerificationResultOut
from app.routers.auth import get_current_user
from app.services.requirement_checker import requirement_checker
from app.services.expiry_detector import expiry_detector
from app.services.mismatch_detector import mismatch_detector
from app.services.report_generator import report_generator
from app.services.confidence_meter_service import confidence_meter_service

router = APIRouter(prefix="/verify", tags=["Verification"])

def _format_verification_out(res: VerificationResult) -> dict:
    return {
        "id": res.id,
        "user_application_id": res.user_application_id,
        "overall_status": res.overall_status,
        "readiness_status": getattr(res, "readiness_status", None) or "Action Required",
        "readiness_score": getattr(res, "readiness_score", None) or "0%",
        "satisfied_requirements": res.get_json_field("satisfied_requirements"),
        "missing_requirements": res.get_json_field("missing_requirements"),
        "expired_documents": res.get_json_field("expired_documents"),
        "expiring_soon_documents": res.get_json_field("expiring_soon_documents"),
        "detected_mismatches": res.get_json_field("detected_mismatches"),
        "tampering_flags": res.get_json_field("tampering_flags"),
        "recommended_actions": res.get_json_field("recommended_actions"),
        "prioritized_checklist": res.get_json_field("prioritized_checklist"),
        "action_plan": res.get_json_field("action_plan"),
        "confidence_summary": res.get_json_field("confidence_summary"),
        "report_pdf_url": f"/api/v1/reports/{res.user_application_id}/download" if res.report_pdf_path else None,
        "evaluated_at": res.evaluated_at
    }

@router.post("/run/{application_id}", response_model=VerificationResultOut)
def run_verification(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == application_id).all()
    profile = db.query(ApplicationProfile).filter(ApplicationProfile.id == app.application_profile_id).first()

    # 1. Run Expiry Analysis
    expiry_analysis = expiry_detector.analyze_documents(docs)
    expired_list = expiry_analysis["expired"]
    expiring_soon_list = expiry_analysis["expiring_soon"]
    expired_doc_ids = [d["document_id"] for d in expired_list]

    # 2. Run Requirement Checker Matrix
    req_analysis = requirement_checker.evaluate_requirements(
        profile.requirements,
        docs,
        expired_doc_ids=expired_doc_ids
    )

    # 3. Run Cross-Document Mismatch Engine
    mismatches = mismatch_detector.detect_mismatches(docs)

    # 4. Gather Tampering Diagnostics
    tampering_flags = []
    for d in docs:
        if d.tampering_analysis and d.tampering_analysis.is_flagged:
            tampering_flags.append({
                "document_id": d.id,
                "document_name": d.original_filename,
                "risk_level": d.tampering_analysis.risk_level,
                "is_flagged": True,
                "ela_score": d.tampering_analysis.ela_anomaly_score,
                "software_detected": d.tampering_analysis.metadata_software_detected,
                "anomalies": d.tampering_analysis.get_detected_anomalies(),
                "explanation": d.tampering_analysis.explanation or "Potential formatting anomaly"
            })

    # 5. Determine Overall & Readiness Status
    # Readiness statuses per citizen guidelines:
    # - Ready for Next Step
    # - Action Required
    # - Needs Manual Review
    # - Official Verification Pending
    has_missing_mandatory = req_analysis["has_missing_mandatory"]
    has_expired = len(expired_list) > 0
    has_severe_mismatch = any(m.get("requires_manual_review") for m in mismatches)
    has_tamper_flag = len(tampering_flags) > 0
    has_unreadable = any(d.ocr_overall_confidence < 0.35 for d in docs)

    # Build Prioritized Checklist
    prioritized_checklist = []
    satisfied_dict = {s["requirement_code"]: s for s in req_analysis["satisfied"]}

    for req in profile.requirements:
        code = req.requirement_code
        req_type = getattr(req, "requirement_type", None) or ("REQUIRED" if req.is_mandatory else "OPTIONAL")

        if code in satisfied_dict:
            sat_info = satisfied_dict[code]
            matched_ids = sat_info.get("matched_document_ids", [])
            has_doc_expired = any(did in expired_doc_ids for did in matched_ids)
            has_doc_unreadable = any(any(d.id == did and d.ocr_overall_confidence < 0.35 for d in docs) for did in matched_ids)

            if has_doc_expired:
                prioritized_checklist.append({
                    "requirement_code": code,
                    "display_name": req.display_name,
                    "status": "NEEDS_REVIEW",
                    "symbol": "[!]",
                    "detail": "Uploaded document is expired and needs official renewal",
                    "is_mandatory": req.is_mandatory,
                    "requirement_type": req_type,
                    "guide_id": "dl_renewal" if ("DL" in code or "DRIVING" in code) else "income_reissue"
                })
            elif has_doc_unreadable:
                prioritized_checklist.append({
                    "requirement_code": code,
                    "display_name": req.display_name,
                    "status": "NEEDS_REVIEW",
                    "symbol": "[!]",
                    "detail": "Scan quality low or degraded; re-scan recommended",
                    "is_mandatory": req.is_mandatory,
                    "requirement_type": req_type,
                    "guide_id": "blurry_scan"
                })
            else:
                prioritized_checklist.append({
                    "requirement_code": code,
                    "display_name": req.display_name,
                    "status": "SATISFIED",
                    "symbol": "[x]",
                    "detail": f"Uploaded and readable ({', '.join(sat_info.get('matched_document_names', [])) or 'Verified'})",
                    "is_mandatory": req.is_mandatory,
                    "requirement_type": req_type,
                    "guide_id": None
                })
        else:
            if req_type == "CONDITIONALLY_REQUIRED":
                prioritized_checklist.append({
                    "requirement_code": code,
                    "display_name": req.display_name,
                    "status": "NEEDS_REVIEW",
                    "symbol": "[!]",
                    "detail": f"Conditionally required: {req.description or 'Requirement depends on applicable admission / scheme rules'}",
                    "is_mandatory": False,
                    "requirement_type": req_type,
                    "guide_id": "nativity_reissue" if "NATIVITY" in code else "income_reissue"
                })
            elif req.is_mandatory:
                prioritized_checklist.append({
                    "requirement_code": code,
                    "display_name": req.display_name,
                    "status": "MISSING",
                    "symbol": "[ ]",
                    "detail": "Mandatory document missing. Upload required before applying.",
                    "is_mandatory": True,
                    "requirement_type": req_type,
                    "guide_id": "income_reissue" if "INCOME" in code else ("nativity_reissue" if "NATIVITY" in code else "aadhaar_update")
                })
            else:
                prioritized_checklist.append({
                    "requirement_code": code,
                    "display_name": req.display_name,
                    "status": "MISSING",
                    "symbol": "[ ]",
                    "detail": "Optional supporting document (upload if applicable).",
                    "is_mandatory": False,
                    "requirement_type": req_type,
                    "guide_id": None
                })

    # Build Prioritized Action Plan
    action_plan = []
    plan_priority = 1

    # 1. Critical Missing Mandatory
    for m in req_analysis["missing"]:
        if m.get("is_mandatory", True):
            guide_id = "income_reissue" if "INCOME" in m["requirement_code"] else ("nativity_reissue" if "NATIVITY" in m["requirement_code"] else "aadhaar_update")
            action_plan.append({
                "id": f"act-{plan_priority}",
                "priority": plan_priority,
                "urgency": "CRITICAL",
                "title": f"Upload Missing {m['display_name']}",
                "description": f"Mandatory document is missing from your checklist. Upload a clear copy to complete pre-application requirements.",
                "issue_type": "MISSING_DOC",
                "guide_id": guide_id,
                "action_label": "How to Fix This?"
            })
            plan_priority += 1

    # 2. Critical Expired Documents
    for exp in expired_list:
        guide_id = "dl_renewal" if "DRIVING" in exp.get("doc_category", "") else "income_reissue"
        action_plan.append({
            "id": f"act-{plan_priority}",
            "priority": plan_priority,
            "urgency": "CRITICAL",
            "title": f"Renew Expired Document: {exp['document_name']}",
            "description": exp.get("message", "Document is past its official validity date. Obtain a renewed certificate before submitting your application."),
            "issue_type": "EXPIRED",
            "guide_id": guide_id,
            "action_label": "How to Fix This?"
        })
        plan_priority += 1

    # 3. Discrepancies & Mismatches
    for mis in mismatches:
        action_plan.append({
            "id": f"act-{plan_priority}",
            "priority": plan_priority,
            "urgency": "WARNING" if mis.get("requires_manual_review") else "INFO",
            "title": f"Resolve {mis.get('display_field', 'Name')} Discrepancy",
            "description": f"Difference between '{mis.get('document_a_name')}' and '{mis.get('document_b_name')}'. {mis.get('explanation', '')}",
            "issue_type": "MISMATCH",
            "guide_id": "name_mismatch",
            "action_label": "How to Fix This?"
        })
        plan_priority += 1

    # 4. Low resolution / Blurry
    for d in docs:
        if d.ocr_overall_confidence < 0.35:
            action_plan.append({
                "id": f"act-{plan_priority}",
                "priority": plan_priority,
                "urgency": "WARNING",
                "title": f"Re-scan Blurry Document: {d.original_filename}",
                "description": "OCR confidence is low due to poor scan lighting or low resolution. Scrutiny officers may reject unreadable records.",
                "issue_type": "UNREADABLE",
                "guide_id": "blurry_scan",
                "action_label": "How to Fix This?"
            })
            plan_priority += 1

    # 5. Tampering Anomaly
    for tf in tampering_flags:
        action_plan.append({
            "id": f"act-{plan_priority}",
            "priority": plan_priority,
            "urgency": "WARNING",
            "title": f"Inspect Image Authenticity: {tf['document_name']}",
            "description": "Compression variance or editing software indicators detected. Original physical inspection recommended.",
            "issue_type": "TAMPERING",
            "guide_id": "blurry_scan",
            "action_label": "How to Fix This?"
        })
        plan_priority += 1

    # 6. Conditionals
    for item in prioritized_checklist:
        if item["requirement_type"] == "CONDITIONALLY_REQUIRED" and item["status"] != "SATISFIED":
            action_plan.append({
                "id": f"act-{plan_priority}",
                "priority": plan_priority,
                "urgency": "INFO",
                "title": f"Confirm Rules for {item['display_name']}",
                "description": f"Verify with admissions / department guidelines whether {item['display_name']} is required for your quota category.",
                "issue_type": "CONDITIONAL",
                "guide_id": item.get("guide_id") or "nativity_reissue",
                "action_label": "View Official Instructions"
            })
            plan_priority += 1

    # 7. Final Next Step
    if not has_missing_mandatory and not has_expired and not has_severe_mismatch and not has_unreadable:
        action_plan.append({
            "id": f"act-{plan_priority}",
            "priority": plan_priority,
            "urgency": "INFO",
            "title": "Review Final Checklist & Proceed to Official Department Portal",
            "description": "All pre-application readiness checks are satisfied. Download your audit report and proceed to submit your application.",
            "issue_type": "FINAL_STEP",
            "guide_id": "name_mismatch",
            "action_label": "View Official Instructions"
        })

    # Determine Readiness Status & Score
    total_reqs = len(profile.requirements) or 1
    satisfied_count = len([c for c in prioritized_checklist if c["status"] == "SATISFIED"])
    critical_issues = len([a for a in action_plan if a["urgency"] == "CRITICAL"])
    warning_issues = len([a for a in action_plan if a["urgency"] == "WARNING"])

    if critical_issues > 0:
        readiness_status = "Action Required"
        overall_status = "INCOMPLETE"
    elif warning_issues > 0:
        readiness_status = "Needs Manual Review"
        overall_status = "REVIEW_REQUIRED"
    elif any("CERTIFICATE" in r.requirement_code for r in profile.requirements) and not any(d.doc_category == "COMMUNITY_CERTIFICATE" for d in docs):
        readiness_status = "Official Verification Pending"
        overall_status = "COMPLETE"
    else:
        readiness_status = "Ready for Next Step"
        overall_status = "COMPLETE"

    score_pct = int(round((satisfied_count / total_reqs) * 100))
    if critical_issues > 0 and score_pct > 75:
        score_pct = 75
    readiness_score = f"{score_pct}%"

    actions = [f"{a['title']}: {a['description']}" for a in action_plan]

    # 6. Calculate Explainable Verification Confidence Meter
    confidence_data = confidence_meter_service.calculate_application_confidence(
        docs=docs,
        mismatches=mismatches
    )

    # 7. Generate Verification Audit PDF Report
    applicant_name = app.user.full_name if app.user else "Applicant"
    pdf_path = report_generator.generate_pdf_report(
        application_ref=app.reference_number,
        profile_name=profile.name,
        jurisdiction=profile.jurisdiction,
        applicant_name=applicant_name,
        overall_status=overall_status,
        satisfied_items=req_analysis["satisfied"],
        missing_items=req_analysis["missing"],
        expired_docs=expired_list,
        expiring_soon_docs=expiring_soon_list,
        mismatches=mismatches,
        tampering_flags=tampering_flags,
        recommended_actions=actions,
        confidence_data=confidence_data
    )

    # 8. Update or Create VerificationResult record
    ver_res = db.query(VerificationResult).filter(VerificationResult.user_application_id == application_id).first()
    if not ver_res:
        ver_res = VerificationResult(user_application_id=application_id)
        db.add(ver_res)

    ver_res.overall_status = overall_status
    ver_res.readiness_status = readiness_status
    ver_res.readiness_score = readiness_score
    ver_res.set_json_field("satisfied_requirements", req_analysis["satisfied"])
    ver_res.set_json_field("missing_requirements", req_analysis["missing"])
    ver_res.set_json_field("expired_documents", expired_list)
    ver_res.set_json_field("expiring_soon_documents", expiring_soon_list)
    ver_res.set_json_field("detected_mismatches", mismatches)
    ver_res.set_json_field("tampering_flags", tampering_flags)
    ver_res.set_json_field("recommended_actions", actions)
    ver_res.set_json_field("prioritized_checklist", prioritized_checklist)
    ver_res.set_json_field("action_plan", action_plan)
    ver_res.set_json_field("confidence_summary", confidence_data)
    ver_res.report_pdf_path = pdf_path

    # Update application status
    app.status = overall_status
    app.readiness_status = readiness_status
    db.commit()
    db.refresh(ver_res)

    return _format_verification_out(ver_res)

@router.post("/recheck/{application_id}", response_model=VerificationResultOut)
def recheck_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reruns the pre-application readiness check after the user replaces or uploads a document.
    """
    return run_verification(application_id=application_id, current_user=current_user, db=db)

@router.get("/confidence/{application_id}")
def get_application_confidence(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns explainable reliability metrics across 6 dimensions for all documents in an application.
    """
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == application_id).all()
    mismatches = mismatch_detector.detect_mismatches(docs)
    return confidence_meter_service.calculate_application_confidence(docs=docs, mismatches=mismatches)

@router.get("/confidence/document/{document_id}")
def get_document_confidence(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns explainable reliability metrics across 6 dimensions for a specific document.
    """
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    app_docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == doc.user_application_id).all()
    mismatches = mismatch_detector.detect_mismatches(app_docs)
    return confidence_meter_service.calculate_document_confidence(
        doc=doc,
        extracted_fields=doc.extracted_fields or [],
        mismatches=mismatches,
        total_application_docs=len(app_docs)
    )

@router.get("/{application_id}", response_model=VerificationResultOut)
def get_verification_result(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    ver_res = db.query(VerificationResult).filter(VerificationResult.user_application_id == application_id).first()
    if not ver_res:
        raise HTTPException(status_code=404, detail="Verification has not been executed for this application yet")

    return _format_verification_out(ver_res)
