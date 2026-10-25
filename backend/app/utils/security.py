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
