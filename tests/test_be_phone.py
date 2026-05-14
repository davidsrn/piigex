"""Tests for the be_phone detector.

https://en.wikipedia.org/wiki/Telephone_numbers_in_Belgium
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["be_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "0412345678",  # mobile 04xx (10 digits)
    "023456789",  # fixed Brussels 02 (9 digits)
    "033456789",  # fixed Antwerp 03 (9 digits)
    "+3223456789",  # Brussels with CC
    "+32 2 345 67 89",  # Brussels with CC and spaces
    "04 12 34 56 78",  # mobile with spaces
    "02 345 67 89",  # fixed with spaces
    "+32412345678",  # mobile with CC compact
    "02-345-67-89",  # fixed with dashes
    "0032412345678",  # mobile with 0032 CC
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
    "12345678",  # no 0 or +32 prefix
    "012345",  # too short
    "5551234567",  # invalid prefix for BE
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
    text = "Bel ons op 02 345 67 89 voor meer info."
    matches = s.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "02 345 67 89"


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "(Tel: 0412345678)"
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "0412345678"


# ---------------------------------------------------------------------------
# 4. Cross-region
# ---------------------------------------------------------------------------


def test_no_match_es_phone(s: Scrubber) -> None:
    # Spanish mobile 612345678: no 0 prefix
    assert s.scan("612345678") == []


def test_no_match_pt_phone(s: Scrubber) -> None:
    # Portuguese 912345678: starts with 9, no 0 prefix
    assert s.scan("912345678") == []


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["be_phone"], stable_tokens=True)
    text = "0412345678 en 0412345678"
    result = sc.clean(text)
    assert result.count("{{BE_PHONE_1}}") == 2


def test_stable_normalized_equivalents() -> None:
    sc = Scrubber(detectors=["be_phone"], stable_tokens=True)
    result = sc.clean("04 12 34 56 78 en 0412345678")
    assert result.count("{{BE_PHONE_1}}") == 2
