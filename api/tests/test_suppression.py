"""Tests for suppression list — hash-based privacy-safe opt-out."""
import hashlib
import pytest
from app.services.suppression import _hash


def _sha256(val: str) -> str:
    return hashlib.sha256(val.strip().lower().encode()).hexdigest()


def test_hash_deterministic():
    assert _hash("test@example.com") == _hash("test@example.com")


def test_hash_case_insensitive():
    assert _hash("Test@Example.COM") == _hash("test@example.com")


def test_hash_strips_whitespace():
    assert _hash("  test@example.com  ") == _hash("test@example.com")


def test_hash_none_returns_none():
    assert _hash(None) is None


def test_hash_empty_string_is_none():
    assert _hash("") is None


def test_hash_matches_sha256():
    email = "user@example.com"
    expected = hashlib.sha256(email.strip().lower().encode()).hexdigest()
    assert _hash(email) == expected


def test_hash_phone():
    phone = "+91 98765 43210"
    h = _hash(phone)
    assert h is not None
    assert len(h) == 64


def test_different_values_different_hashes():
    assert _hash("alice@example.com") != _hash("bob@example.com")
