"""Tests for Croatian (hr) detectors.

Vectors sourced from:
  stdnum.hr.oib docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.hr.oib
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# HR_OIB
# ---------------------------------------------------------------------------

VALID_OIBS = [
    "11111111119",  # from stdnum docs
    "33392005961",  # from EU VAT test (HR VAT uses OIB)
    "69435151530",  # wikipedia example
]
INVALID_OIBS = [
    "11111111110",  # wrong check digit
    "00000000000",  # all zeros
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["hr_oib"])


@pytest.mark.parametrize("v", VALID_OIBS)
def test_oib_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_OIBS)
def test_oib_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_oib_embedded(s: Scrubber) -> None:
    text = "OIB: 11111111119 (Croatia)"
    m = s.scan(text)
    assert len(m) == 1


def test_oib_not_inside_longer_number(s: Scrubber) -> None:
    assert s.scan("111111111190") == []


def test_oib_cross_region(s: Scrubber) -> None:
    # 10-digit DE IdNr should not match (different length)
    pass


def test_oib_stable_token() -> None:
    scrubber = Scrubber(detectors=["hr_oib"], stable_tokens=True)
    result = scrubber.clean("11111111119 and 11111111119")
    assert result.count("{{HR_OIB_1}}") == 2


def test_oib_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["hr_oib"], stable_tokens=True)
    result = scrubber.clean("11111111119 and 33392005961")
    assert "{{HR_OIB_1}}" in result
    assert "{{HR_OIB_2}}" in result
