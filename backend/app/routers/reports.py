import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import UserApplication, ApplicationProfile
from app.models.document import UploadedDocument
from app.models.verification import VerificationResult
from app.models.user import User
from app.routers.auth import get_current_user_flexible
from app.services.requirement_checker import requirement_checker
from app.services.expiry_detector import expiry_detector
from app.services.mismatch_detector import mismatch_detector
from app.services.report_generator import report_generator

router = APIRouter(prefix="/reports", tags=["Reports"])

def _ensure_report_exists(app: UserApplication, db: Session) -> str:
    """
    Ensures a valid PDF audit report exists on disk.
    If not found, executes on-the-fly generation from current application state.
    """
    ver_res = db.query(VerificationResult).filter(VerificationResult.user_application_id == app.id).first()
    
    # Check if report already exists on disk
    if ver_res and ver_res.report_pdf_path:
        file_path = Path(ver_res.report_pdf_path)
        if file_path.exists() and file_path.stat().st_size > 0:
            return str(file_path)

    # Need to generate or regenerate report
    docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == app.id).all()
    profile = db.query(ApplicationProfile).filter(ApplicationProfile.id == app.application_profile_id).first()
    profile_name = profile.name if profile else "Indian Citizen Document Verification"
    jurisdiction = profile.jurisdiction if profile else "India"

    # Evaluate expiry
    expiry_analysis = expiry_detector.analyze_documents(docs)
    expired_list = expiry_analysis["expired"]
    expiring_soon_list = expiry_analysis["expiring_soon"]
    expired_doc_ids = [d["document_id"] for d in expired_list]

    # Evaluate requirements
    reqs = profile.requirements if profile else []
    req_analysis = requirement_checker.evaluate_requirements(
        reqs,
        docs,
        expired_doc_ids=expired_doc_ids
    )

    # Evaluate mismatches
    mismatches = mismatch_detector.detect_mismatches(docs)

    # Gather tampering / anomaly flags
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
                "explanation": d.tampering_analysis.explanation or "Potential visual anomaly"
            })

    # Summary of uploaded documents
    uploaded_summary = []
    for d in docs:
        fields_summary = []
        for f in d.extracted_fields:
            if f.effective_value:
                fields_summary.append(f"{f.field_key.replace('_', ' ').title()}: {f.effective_value}")
        
        uploaded_summary.append({
            "filename": d.original_filename,
            "category": d.doc_category,
            "confidence": int(round(d.ocr_overall_confidence * 100)),
            "extracted_text": ", ".join(fields_summary) if fields_summary else "Basic digital scan verified"
        })

    # Determine status
    has_missing_mandatory = req_analysis["has_missing_mandatory"]
    has_expired = len(expired_list) > 0
    has_severe_mismatch = any(m.get("requires_manual_review") for m in mismatches)
    has_tamper_flag = len(tampering_flags) > 0

    actions = list(req_analysis["recommended_actions"])
    if has_missing_mandatory:
        overall_status = "INCOMPLETE"
    elif has_expired or has_severe_mismatch or has_tamper_flag:
        overall_status = "REVIEW_REQUIRED"
        if has_expired:
            actions.append(f"Renew/replace {len(expired_list)} expired document(s).")
    else:
        overall_status = "COMPLETE" if len(docs) > 0 else "INCOMPLETE"
        if len(docs) > 0:
            actions.append("All expected mandatory checklist items satisfied.")

    applicant_name = app.user.full_name if app.user else "Applicant"
    pdf_path = report_generator.generate_pdf_report(
        application_ref=app.reference_number,
        profile_name=profile_name,
        jurisdiction=jurisdiction,
        applicant_name=applicant_name,
        overall_status=overall_status,
        satisfied_items=req_analysis["satisfied"],
        missing_items=req_analysis["missing"],
        expired_docs=expired_list,
        expiring_soon_docs=expiring_soon_list,
        mismatches=mismatches,
        tampering_flags=tampering_flags,
        recommended_actions=actions,
        uploaded_documents_summary=uploaded_summary
    )

    if not ver_res:
        ver_res = VerificationResult(user_application_id=app.id)
        db.add(ver_res)

    ver_res.overall_status = overall_status
    ver_res.set_json_field("satisfied_requirements", req_analysis["satisfied"])
    ver_res.set_json_field("missing_requirements", req_analysis["missing"])
    ver_res.set_json_field("expired_documents", expired_list)
    ver_res.set_json_field("expiring_soon_documents", expiring_soon_list)
    ver_res.set_json_field("detected_mismatches", mismatches)
    ver_res.set_json_field("tampering_flags", tampering_flags)
    ver_res.set_json_field("recommended_actions", actions)
    ver_res.report_pdf_path = pdf_path
    db.commit()

    return pdf_path

@router.get("/{application_id}/download")
def download_verification_report(
    application_id: str,
    token: Optional[str] = Query(None, description="Optional bearer token for direct browser links"),
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        report_file_path = _ensure_report_exists(app, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate verification report: {str(e)}"
        )

    file_path = Path(report_file_path)
    if not file_path.exists() or file_path.stat().st_size == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Generated report PDF is empty or missing from storage"
        )

    filename = f"QUBIX_Report_{app.reference_number}.pdf"
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )
