from datetime import timedelta
from uuid import uuid4
import pytest
from app.domain.identity.security import (
    InvalidTokenError,
    create_jwt,
    decode_jwt,
    validate_password,
    verify_password,
    hash_password,
)


def test_password_hash_is_verified_without_plaintext() -> None:
    hashed = hash_password("SecurePassword123")
    assert hashed != "SecurePassword123"
    assert verify_password("SecurePassword123", hashed)
    assert not verify_password("wrong", hashed)


@pytest.mark.parametrize("password", ["password123", "alllowercase123", "ALLUPPERCASE123"])
def test_weak_passwords_are_rejected(password: str) -> None:
    with pytest.raises(ValueError):
        validate_password(password, "person@example.com")


def test_jwt_type_is_enforced() -> None:
    secret = "a" * 64
    token = create_jwt(secret, uuid4(), "access", timedelta(minutes=5), 1)
    assert decode_jwt(token, secret, "access")["typ"] == "access"
    with pytest.raises(InvalidTokenError):
        decode_jwt(token, secret, "refresh")
