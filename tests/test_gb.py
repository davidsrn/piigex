"""Tests for GB detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# GB_NHS
# ---------------------------------------------------------------------------

VALID_NHS = ["9434765919"]
INVALID_NHS = ["9434765910"]  # bad check digit


@pytest.fixture()
def nhs_scrubber() -> Scrubber:
    return Scrubber(detectors=["gb_nhs"])


@pytest.mark.parametrize("v", VALID_NHS)
def test_nhs_valid(nhs_scrubber: Scrubber, v: str) -> None:
    matches = nhs_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_NHS)
def test_nhs_invalid(nhs_scrubber: Scrubber, bad: str) -> None:
    matches = nhs_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_nhs_embedded(nhs_scrubber: Scrubber) -> None:
    text = "Patient NHS number: 9434765919 confirmed."
    m = nhs_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "9434765919"


def test_nhs_not_inside_word(nhs_scrubber: Scrubber) -> None:
    assert nhs_scrubber.scan("ref9434765919abc") == []


# ---------------------------------------------------------------------------
# GB_UTR
# ---------------------------------------------------------------------------

VALID_UTRS = ["1955839661", "1123456789"]
INVALID_UTRS = ["2955839661"]  # wrong check digit (stdnum raises InvalidChecksum)


@pytest.fixture()
def utr_scrubber() -> Scrubber:
    return Scrubber(detectors=["gb_utr"])


@pytest.mark.parametrize("v", VALID_UTRS)
def test_utr_valid(utr_scrubber: Scrubber, v: str) -> None:
    matches = utr_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_UTRS)
def test_utr_invalid(utr_scrubber: Scrubber, bad: str) -> None:
    matches = utr_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_utr_embedded(utr_scrubber: Scrubber) -> None:
    text = "HMRC UTR: 1955839661 for self-assessment."
    m = utr_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "1955839661"


def test_utr_not_inside_word(utr_scrubber: Scrubber) -> None:
    assert utr_scrubber.scan("ref1955839661abc") == []


# ---------------------------------------------------------------------------
# GB_VAT
# ---------------------------------------------------------------------------

VALID_VATS = [
    "GB980780684",  # standard 9-digit
    "GB980780684001",  # branch 12-digit
    "GBGD001",  # government department (GD000-GD499)
    "GBHA500",  # health authority (HA500-HA999)
]
INVALID_VATS = [
    "GB802311781",  # bad checksum (stdnum docs example)
    "GB980780683",  # wrong last digit
]


@pytest.fixture()
def vat_scrubber() -> Scrubber:
    return Scrubber(detectors=["gb_vat"])


@pytest.mark.parametrize("v", VALID_VATS)
def test_vat_valid(vat_scrubber: Scrubber, v: str) -> None:
    matches = vat_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_VATS)
def test_vat_invalid(vat_scrubber: Scrubber, bad: str) -> None:
    matches = vat_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_vat_embedded(vat_scrubber: Scrubber) -> None:
    text = "Invoice VAT GB980780684 attached."
    m = vat_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "GB980780684"


def test_vat_not_inside_word(vat_scrubber: Scrubber) -> None:
    assert vat_scrubber.scan("refGB980780684abc") == []


def test_vat_no_match_without_prefix(vat_scrubber: Scrubber) -> None:
    # Compact form without GB prefix must not match; avoids fr_siren/us_rtn collision.
    assert vat_scrubber.scan("980780684") == []


# ---------------------------------------------------------------------------
# GB_NINO
# ---------------------------------------------------------------------------

VALID_NINOS = ["AB123456A", "AB 12 34 56 A"]
INVALID_NINO_RESERVED = [
    "BG123456A",  # BG reserved
    "GB123456A",  # GB reserved
    "TN123456A",  # TN reserved
    "ZZ123456A",  # ZZ reserved
]


@pytest.fixture()
def nino_scrubber() -> Scrubber:
    return Scrubber(detectors=["gb_nino"])


@pytest.mark.parametrize("v", VALID_NINOS)
def test_nino_valid(nino_scrubber: Scrubber, v: str) -> None:
    matches = nino_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_NINO_RESERVED)
def test_nino_reserved_prefix(nino_scrubber: Scrubber, bad: str) -> None:
    # Pattern matches the shape; validator rejects the reserved prefix.
    matches = nino_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_nino_excluded_suffix_no_match(nino_scrubber: Scrubber) -> None:
    # E is not in [A-D]: pattern-level rejection.
    assert nino_scrubber.scan("AB123456E") == []


def test_nino_excluded_first_letter_no_match(nino_scrubber: Scrubber) -> None:
    # D is excluded from first letter: pattern-level rejection.
    assert nino_scrubber.scan("DA123456A") == []


def test_nino_excluded_second_letter_no_match(nino_scrubber: Scrubber) -> None:
    # F is excluded from second letter: pattern-level rejection.
    assert nino_scrubber.scan("AF123456A") == []


def test_nino_spaced_form_value(nino_scrubber: Scrubber) -> None:
    matches = nino_scrubber.scan("AB 12 34 56 A")
    assert len(matches) == 1
    assert matches[0].value == "AB 12 34 56 A"


def test_nino_embedded(nino_scrubber: Scrubber) -> None:
    text = "National Insurance: AB123456A on record."
    m = nino_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "AB123456A"


def test_nino_not_inside_word(nino_scrubber: Scrubber) -> None:
    assert nino_scrubber.scan("refAB123456Aabc") == []


def test_nino_no_overlap_with_dea(nino_scrubber: Scrubber) -> None:
    # DEA numbers are 2 letters + 7 digits (end in a digit).
    # NINO ends in [A-D], so DEA-shaped strings must not match.
    assert nino_scrubber.scan("AB1234563") == []


# ---------------------------------------------------------------------------
# Cross-detector / integration
# ---------------------------------------------------------------------------


def test_gb_detectors_default_on() -> None:
    s = Scrubber()
    text = "NHS 9434765919, UTR 1955839661, VAT GB980780684, NINO AB123456A."
    redacted = s.clean(text)
    for raw in ("9434765919", "1955839661", "GB980780684", "AB123456A"):
        assert raw not in redacted, f"{raw!r} leaked into redacted output"


def test_gb_region_filter() -> None:
    s = Scrubber(regions=["gb"])
    matches = {m.name for m in s.scan("NHS 9434765919 UTR 1955839661") if m.valid}
    assert "gb_nhs" in matches or "gb_utr" in matches


def test_known_10digit_gb_collision() -> None:
    # 10-digit values can match gb_nhs, gb_utr, bg_pnf, or us_npi depending
    # on which checksums pass. The value must always be scrubbed; only the
    # token label varies. This test documents the known behaviour.
    s = Scrubber()
    matches = {m.value: m.name for m in s.scan("9434765919") if m.valid}
    assert "9434765919" in matches
    assert matches["9434765919"] in {"gb_nhs", "gb_utr", "bg_pnf", "us_npi"}
