"""Tests for Lithuanian (lt) detectors.

Vectors sourced from:
  stdnum.lt.asmens docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.lt.asmens
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# LT_ASMENS
# ---------------------------------------------------------------------------

VALID_ASMENS = [
    "33309240064",  # from stdnum docs
    "38703181745",  # valid
]
INVALID_ASMENS = [
    "33309240164",  # from stdnum docs: wrong check digit
    "00000000000",  # invalid first digit
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["lt_asmens"])


@pytest.mark.parametrize("v", VALID_ASMENS)
def test_asmens_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_ASMENS)
def test_asmens_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_asmens_embedded(s: Scrubber) -> None:
    text = "Asmens kodas: 33309240064 (Lietuva)"
    m = s.scan(text)
    assert len(m) == 1


def test_asmens_not_inside_longer_number(s: Scrubber) -> None:
    assert s.scan("333092400640") == []


def test_asmens_stable_token() -> None:
    scrubber = Scrubber(detectors=["lt_asmens"], stable_tokens=True)
    result = scrubber.clean("33309240064 and 33309240064")
    assert result.count("{{LT_ASMENS_1}}") == 2


def test_asmens_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["lt_asmens"], stable_tokens=True)
    result = scrubber.clean("33309240064 and 38703181745")
    assert "{{LT_ASMENS_1}}" in result
    assert "{{LT_ASMENS_2}}" in result
