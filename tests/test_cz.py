"""Tests for Czech (cz) detectors.

Vectors sourced from:
  stdnum.cz.rc docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.cz.rc
  stdnum.cz.dic docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.cz.dic
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# CZ_RC
# ---------------------------------------------------------------------------

VALID_RCS = [
    "7103192745",  # from stdnum docs
    "1212121218",  # valid
    "710319/2745",  # with slash separator
]
INVALID_RCS = [
    "7103192740",  # wrong check (10 not divisible by 11)
    "9902300000",  # invalid date
]


@pytest.fixture()
def rc_s() -> Scrubber:
    return Scrubber(detectors=["cz_rc"])


@pytest.mark.parametrize("v", VALID_RCS)
def test_rc_valid(rc_s: Scrubber, v: str) -> None:
    matches = rc_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_RCS)
def test_rc_invalid(rc_s: Scrubber, bad: str) -> None:
    matches = rc_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_rc_embedded(rc_s: Scrubber) -> None:
    text = "RC: 7103192745 (rodné číslo)"
    m = rc_s.scan(text)
    assert len(m) == 1


def test_rc_stable_token() -> None:
    scrubber = Scrubber(detectors=["cz_rc"], stable_tokens=True)
    result = scrubber.clean("7103192745 and 7103192745")
    assert result.count("{{CZ_RC_1}}") == 2


# ---------------------------------------------------------------------------
# CZ_DIC
# ---------------------------------------------------------------------------

VALID_DICS = [
    "CZ25123891",  # from stdnum docs: legal entity
    "CZ7103192745",  # individual using RC
]
INVALID_DICS = [
    "CZ25123890",  # from stdnum docs: invalid check digit
]


@pytest.fixture()
def dic_s() -> Scrubber:
    return Scrubber(detectors=["cz_dic"])


@pytest.mark.parametrize("v", VALID_DICS)
def test_dic_valid(dic_s: Scrubber, v: str) -> None:
    matches = dic_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_DICS)
def test_dic_invalid(dic_s: Scrubber, bad: str) -> None:
    matches = dic_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_dic_embedded(dic_s: Scrubber) -> None:
    text = "DIČ: CZ25123891 (firma)"
    m = dic_s.scan(text)
    assert len(m) == 1


def test_dic_stable_token() -> None:
    scrubber = Scrubber(detectors=["cz_dic"], stable_tokens=True)
    result = scrubber.clean("CZ25123891 and CZ25123891")
    assert result.count("{{CZ_DIC_1}}") == 2
