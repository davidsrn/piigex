"""Tests for the us_phone detector.

https://en.wikipedia.org/wiki/North_American_Numbering_Plan
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["us_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "5552345678",
    "555-234-5678",
    "555.234.5678",
    "(555) 234-5678",
    "(555)234-5678",
    "1-555-234-5678",
    "+1 555-234-5678",
    "+1-555-234-5678",
    "+15552345678",
    "001-555-234-5678",
    "001 555 234 5678",
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
    "055-234-5678",  # area code starts with 0
    "155-234-5678",  # area code starts with 1
    "555-034-5678",  # exchange starts with 0
    "555-134-5678",  # exchange starts with 1
    "555-234-567",  # too short
    "123",  # way too short
]


@pytest.mark.parametrize("phone", INVALID)
def test_invalid_not_matched(s: Scrubber, phone: str) -> None:
    matches = s.scan(phone)
    for m in matches:
        assert m.valid is False


# ---------------------------------------------------------------------------
# 3. Embedded
# ---------------------------------------------------------------------------


def test_embedded_span(s: Scrubber) -> None:
    text = "Call us at (555) 234-5678 for support."
    matches = s.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "(555) 234-5678"


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "Tel: 555.234.5678."
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "555.234.5678"


# ---------------------------------------------------------------------------
# 4. Cross-region / cross-detector
# ---------------------------------------------------------------------------


def test_no_match_fr_phone_shape(s: Scrubber) -> None:
    # French number 0123456789: leading zero, no NANP shape
    matches = s.scan("0123456789")
    for m in matches:
        assert m.valid is False


def test_no_match_ssn_shape(s: Scrubber) -> None:
    # SSN xxx-xx-xxxx (3-2-4) should not be picked up by us_phone (3-3-4)
    assert s.scan("001-01-0001") == []


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["us_phone"], stable_tokens=True)
    text = "5552345678 and 5552345678"
    result = sc.clean(text)
    assert result.count("{{US_PHONE_1}}") == 2


def test_stable_normalized_equivalents() -> None:
    sc = Scrubber(detectors=["us_phone"], stable_tokens=True)
    result = sc.clean("(555) 234-5678 and 5552345678")
    assert result.count("{{US_PHONE_1}}") == 2
