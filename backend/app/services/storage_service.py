import os
import uuid
from pathlib import Path
from typing import Tuple
from app.config import settings
from app.utils.security import encrypt_bytes, decrypt_bytes
from app.utils.validators import sanitize_filename, compute_sha256

class StorageService:
    def __init__(self, base_dir: Path = settings.STORAGE_ROOT):
        self.base_dir = Path(base_dir)
        self.encrypted_dir = self.base_dir / "encrypted"
        self.ela_dir = self.base_dir / "ela_cache"
        self.reports_dir = self.base_dir / "reports"

        self.encrypted_dir.mkdir(parents=True, exist_ok=True)
        self.ela_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save_document(self, original_filename: str, raw_bytes: bytes) -> Tuple[str, str, str]:
        """
        Saves uploaded file securely:
        1. Generates unique stored filename
        2. Encrypts payload at rest using AES-256
        3. Writes to private encrypted storage
        4. Returns (stored_filename, absolute_path, sha256_hash)
        """
        sanitized = sanitize_filename(original_filename)
        ext = os.path.splitext(sanitized)[1]
        stored_filename = f"{uuid.uuid4().hex}{ext}.enc"
        target_path = self.encrypted_dir / stored_filename

        encrypted_data = encrypt_bytes(raw_bytes)
        with open(target_path, "wb") as f:
            f.write(encrypted_data)

        sha256_hash = compute_sha256(raw_bytes)
        return stored_filename, str(target_path), sha256_hash

    def read_document_bytes(self, file_path: str) -> bytes:
        """Reads encrypted document from disk and returns decrypted plain bytes."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            encrypted_data = f.read()

        return decrypt_bytes(encrypted_data)

    def delete_document(self, file_path: str) -> bool:
        """Permanently removes stored document for data retention compliance."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

storage_service = StorageService()
