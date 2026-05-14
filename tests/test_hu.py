"""Tests for Hungarian (hu) detectors.

Vectors sourced from:
  stdnum.hu.anum docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.hu.anum
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# HU_ANUM
# ---------------------------------------------------------------------------

VALID_ANUMS = [
    "12892312",  # from stdnum docs: validate('HU-12892312')
    "10597190",  # valid
]
INVALID_ANUMS = [
    "12892313",  # from stdnum docs: invalid check digit
    "10597191",  # wrong check digit
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["hu_anum"])


@pytest.mark.parametrize("v", VALID_ANUMS)
def test_anum_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_ANUMS)
def test_anum_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_anum_embedded(s: Scrubber) -> None:
    text = "Adószám: 12892312 (Magyarország)"
    m = s.scan(text)
    assert len(m) == 1


def test_anum_not_inside_longer_number(s: Scrubber) -> None:
    assert s.scan("128923120") == []


def test_anum_cross_region(s: Scrubber) -> None:
    # DK CVR is also 8 digits: different registry, both can fire
    # Just verify HU detector does not fire on string with non-digit prefix
    assert s.scan("HU12892312") == []


def test_anum_stable_token() -> None:
    scrubber = Scrubber(detectors=["hu_anum"], stable_tokens=True)
    result = scrubber.clean("12892312 and 12892312")
    assert result.count("{{HU_ANUM_1}}") == 2


def test_anum_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["hu_anum"], stable_tokens=True)
    result = scrubber.clean("12892312 and 10597190")
    assert "{{HU_ANUM_1}}" in result
    assert "{{HU_ANUM_2}}" in result
