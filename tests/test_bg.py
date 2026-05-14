"""Tests for Bulgarian (bg) detectors.

Vectors sourced from:
  stdnum.bg.egn docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.bg.egn
  stdnum.bg.pnf docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.bg.pnf
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# BG_EGN
# ---------------------------------------------------------------------------

VALID_EGNS = [
    "7523169263",  # from stdnum docs
    "8032056031",  # from stdnum docs
    "7542011030",  # from stdnum docs (get_birth_date example)
]
INVALID_EGNS = [
    "8019010008",  # invalid date: from stdnum docs
    "7523169260",  # wrong check digit
]


@pytest.fixture()
def egn_s() -> Scrubber:
    return Scrubber(detectors=["bg_egn"])


@pytest.mark.parametrize("v", VALID_EGNS)
def test_egn_valid(egn_s: Scrubber, v: str) -> None:
    matches = egn_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_EGNS)
def test_egn_invalid(egn_s: Scrubber, bad: str) -> None:
    matches = egn_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_egn_embedded(egn_s: Scrubber) -> None:
    text = "EGN: 7523169263 (personal)"
    m = egn_s.scan(text)
    assert len(m) == 1


def test_egn_not_inside_longer_number(egn_s: Scrubber) -> None:
    assert egn_s.scan("75231692630") == []


def test_egn_cross_region(egn_s: Scrubber) -> None:
    # IBAN is longer; EGN is exactly 10 digits
    assert egn_s.scan("ATU57194903") == []


def test_egn_stable_token() -> None:
    scrubber = Scrubber(detectors=["bg_egn"], stable_tokens=True)
    result = scrubber.clean("7523169263 and 7523169263")
    assert result.count("{{BG_EGN_1}}") == 2


# ---------------------------------------------------------------------------
# BG_PNF
# ---------------------------------------------------------------------------

VALID_PNFS = [
    "7111042925",  # from stdnum docs
]
INVALID_PNFS = [
    "7111042922",  # from stdnum docs: invalid check digit
    "1234567890",  # wrong checksum
]


@pytest.fixture()
def pnf_s() -> Scrubber:
    return Scrubber(detectors=["bg_pnf"])


@pytest.mark.parametrize("v", VALID_PNFS)
def test_pnf_valid(pnf_s: Scrubber, v: str) -> None:
    matches = pnf_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_PNFS)
def test_pnf_invalid(pnf_s: Scrubber, bad: str) -> None:
    matches = pnf_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_pnf_embedded(pnf_s: Scrubber) -> None:
    text = "PNF: 7111042925 (foreigner)"
    m = pnf_s.scan(text)
    assert len(m) == 1


def test_pnf_stable_token() -> None:
    scrubber = Scrubber(detectors=["bg_pnf"], stable_tokens=True)
    result = scrubber.clean("7111042925 and 7111042925")
    assert result.count("{{BG_PNF_1}}") == 2
