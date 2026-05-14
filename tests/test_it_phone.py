"""Tests for the it_phone detector.

https://en.wikipedia.org/wiki/Telephone_numbers_in_Italy
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["it_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "3201234567",  # mobile 10 digits starting with 3
    "3331234567",  # mobile Vodafone prefix
    "3481234567",  # mobile TIM prefix
    "0212345678",  # fixed Milan (02 + 8 digits)
    "0612345678",  # fixed Rome (06 + 8 digits)
    "+393201234567",  # mobile with country code
    "+390612345678",  # fixed with country code
    "00393201234567",  # with 0039 prefix + full mobile
    "320 123 4567",  # mobile with spaces
    "02 1234 5678",  # fixed with spaces
]


@pytest.mark.parametrize("phone", VALID)
def test_valid_detected(s: Scrubber, phone: str) -> None:
    matches = s.scan(phone)
    assert len(matches) >= 1
    assert any(m.valid for m in matches)


# ---------------------------------------------------------------------------
# 2. Negative
# ---------------------------------------------------------------------------

INVALID = [
    "123456789",  # no valid Italian prefix
    "5551234567",  # starts with 5: not Italian
    "12345",  # too short
    "123456789012345",  # too long
]


@pytest.mark.parametrize("phone", INVALID)
def test_invalid_not_matched_or_invalid(s: Scrubber, phone: str) -> None:
    matches = s.scan(phone)
    for m in matches:
        assert m.valid is False


# ---------------------------------------------------------------------------
# 3. Embedded
# ---------------------------------------------------------------------------


def test_embedded_mobile(s: Scrubber) -> None:
    text = "Chiama il 320 123 4567 per info."
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].valid is True


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "(Tel: 0212345678)"
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "0212345678"


# ---------------------------------------------------------------------------
# 4. Cross-region
# ---------------------------------------------------------------------------


def test_no_match_es_phone(s: Scrubber) -> None:
    # Spanish mobile 612345678: starts with 6, not valid for Italy
    matches = s.scan("612345678")
    for m in matches:
        assert m.valid is False


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["it_phone"], stable_tokens=True)
    text = "3201234567 e 3201234567"
    result = sc.clean(text)
    assert result.count("{{IT_PHONE_1}}") == 2
