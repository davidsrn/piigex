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
    "GB980780684",       # standard 9-digit
    "GB980780684001",    # branch 12-digit
    "GBGD001",           # government department (GD000-GD499)
    "GBHA500",           # health authority (HA500-HA999)
]
INVALID_VATS = [
    "GB802311781",   # bad checksum (stdnum docs example)
    "GB980780683",   # wrong last digit
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
