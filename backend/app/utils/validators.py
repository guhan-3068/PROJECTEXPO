import os
import re
import hashlib
from typing import Tuple
from app.config import settings

MAGIC_SIGNATURES = {
    b"%PDF-": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png"
}

def detect_mime_from_bytes(data: bytes) -> str:
    """Inspects header magic bytes to verify actual content type."""
    for magic, mime in MAGIC_SIGNATURES.items():
        if data.startswith(magic):
            return mime
    return "application/octet-stream"

def sanitize_filename(filename: str) -> str:
    """Removes path traversal components and unsafe symbols from filename."""
    base = os.path.basename(filename)
    # Strip any directory separators and invalid characters
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    return sanitized or "unnamed_document"

def compute_sha256(data: bytes) -> str:
    """Calculates SHA-256 hexadecimal digest for document integrity."""
    return hashlib.sha256(data).hexdigest()

def validate_uploaded_file(filename: str, data: bytes) -> Tuple[bool, str, str]:
    """
    Validates file extension, magic signature, and size limit.
    Returns: (is_valid: bool, mime_type: str, error_message: str)
    """
    # 1. Size check
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        return False, "", f"File exceeds maximum allowed size of {max_mb:.0f} MB"

    if len(data) == 0:
        return False, "", "File is empty (0 bytes)"

    # 2. Extension check
    _, ext = os.path.splitext(filename.lower())
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, "", f"Unsupported file extension '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"

    # 3. Magic byte check
    detected_mime = detect_mime_from_bytes(data)
    if detected_mime not in settings.ALLOWED_MIME_TYPES:
        return False, detected_mime, f"File content does not match allowed types (detected {detected_mime})"

    return True, detected_mime, ""
