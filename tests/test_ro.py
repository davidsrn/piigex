"""Tests for Romanian (ro) detectors.

Vectors sourced from:
  stdnum.ro.cnp docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ro.cnp
  stdnum.ro.cf docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ro.cf
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# RO_CNP
# ---------------------------------------------------------------------------

VALID_CNPS = [
    "1630615123457",  # from stdnum docs
    "1800101221144",  # from stdnum docs
]
INVALID_CNPS = [
    "1630615123458",  # from stdnum docs: wrong check digit
    "0000000000000",  # invalid first digit (0)
]


@pytest.fixture()
def cnp_s() -> Scrubber:
    return Scrubber(detectors=["ro_cnp"])


@pytest.mark.parametrize("v", VALID_CNPS)
def test_cnp_valid(cnp_s: Scrubber, v: str) -> None:
    matches = cnp_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_CNPS)
def test_cnp_invalid(cnp_s: Scrubber, bad: str) -> None:
    matches = cnp_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_cnp_embedded(cnp_s: Scrubber) -> None:
    text = "CNP: 1630615123457 (România)"
    m = cnp_s.scan(text)
    assert len(m) == 1


def test_cnp_not_inside_longer_number(cnp_s: Scrubber) -> None:
    assert cnp_s.scan("16306151234570") == []


def test_cnp_stable_token() -> None:
    scrubber = Scrubber(detectors=["ro_cnp"], stable_tokens=True)
    result = scrubber.clean("1630615123457 and 1630615123457")
    assert result.count("{{RO_CNP_1}}") == 2


# ---------------------------------------------------------------------------
# RO_CF
# ---------------------------------------------------------------------------

VALID_CFS = [
    "RO18547290",  # from stdnum docs
    "RO185472890",  # longer variant
]
INVALID_CFS = [
    "RO18547291",  # wrong check digit
    "RO00000000",  # starts with zeros: no valid CUI
]


@pytest.fixture()
def cf_s() -> Scrubber:
    return Scrubber(detectors=["ro_cf"])


@pytest.mark.parametrize("v", VALID_CFS)
def test_cf_valid(cf_s: Scrubber, v: str) -> None:
    matches = cf_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_CFS)
def test_cf_invalid(cf_s: Scrubber, bad: str) -> None:
    matches = cf_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_cf_embedded(cf_s: Scrubber) -> None:
    text = "CIF: RO18547290 (firma)"
    m = cf_s.scan(text)
    assert len(m) == 1
    assert m[0].value == "RO18547290"


def test_cf_stable_token() -> None:
    scrubber = Scrubber(detectors=["ro_cf"], stable_tokens=True)
    result = scrubber.clean("RO18547290 and RO18547290")
    assert result.count("{{RO_CF_1}}") == 2
