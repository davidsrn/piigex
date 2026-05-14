"""Tests for Swedish (se) detectors.

Vectors sourced from:
  stdnum.se.personnummer docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.se.personnummer
  stdnum.se.orgnr docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.se.orgnr
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# SE_PERSONNUMMER
# ---------------------------------------------------------------------------

VALID_PERSONNUMMERS = [
    "880320-0016",  # from stdnum docs
    "640823-3234",  # valid
    "811228-9841",  # from stdnum docs (get_birth_date example)
]
INVALID_PERSONNUMMERS = [
    "880320-0018",  # from stdnum docs: wrong check digit
    "991332-0000",  # invalid date
]


@pytest.fixture()
def pnr_s() -> Scrubber:
    return Scrubber(detectors=["se_personnummer"])


@pytest.mark.parametrize("v", VALID_PERSONNUMMERS)
def test_personnummer_valid(pnr_s: Scrubber, v: str) -> None:
    matches = pnr_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_PERSONNUMMERS)
def test_personnummer_invalid(pnr_s: Scrubber, bad: str) -> None:
    matches = pnr_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_personnummer_embedded(pnr_s: Scrubber) -> None:
    text = "Personnummer: 880320-0016 (Sverige)"
    m = pnr_s.scan(text)
    assert len(m) == 1
    assert m[0].value == "880320-0016"


def test_personnummer_cross_region(pnr_s: Scrubber) -> None:
    # Finnish ytunnus (7-hyphen-1) should not fire on SE personnummer
    # (different digit counts)
    se_s = Scrubber(detectors=["se_personnummer", "fi_ytunnus"])
    matches = [m for m in se_s.scan("2077474-0") if m.name == "se_personnummer"]
    assert matches == []


def test_personnummer_stable_token() -> None:
    scrubber = Scrubber(detectors=["se_personnummer"], stable_tokens=True)
    result = scrubber.clean("880320-0016 and 880320-0016")
    assert result.count("{{SE_PERSONNUMMER_1}}") == 2


def test_personnummer_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["se_personnummer"], stable_tokens=True)
    result = scrubber.clean("880320-0016 and 640823-3234")
    assert "{{SE_PERSONNUMMER_1}}" in result
    assert "{{SE_PERSONNUMMER_2}}" in result


# ---------------------------------------------------------------------------
# SE_ORGNR
# ---------------------------------------------------------------------------

VALID_ORGNRS = [
    "1234567897",  # from stdnum docs
    "5560360793",  # valid (Luhn)
]
INVALID_ORGNRS = [
    "1234567891",  # from stdnum docs: wrong check digit
    "9999999990",  # wrong check digit
]


@pytest.fixture()
def org_s() -> Scrubber:
    return Scrubber(detectors=["se_orgnr"])


@pytest.mark.parametrize("v", VALID_ORGNRS)
def test_orgnr_valid(org_s: Scrubber, v: str) -> None:
    # Note: se_orgnr requires hyphen separator in regex pattern
    formatted = v[:6] + "-" + v[6:]
    matches = org_s.scan(formatted)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_ORGNRS)
def test_orgnr_invalid(org_s: Scrubber, bad: str) -> None:
    formatted = bad[:6] + "-" + bad[6:]
    matches = org_s.scan(formatted)
    if matches:
        assert not matches[0].valid


def test_orgnr_embedded(org_s: Scrubber) -> None:
    text = "Organisationsnummer: 123456-7897 (Sverige)"
    m = org_s.scan(text)
    assert len(m) == 1


def test_orgnr_stable_token() -> None:
    scrubber = Scrubber(detectors=["se_orgnr"], stable_tokens=True)
    result = scrubber.clean("123456-7897 and 123456-7897")
    assert result.count("{{SE_ORGNR_1}}") == 2
