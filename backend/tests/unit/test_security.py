import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_produces_a_verifiable_hash():
    plain = "CorrectHorseBatteryStaple"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("CorrectHorseBatteryStaple")
    assert verify_password("WrongPassword", hashed) is False


def test_create_and_decode_access_token_round_trips():
    token = create_access_token(subject="42", role="OWNER")
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "OWNER"
    assert "exp" in payload


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(subject="42", role="OWNER")
    tampered = token + "invalid"

    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered)