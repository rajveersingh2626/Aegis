import pytest
from core.auth import hash_password, verify_password

def test_password_hashing_consistency():
    password = "MySecurePassword123"
    hashed = hash_password(password)

    assert isinstance(hashed, str)
    assert hashed != password

def test_password_verification_success():
    password = "TestPass456"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True

def test_password_verification_failure():
    password = "TestPass456"
    hashed = hash_password(password)
    incorrect_password = "WrongPass789"

    assert verify_password(incorrect_password, hashed) is False

def test_password_verification_type_handling():
    password = "TestPass789"
    hashed = hash_password(password)

    assert verify_password("", hashed) is False
