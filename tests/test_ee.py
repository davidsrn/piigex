"""Tests for Estonian (ee) detectors.

Vectors sourced from:
  stdnum.ee.ik docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ee.ik
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# EE_IK
# ---------------------------------------------------------------------------

VALID_IKS = [
    "36805280109",  # from stdnum docs
    "37605030299",  # valid
]
INVALID_IKS = [
    "36805280108",  # from stdnum docs: wrong check digit
    "00000000000",  # invalid first digit (must be 1-6)
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["ee_ik"])


@pytest.mark.parametrize("v", VALID_IKS)
def test_ik_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_IKS)
def test_ik_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_ik_embedded(s: Scrubber) -> None:
    text = "Isikukood: 36805280109 (Eesti)"
    m = s.scan(text)
    assert len(m) == 1


def test_ik_not_inside_longer_number(s: Scrubber) -> None:
    assert s.scan("368052801090") == []


def test_ik_cross_region(s: Scrubber) -> None:
    # EE IK starts with 1-6; a 7-prefix sequence should not match
    assert s.scan("70000000000") == []


def test_ik_stable_token() -> None:
    scrubber = Scrubber(detectors=["ee_ik"], stable_tokens=True)
    result = scrubber.clean("36805280109 and 36805280109")
    assert result.count("{{EE_IK_1}}") == 2


def test_ik_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["ee_ik"], stable_tokens=True)
    result = scrubber.clean("36805280109 and 37605030299")
    assert "{{EE_IK_1}}" in result
    assert "{{EE_IK_2}}" in result
