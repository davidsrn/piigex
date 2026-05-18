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
