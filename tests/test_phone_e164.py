"""Tests for the intl_phone_e164 detector.

Positive vectors from ITU-T E.164 / Wikipedia E.164 examples (fake but format-valid).
https://en.wikipedia.org/wiki/E.164
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["intl_phone_e164"])


@pytest.fixture()
def s_noval() -> Scrubber:
    return Scrubber(detectors=["intl_phone_e164"], validate=False)


# ---------------------------------------------------------------------------
# 1. Positive
# ---------------------------------------------------------------------------

VALID_PHONES = [
    "+14155552671",  # US
    "+442071838750",  # UK
    "+34612345678",  # ES
    "+819012345678",  # JP
    "+551155256325",  # BR
    "+1 415 555 2671",  # US with spaces
    "+44 207 183 8750",  # UK with spaces
    "+34 612 345 678",  # ES with spaces
    "+49.30.12345678",  # DE with dots
    "+33-1-23-45-67-89",  # FR with dashes
]


@pytest.mark.parametrize("phone", VALID_PHONES)
def test_valid_detected(s: Scrubber, phone: str) -> None:
    matches = s.scan(phone)
    assert len(matches) == 1
    assert matches[0].valid is True
    assert matches[0].name == "intl_phone_e164"


# ---------------------------------------------------------------------------
# 2. Negative: shape-matches that fail validation
# ---------------------------------------------------------------------------

INVALID_PHONES = [
    "+0123456789",  # leading zero country code
    "+123456",  # too short (only 6 digits after +)
    "+12345678901234567",  # too long (16 digits after +)
    "+0999999999",  # leading zero
    "+1234",  # way too short
]


@pytest.mark.parametrize("phone", INVALID_PHONES)
def test_invalid_not_redacted(s: Scrubber, phone: str) -> None:
    assert s.clean(phone) == phone


def test_no_leading_zero_redacted(s: Scrubber) -> None:
    assert s.clean("+0123456789") == "+0123456789"


def test_too_short_no_match(s: Scrubber) -> None:
    assert s.scan("+123456") == []


def test_too_long_regex_matches_but_validate_rejects(s: Scrubber, s_noval: Scrubber) -> None:
    long_phone = "+12345678901234567"
    assert s_noval.clean(long_phone) != long_phone
    assert s.clean(long_phone) == long_phone


# ---------------------------------------------------------------------------
# 3. Embedded in sentence
# ---------------------------------------------------------------------------


def test_embedded_span(s: Scrubber) -> None:
    text = "Call me at +34 612 345 678 tomorrow."
    matches = s.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "+34 612 345 678"


def test_embedded_no_surrounding_context_consumed(s: Scrubber) -> None:
    text = "Phone: +14155552671, email: test@example.com"
    matches = s.scan(text)
    phone_matches = [m for m in matches if m.name == "intl_phone_e164"]
    assert len(phone_matches) == 1
    assert phone_matches[0].value == "+14155552671"


# ---------------------------------------------------------------------------
# 4. Cross-region isolation
# ---------------------------------------------------------------------------


def test_iban_not_matched(s: Scrubber) -> None:
    assert s.scan("ES9121000418450200051332") == []


def test_plain_number_not_matched(s: Scrubber) -> None:
    assert s.scan("14155552671") == []


def test_adjacent_alphanum_no_match(s: Scrubber) -> None:
    assert s.scan("prefix+14155552671") == []


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value_same_token() -> None:
    sc = Scrubber(detectors=["intl_phone_e164"], stable_tokens=True)
    text = "+14155552671 and +14155552671"
    result = sc.clean(text)
    assert result.count("{{INTL_PHONE_E164_1}}") == 2


def test_stable_different_values_different_tokens() -> None:
    sc = Scrubber(detectors=["intl_phone_e164"], stable_tokens=True)
    text = "+14155552671 and +442071838750"
    result = sc.clean(text)
    assert "{{INTL_PHONE_E164_1}}" in result
    assert "{{INTL_PHONE_E164_2}}" in result


def test_stable_normalized_equivalents_same_token() -> None:
    sc = Scrubber(detectors=["intl_phone_e164"], stable_tokens=True)
    compact = "+14155552671"
    spaced = "+1 415 555 2671"
    result = sc.clean(f"{compact} and {spaced}")
    assert result.count("{{INTL_PHONE_E164_1}}") == 2
