"""Tests for the fr_phone detector.

https://en.wikipedia.org/wiki/Telephone_numbers_in_France
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["fr_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "0123456789",  # fixed Paris area
    "0612345678",  # mobile 06xx
    "0712345678",  # mobile 07xx
    "0912345678",  # non-geographic 09xx
    "+33123456789",  # with CC, no trunk 0
    "+33 1 23 45 67 89",  # with CC, spaces
    "01 23 45 67 89",  # fixed with spaces
    "06 12 34 56 78",  # mobile with spaces
    "01.23.45.67.89",  # with dots
    "01-23-45-67-89",  # with dashes
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
    "00123456789",  # starts with 00: international prefix, not local
    "012345678",  # only 9 digits (local form needs 10)
    "123456789",  # no 0 prefix, not +33 form
    "12345",  # too short
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
    text = "Appelez le 01 23 45 67 89 pour plus d'infos."
    matches = s.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "01 23 45 67 89"


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "(Tél: 0612345678)"
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "0612345678"


# ---------------------------------------------------------------------------
# 4. Cross-region
# ---------------------------------------------------------------------------


def test_no_match_es_phone(s: Scrubber) -> None:
    # Spanish number 612345678: 9 digits, no 0 prefix
    assert s.scan("612345678") == []


def test_no_match_de_phone(s: Scrubber) -> None:
    # Generic German number: different pattern
    matches = s.scan("030123456789")
    for m in matches:
        assert m.valid is False


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["fr_phone"], stable_tokens=True)
    text = "0123456789 et 0123456789"
    result = sc.clean(text)
    assert result.count("{{FR_PHONE_1}}") == 2


def test_stable_normalized_equivalents() -> None:
    sc = Scrubber(detectors=["fr_phone"], stable_tokens=True)
    result = sc.clean("01 23 45 67 89 et 0123456789")
    assert result.count("{{FR_PHONE_1}}") == 2
