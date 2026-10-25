import io
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import UserApplication
from app.models.document import UploadedDocument
from app.models.extracted_field import ExtractedField
from app.models.tampering import TamperingAnalysis
from app.models.user import User
from app.schemas.document import DocumentOut, FieldCorrectionRequest
from app.routers.auth import get_current_user, get_current_user_flexible
from app.utils.validators import validate_uploaded_file
from app.services.storage_service import storage_service
from app.services.ocr_engine import ocr_engine
from app.services.field_extractor import field_extractor
from app.services.tampering_detector import tampering_detector

router = APIRouter(prefix="/documents", tags=["Documents"])

def _format_doc_out(doc: UploadedDocument) -> dict:
    t_data = None
    if doc.tampering_analysis:
        t_data = {
            "is_flagged": doc.tampering_analysis.is_flagged,
            "risk_level": doc.tampering_analysis.risk_level,
            "ela_anomaly_score": doc.tampering_analysis.ela_anomaly_score,
            "metadata_software_detected": doc.tampering_analysis.metadata_software_detected,
            "detected_anomalies": doc.tampering_analysis.get_detected_anomalies(),
            "explanation": doc.tampering_analysis.explanation
        }

    fields_out = []
    for f in doc.extracted_fields:
        fields_out.append({
            "id": f.id,
            "field_key": f.field_key,
            "raw_value": f.raw_value,
            "normalized_value": f.normalized_value,
            "confidence": f.confidence,
            "is_user_corrected": f.is_user_corrected,
            "corrected_value": f.corrected_value,
            "effective_value": f.effective_value,
            "notes": f.notes
        })

    return {
        "id": doc.id,
        "user_application_id": doc.user_application_id,
        "original_filename": doc.original_filename,
        "file_size_bytes": doc.file_size_bytes,
        "mime_type": doc.mime_type,
        "doc_category": doc.doc_category,
        "user_assigned_category": doc.user_assigned_category,
        "ocr_status": doc.ocr_status,
        "ocr_overall_confidence": doc.ocr_overall_confidence,
        "created_at": doc.created_at,
        "extracted_fields": fields_out,
        "tampering_analysis": t_data
    }

@router.post("/upload/{application_id}", response_model=List[DocumentOut])
async def upload_documents(
    application_id: str,
    files: List[UploadFile] = File(...),
    claimed_category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify application access
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    uploaded_results = []

    for file in files:
        contents = await file.read()
        filename = file.filename or "uploaded_document"

        # Validate file
        is_valid, mime_type, err = validate_uploaded_file(filename, contents)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed for '{filename}': {err}"
            )

        # 1. Encrypt and save to secure storage
        stored_name, file_path, sha256_hash = storage_service.save_document(filename, contents)

        # 2. Perform OCR
        ocr_res = ocr_engine.extract_text(contents, mime_type)
        raw_text = ocr_res.get("raw_text", "")
        ocr_conf = ocr_res.get("confidence", 0.0)

        # 3. Classify Document
        cat, cat_conf = field_extractor.classify_document(raw_text, claimed_category)

        # 4. Create Document Entity
        doc = UploadedDocument(
            user_application_id=app.id,
            user_id=current_user.id,
            original_filename=filename,
            stored_filename=stored_name,
            file_path=file_path,
            file_size_bytes=len(contents),
            mime_type=mime_type,
            file_hash_sha256=sha256_hash,
            is_encrypted=True,
            doc_category=cat,
            user_assigned_category=claimed_category,
            ocr_status="SUCCESS" if raw_text else "FAILED",
            ocr_overall_confidence=ocr_conf,
            raw_text=raw_text
        )
        db.add(doc)
        db.flush()

        # 5. Extract structured fields
        extracted = field_extractor.extract_fields(raw_text)
        for ef in extracted:
            field_obj = ExtractedField(
                document_id=doc.id,
                field_key=ef["field_key"],
                raw_value=ef.get("raw_value"),
                normalized_value=ef.get("normalized_value"),
                confidence=ef.get("confidence", 0.0),
                notes=ef.get("notes")
            )
            db.add(field_obj)

        # 6. Run Tampering & Anomaly Detection
        tamper_res = tampering_detector.analyze_document(contents, mime_type, doc.id)
        tamper_obj = TamperingAnalysis(
            document_id=doc.id,
            is_flagged=tamper_res["is_flagged"],
            risk_level=tamper_res["risk_level"],
            ela_anomaly_score=tamper_res["ela_score"],
            metadata_software_detected=tamper_res.get("software_detected"),
            explanation=tamper_res.get("explanation"),
            ela_artifact_path=tamper_res.get("ela_artifact_path")
        )
        tamper_obj.set_detected_anomalies(tamper_res.get("detected_anomalies", []))
        db.add(tamper_obj)

        db.commit()
        db.refresh(doc)
        uploaded_results.append(_format_doc_out(doc))

    return uploaded_results

@router.get("/application/{application_id}", response_model=List[DocumentOut])
def get_application_documents(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(UserApplication).filter(UserApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    docs = db.query(UploadedDocument).filter(UploadedDocument.user_application_id == application_id).all()
    return [_format_doc_out(d) for d in docs]

@router.put("/{document_id}/fields", response_model=DocumentOut)
def correct_document_field(
    document_id: str,
    payload: FieldCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    field = db.query(ExtractedField).filter(
        ExtractedField.document_id == document_id,
        ExtractedField.field_key == payload.field_key
    ).first()

    if not field:
        # Create new corrected field if not previously detected by OCR
        field = ExtractedField(
            document_id=document_id,
            field_key=payload.field_key,
            raw_value=payload.corrected_value,
            normalized_value=payload.corrected_value,
            confidence=1.0,
            is_user_corrected=True,
            corrected_value=payload.corrected_value,
            notes=payload.notes or "Manually added by user"
        )
        db.add(field)
    else:
        field.is_user_corrected = True
        field.corrected_value = payload.corrected_value
        field.notes = payload.notes or "Corrected by user"

    db.commit()
    db.refresh(doc)
    return _format_doc_out(doc)

@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    token: Optional[str] = None,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        decrypted_bytes = storage_service.read_document_bytes(doc.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve encrypted document")

    return Response(
        content=decrypted_bytes,
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'inline; filename="{doc.original_filename}"'}
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id and current_user.role.upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    storage_service.delete_document(doc.file_path)
    db.delete(doc)
    db.commit()
    return None
