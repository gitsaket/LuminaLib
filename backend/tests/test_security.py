"""Pure unit tests for app.core.security — no DB required."""
import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_produces_unique_hashes():
    h1 = hash_password("secret")
    h2 = hash_password("secret")
    assert h1 != h2  # bcrypt includes a random salt


def test_verify_password_success():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_wrong_plain():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_roundtrip():
    token = create_access_token("42")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_create_refresh_token_type():
    token = create_refresh_token("99")
    payload = decode_token(token)
    assert payload["sub"] == "99"
    assert payload["type"] == "refresh"


def test_decode_token_raises_on_tampered_token():
    token = create_access_token("1")
    tampered = token[:-4] + "xxxx"
    with pytest.raises(JWTError):
        decode_token(tampered)
