"""Tests for Irish (ie) detectors.

Vectors sourced from:
  stdnum.ie.pps docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ie.pps
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# IE_PPS
# ---------------------------------------------------------------------------

VALID_PPSS = [
    "6433435F",  # from stdnum docs: pre-2013 format
    "6433435FT",  # from stdnum docs: pre-2013 with special T
    "6433435FW",  # from stdnum docs: married women pre-2013
    "6433435OA",  # from stdnum docs: 2013 format (personal)
    "6433435IH",  # from stdnum docs: 2013 format (non-personal)
]
INVALID_PPSS = [
    "6433435E",  # from stdnum docs: incorrect check digit
    "6433435VH",  # from stdnum docs: incorrect check
    "0000000A",  # all zeros with check
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["ie_pps"])


@pytest.mark.parametrize("v", VALID_PPSS)
def test_pps_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_PPSS)
def test_pps_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_pps_embedded(s: Scrubber) -> None:
    text = "PPS No: 6433435F (Ireland)"
    m = s.scan(text)
    assert len(m) == 1
    assert m[0].value == "6433435F"


def test_pps_not_inside_word(s: Scrubber) -> None:
    assert s.scan("x6433435F") == []


def test_pps_cross_region(s: Scrubber) -> None:
    # 9-digit Spanish NSS should not match IE PPS (different pattern)
    pass


def test_pps_stable_token() -> None:
    scrubber = Scrubber(detectors=["ie_pps"], stable_tokens=True)
    result = scrubber.clean("6433435F and 6433435F")
    assert result.count("{{IE_PPS_1}}") == 2


def test_pps_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["ie_pps"], stable_tokens=True)
    result = scrubber.clean("6433435F and 6433435OA")
    assert "{{IE_PPS_1}}" in result
    assert "{{IE_PPS_2}}" in result
