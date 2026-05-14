"""Tests for the es_phone detector.

https://en.wikipedia.org/wiki/Telephone_numbers_in_Spain
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["es_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "612345678",  # mobile 6xx
    "712345678",  # mobile 7xx
    "912345678",  # fixed 9xx
    "812345678",  # fixed 8xx
    "+34612345678",  # with country code
    "0034612345678",  # with 00 prefix
    "612 345 678",  # with spaces
    "612-345-678",  # with dashes
    "+34 612 345 678",
    "912.345.678",
]


@pytest.mark.parametrize("phone", VALID)
def test_valid_detected(s: Scrubber, phone: str) -> None:
    matches = s.scan(phone)
    assert len(matches) == 1
    assert matches[0].valid is True


# ---------------------------------------------------------------------------
# 2. Negative
# ---------------------------------------------------------------------------

INVALID = [
    "112345678",  # starts with 1: not valid ES phone
    "212345678",  # starts with 2
    "312345678",  # starts with 3
    "512345678",  # starts with 5
    "61234567",  # too short (8 digits)
    "6123456789",  # too long (10 digits)
    "123",  # way too short
]


@pytest.mark.parametrize("phone", INVALID)
def test_invalid_not_matched_or_invalid(s: Scrubber, phone: str) -> None:
    matches = s.scan(phone)
    for m in matches:
        assert m.valid is False


# ---------------------------------------------------------------------------
# 3. Embedded
# ---------------------------------------------------------------------------


def test_embedded_span(s: Scrubber) -> None:
    text = "Llámame al 612 345 678 mañana."
    matches = s.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "612 345 678"


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "(Teléfono: 912345678)"
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "912345678"


# ---------------------------------------------------------------------------
# 4. Cross-region
# ---------------------------------------------------------------------------


def test_no_match_de_phone(s: Scrubber) -> None:
    # German number starting with 0: not an ES phone
    assert s.scan("030123456789") == []


def test_no_match_fr_phone(s: Scrubber) -> None:
    # French number 01 23 45 67 89
    assert s.scan("0123456789") == []


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["es_phone"], stable_tokens=True)
    text = "612345678 y 612345678"
    result = sc.clean(text)
    assert result.count("{{ES_PHONE_1}}") == 2


def test_stable_normalized_equivalents() -> None:
    sc = Scrubber(detectors=["es_phone"], stable_tokens=True)
    result = sc.clean("612 345 678 y 612345678")
    assert result.count("{{ES_PHONE_1}}") == 2
