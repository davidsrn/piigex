"""Tests for Danish (dk) detectors.

Vectors sourced from:
  stdnum.dk.cpr docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.dk.cpr
  stdnum.dk.cvr docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.dk.cvr
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# DK_CPR
# ---------------------------------------------------------------------------

VALID_CPRS = [
    "2110625629",  # valid CPR
    "211062-5629",  # with hyphen separator
    "0101901234",  # valid format
]
INVALID_CPRS = [
    "3213000000",  # invalid date (32nd day)
    "9999990000",  # invalid date
]


@pytest.fixture()
def cpr_s() -> Scrubber:
    return Scrubber(detectors=["dk_cpr"])


@pytest.mark.parametrize("v", VALID_CPRS)
def test_cpr_valid(cpr_s: Scrubber, v: str) -> None:
    matches = cpr_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_CPRS)
def test_cpr_invalid(cpr_s: Scrubber, bad: str) -> None:
    matches = cpr_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_cpr_embedded(cpr_s: Scrubber) -> None:
    text = "CPR-nummer: 211062-5629 (Danmark)"
    m = cpr_s.scan(text)
    assert len(m) == 1


def test_cpr_stable_token() -> None:
    scrubber = Scrubber(detectors=["dk_cpr"], stable_tokens=True)
    result = scrubber.clean("2110625629 and 2110625629")
    assert result.count("{{DK_CPR_1}}") == 2


# ---------------------------------------------------------------------------
# DK_CVR
# ---------------------------------------------------------------------------

VALID_CVRS = [
    "13585628",  # valid CVR number
]
INVALID_CVRS = [
    "13585620",  # wrong check digit
    "00000000",  # all zeros
]


@pytest.fixture()
def cvr_s() -> Scrubber:
    return Scrubber(detectors=["dk_cvr"])


@pytest.mark.parametrize("v", VALID_CVRS)
def test_cvr_valid(cvr_s: Scrubber, v: str) -> None:
    matches = cvr_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_CVRS)
def test_cvr_invalid(cvr_s: Scrubber, bad: str) -> None:
    matches = cvr_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_cvr_embedded(cvr_s: Scrubber) -> None:
    text = "CVR: 13585628 (virksomhed)"
    m = cvr_s.scan(text)
    assert len(m) == 1


def test_cvr_stable_token() -> None:
    scrubber = Scrubber(detectors=["dk_cvr"], stable_tokens=True)
    result = scrubber.clean("13585628 and 13585628")
    assert result.count("{{DK_CVR_1}}") == 2
