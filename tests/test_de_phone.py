"""Tests for the de_phone detector.

https://en.wikipedia.org/wiki/Telephone_numbers_in_Germany
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["de_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "030123456789",  # Berlin area (030)
    "089123456",  # Munich area (089)
    "040123456789",  # Hamburg (040)
    "+4930123456789",  # Berlin with CC
    "004930123456789",  # Berlin with 0049 CC
    "+49 30 12345678",  # Berlin with spaces
    "030 123 456 789",  # Berlin with spaces
    "0301234567",  # Berlin shorter
    "069 1234 5678",  # Frankfurt with spaces
    "+49 69 12345678",  # Frankfurt with CC
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
    "12345",  # too short
    "1234567890123456",  # too long
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
    text = "Rufen Sie 030 12345678 an."
    matches = s.scan(text)
    assert len(matches) >= 1
    assert any(m.valid for m in matches)


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "(Tel: 030123456789)"
    matches = s.scan(text)
    assert len(matches) >= 1


# ---------------------------------------------------------------------------
# 4. Cross-region
# ---------------------------------------------------------------------------


def test_no_match_es_phone_alone(s: Scrubber) -> None:
    # Spanish number 612345678 starts with 6xx: DE pattern expects 0xx
    # ES phone does not have 0-prefix so no match under de_phone
    matches = s.scan("612345678")
    for m in matches:
        assert m.valid is False


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["de_phone"], stable_tokens=True)
    text = "030123456789 und 030123456789"
    result = sc.clean(text)
    assert result.count("{{DE_PHONE_1}}") == 2
