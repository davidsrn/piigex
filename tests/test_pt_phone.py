"""Tests for the pt_phone detector.

https://en.wikipedia.org/wiki/Telephone_numbers_in_Portugal
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["pt_phone"])


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID = [
    "912345678",  # mobile 9xx
    "932345678",  # mobile 93x
    "961234567",  # mobile 96x
    "212345678",  # fixed Lisbon 21x
    "222345678",  # fixed Porto 22x
    "+351912345678",  # with CC
    "00351212345678",  # with 00351 CC
    "912 345 678",  # with spaces
    "212-345-678",  # with dashes
    "+351 21 234 5678",  # with CC and spaces
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
    "112345678",  # starts with 1: not PT phone
    "512345678",  # starts with 5
    "812345678",  # starts with 8
    "91234567",  # too short (8 digits)
    "9123456789",  # too long (10 digits)
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
    text = "Ligue para 912 345 678 agora."
    matches = s.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "912 345 678"


def test_embedded_with_punctuation(s: Scrubber) -> None:
    text = "(Tel: 212345678)"
    matches = s.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "212345678"


# ---------------------------------------------------------------------------
# 4. Cross-region
# ---------------------------------------------------------------------------


def test_no_match_es_phone(s: Scrubber) -> None:
    # Spanish 612345678 starts with 6: not valid for PT (only 2 or 9)
    assert s.scan("612345678") == []


def test_no_match_fr_phone(s: Scrubber) -> None:
    # French 0612345678 starts with 0: not valid for PT
    assert s.scan("0612345678") == []


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value() -> None:
    sc = Scrubber(detectors=["pt_phone"], stable_tokens=True)
    text = "912345678 e 912345678"
    result = sc.clean(text)
    assert result.count("{{PT_PHONE_1}}") == 2


def test_stable_normalized_equivalents() -> None:
    sc = Scrubber(detectors=["pt_phone"], stable_tokens=True)
    result = sc.clean("912 345 678 e 912345678")
    assert result.count("{{PT_PHONE_1}}") == 2
