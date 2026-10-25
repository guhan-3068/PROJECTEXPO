import io
import os
import uuid
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageChops, ImageEnhance
from app.config import settings

SUSPICIOUS_SOFTWARE_KEYWORDS = [
    "photoshop", "gimp", "canva", "coreldraw", "illustrator",
    "pdfescape", "sejda", "ilovepdf", "smallpdf", "paint.net", "acrobat distiller"
]

class TamperingDetector:
    """
    Forensic image analysis engine.
    Detects compression anomalies (Error Level Analysis - ELA)
    and inspects metadata for image-editing signatures.
    Always produces explainable diagnostics for human review.
    """

    def analyze_document(
        self,
        file_bytes: bytes,
        mime_type: str,
        document_id: str
    ) -> Dict[str, Any]:
        anomalies: List[str] = []
        software_detected = None
        ela_score = 0.0
        ela_image_filename = None

        # 1. Metadata / Software Inspection
        software_detected, meta_anomalies = self._inspect_metadata(file_bytes, mime_type)
        if software_detected:
            anomalies.append(f"Edited with software: {software_detected}")
        anomalies.extend(meta_anomalies)

        # 2. Forensic ELA (Error Level Analysis) for raster images
        if mime_type.startswith("image/"):
            ela_score, ela_path = self._perform_ela(file_bytes, document_id)
            if ela_path:
                ela_image_filename = os.path.basename(ela_path)
            if ela_score > 28.0:
                anomalies.append(f"High compression variance detected (ELA score {ela_score:.1f}). Possible localized editing or splice.")
        elif mime_type == "application/pdf":
            # For PDFs, extract first page image if available and run ELA
            pdf_ela_score, ela_path = self._perform_pdf_ela(file_bytes, document_id)
            if pdf_ela_score > 0:
                ela_score = pdf_ela_score
                if ela_path:
                    ela_image_filename = os.path.basename(ela_path)
                if ela_score > 28.0:
                    anomalies.append(f"Page image compression discrepancy (ELA score {ela_score:.1f}).")

        # 3. Risk Level Determination
        is_flagged = len(anomalies) > 0
        if not is_flagged:
            risk_level = "LOW"
            explanation = "Document exhibits uniform compression and standard metadata structure."
        elif len(anomalies) >= 2 or (software_detected and "photoshop" in software_detected.lower()):
            risk_level = "HIGH"
            explanation = (
                f"Document flagged for manual review due to {len(anomalies)} anomalies: "
                f"{'; '.join(anomalies)}. Human reviewer inspection required before processing."
            )
        else:
            risk_level = "MEDIUM"
            explanation = (
                f"Potential formatting or metadata irregularity observed: {'; '.join(anomalies)}. "
                "Advisory review recommended."
            )

        return {
            "is_flagged": is_flagged,
            "risk_level": risk_level,
            "ela_score": round(ela_score, 2),
            "software_detected": software_detected,
            "detected_anomalies": anomalies,
            "explanation": explanation,
            "ela_artifact_path": ela_image_filename
        }

    def _inspect_metadata(self, data: bytes, mime_type: str) -> Tuple[Optional[str], List[str]]:
        anomalies = []
        detected_software = None

        if mime_type == "application/pdf":
            # Check PDF trailer dictionary and info dictionary
            lower_head = data[:4096].lower() + data[-8192:].lower()
            for kw in SUSPICIOUS_SOFTWARE_KEYWORDS:
                if kw.encode() in lower_head:
                    detected_software = kw.title()
                    break

            # Check if PDF contains incremental updates or multiple EOF markers
            eof_count = data.count(b"%%EOF")
            if eof_count > 3:
                anomalies.append(f"Multiple PDF revision revisions detected ({eof_count} updates)")

        elif mime_type.startswith("image/"):
            # Inspect direct byte stream for PNG/JPEG software chunk signatures
            lower_bytes = data.lower()
            for kw in SUSPICIOUS_SOFTWARE_KEYWORDS:
                if kw.encode() in lower_bytes:
                    detected_software = kw.title()
                    break

            try:
                img = Image.open(io.BytesIO(data))
                info = img.info or {}
                # Check EXIF / software tag
                software = info.get("Software") or info.get("software")
                if software and not detected_software:
                    for kw in SUSPICIOUS_SOFTWARE_KEYWORDS:
                        if kw in str(software).lower():
                            detected_software = str(software)
                            break
            except Exception:
                pass

        return detected_software, anomalies

    def _perform_ela(self, img_bytes: bytes, document_id: str, quality: int = 90) -> Tuple[float, str]:
        """
        Executes Error Level Analysis (ELA):
        Re-saves image at specified quality and compares pixel delta.
        """
        try:
            original = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            # Recompress in-memory
            buffer = io.BytesIO()
            original.save(buffer, "JPEG", quality=quality)
            buffer.seek(0)
            recompressed = Image.open(buffer)

            # Compute absolute difference
            diff = ImageChops.difference(original, recompressed)
            
            # Enhance difference for visual artifact rendering
            extrema = diff.getextrema()
            max_diff = max([ex[1] for ex in extrema])
            scale = 255.0 / max_diff if max_diff > 0 else 1.0
            enhanced = ImageEnhance.Brightness(diff).enhance(scale)

            # Calculate average anomaly score
            gray_diff = diff.convert("L")
            stat = getattr(gray_diff, "get_flattened_data", gray_diff.getdata)()
            avg_diff = sum(stat) / len(stat) if len(stat) > 0 else 0.0

            # Save ELA visualization artifact
            artifact_name = f"ela_{document_id}_{uuid.uuid4().hex[:8]}.jpg"
            artifact_path = settings.STORAGE_ROOT / "ela_cache" / artifact_name
            enhanced.save(artifact_path, "JPEG")

            return avg_diff, str(artifact_path)
        except Exception:
            return 0.0, ""

    def _perform_pdf_ela(self, pdf_bytes: bytes, document_id: str) -> Tuple[float, str]:
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            if len(doc) > 0:
                pix = doc[0].get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                doc.close()
                return self._perform_ela(img_bytes, document_id)
        except Exception:
            pass
        return 0.0, ""

tampering_detector = TamperingDetector()
