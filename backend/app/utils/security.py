import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from app.config import settings

# Derive a valid 32-byte urlsafe base64 key from configuration
def _derive_fernet_key(raw_key: str) -> bytes:
    try:
        # Check if already a valid 32-byte Fernet key
        key_bytes = raw_key.encode()
        Fernet(key_bytes)
        return key_bytes
    except Exception:
        # Deterministically derive 32 bytes using SHA-256 and base64-encode
        digest = hashlib.sha256(raw_key.encode()).digest()
        return base64.urlsafe_b64encode(digest)

fernet_key = _derive_fernet_key(settings.ENCRYPTION_KEY)
fernet_cipher = Fernet(fernet_key)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# Encryption at rest
def encrypt_bytes(data: bytes) -> bytes:
    """Encrypts raw binary data using AES-256-CBC / HMAC (Fernet)."""
    return fernet_cipher.encrypt(data)

def decrypt_bytes(encrypted_data: bytes) -> bytes:
    """Decrypts ciphertext back to original binary."""
    return fernet_cipher.decrypt(encrypted_data)


# Privacy & Data Minimization Masking Helpers
def mask_aadhaar_number(val: str) -> str:
    """Masks 12-digit Aadhaar number as XXXX-XXXX-1234."""
    if not val:
        return "XXXX-XXXX-XXXX"
    clean = "".join(filter(str.isdigit, str(val)))
    if len(clean) >= 4:
        return f"XXXX-XXXX-{clean[-4:]}"
    return "XXXX-XXXX-XXXX"


def mask_pan_number(val: str) -> str:
    """Masks 10-character PAN number preserving first 2 and last 2 characters (e.g., AB***4F)."""
    if not val:
        return "XX***XX"
    s = str(val).strip().upper()
    if len(s) >= 4:
        return f"{s[:2]}***{s[-2:]}"
    return "XX***XX"


def mask_sensitive_value(field_key: str, val: Any) -> str:
    """
    Intelligently masks sensitive personal data according to Indian privacy guidelines.
    """
    if val is None:
        return "N/A"
    s = str(val).strip()
    if not s:
        return ""

    fk = field_key.lower()

    if "aadhaar" in fk or "uid" in fk:
        return mask_aadhaar_number(s)
    elif "pan" in fk:
        return mask_pan_number(s)
    elif "account" in fk or "bank" in fk:
        digits = "".join(filter(str.isdigit, s))
        if len(digits) >= 4:
            return f"XXXX-XXXX-{digits[-4:]}"
        return "XXXX-XXXX-XXXX"
    elif "phone" in fk or "mobile" in fk:
        digits = "".join(filter(str.isdigit, s))
        if len(digits) >= 4:
            return f"XXXXXX{digits[-4:]}"
        return "XXXXXXXXXX"
    elif "ration" in fk or "smart_card" in fk:
        if len(s) >= 4:
            return f"XX/X/{s[-4:]}"
        return "XX/X/XXXX"
    elif "passport" in fk:
        if len(s) >= 3:
            return f"{s[0]}*****{s[-2:]}"
        return "X*****XX"
    elif "license" in fk or "dl" in fk:
        if len(s) >= 4:
            return f"DL-**-***{s[-4:]}"
        return "DL-**-*****"

    return s
