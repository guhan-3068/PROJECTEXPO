import pytest
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, decode_access_token,
    encrypt_bytes, decrypt_bytes
)

def test_password_hashing():
    raw = "SecurePassword123!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_roundtrip():
    payload = {"sub": "user-uuid-123", "role": "USER"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-uuid-123"
    assert decoded["role"] == "USER"

def test_aes_at_rest_encryption():
    secret_doc = b"%PDF-1.4 Confident Identity Record Details"
    encrypted = encrypt_bytes(secret_doc)
    assert encrypted != secret_doc
    assert b"Confident" not in encrypted
    decrypted = decrypt_bytes(encrypted)
    assert decrypted == secret_doc
