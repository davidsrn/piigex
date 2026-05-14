"""Tests for Polish (pl) detectors.

Vectors sourced from:
  stdnum.pl.pesel docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pl.pesel
  stdnum.pl.nip docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pl.nip
  stdnum.pl.regon docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pl.regon
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# PL_PESEL
# ---------------------------------------------------------------------------

VALID_PESELS = [
    "44051401359",  # valid PESEL
    "92071314764",  # valid PESEL
]
INVALID_PESELS = [
    "44051401350",  # wrong check digit
    "99999999999",  # invalid date
]


@pytest.fixture()
def pesel_s() -> Scrubber:
    return Scrubber(detectors=["pl_pesel"])


@pytest.mark.parametrize("v", VALID_PESELS)
def test_pesel_valid(pesel_s: Scrubber, v: str) -> None:
    matches = pesel_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_PESELS)
def test_pesel_invalid(pesel_s: Scrubber, bad: str) -> None:
    matches = pesel_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_pesel_embedded(pesel_s: Scrubber) -> None:
    text = "PESEL: 44051401359 (Polska)"
    m = pesel_s.scan(text)
    assert len(m) == 1


def test_pesel_stable_token() -> None:
    scrubber = Scrubber(detectors=["pl_pesel"], stable_tokens=True)
    result = scrubber.clean("44051401359 and 44051401359")
    assert result.count("{{PL_PESEL_1}}") == 2


# ---------------------------------------------------------------------------
# PL_NIP
# ---------------------------------------------------------------------------

VALID_NIPS = [
    "5260001246",  # valid NIP
    "1234563224",  # valid NIP
]
INVALID_NIPS = [
    "1234567890",  # wrong check digit
    "5260001240",  # wrong check digit
]


@pytest.fixture()
def nip_s() -> Scrubber:
    return Scrubber(detectors=["pl_nip"])


@pytest.mark.parametrize("v", VALID_NIPS)
def test_nip_valid(nip_s: Scrubber, v: str) -> None:
    matches = nip_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_NIPS)
def test_nip_invalid(nip_s: Scrubber, bad: str) -> None:
    matches = nip_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_nip_embedded(nip_s: Scrubber) -> None:
    text = "NIP: 5260001246 (firma)"
    m = nip_s.scan(text)
    assert len(m) == 1


def test_nip_stable_token() -> None:
    scrubber = Scrubber(detectors=["pl_nip"], stable_tokens=True)
    result = scrubber.clean("5260001246 and 5260001246")
    assert result.count("{{PL_NIP_1}}") == 2


# ---------------------------------------------------------------------------
# PL_REGON
# ---------------------------------------------------------------------------

VALID_REGONS = [
    "192598184",  # from stdnum docs: 9-digit
    "123456785",  # from stdnum docs: 9-digit
]
INVALID_REGONS = [
    "192598183",  # from stdnum docs: wrong check
    "999999999",  # wrong check
]


@pytest.fixture()
def regon_s() -> Scrubber:
    return Scrubber(detectors=["pl_regon"])


@pytest.mark.parametrize("v", VALID_REGONS)
def test_regon_valid(regon_s: Scrubber, v: str) -> None:
    matches = regon_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_REGONS)
def test_regon_invalid(regon_s: Scrubber, bad: str) -> None:
    matches = regon_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_regon_embedded(regon_s: Scrubber) -> None:
    text = "REGON: 192598184 (rejestr)"
    m = regon_s.scan(text)
    assert len(m) == 1


def test_regon_stable_token() -> None:
    scrubber = Scrubber(detectors=["pl_regon"], stable_tokens=True)
    result = scrubber.clean("192598184 and 192598184")
    assert result.count("{{PL_REGON_1}}") == 2
