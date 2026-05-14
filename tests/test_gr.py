"""Tests for Greek (gr) detectors.

Vectors sourced from:
  stdnum.gr.amka docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.gr.amka
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# GR_AMKA
# ---------------------------------------------------------------------------

VALID_AMKAS = [
    "01013099997",  # from stdnum docs
]
INVALID_AMKAS = [
    "01013099999",  # from stdnum docs: wrong check digit
    "00000000000",  # all zeros
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["gr_amka"])


@pytest.mark.parametrize("v", VALID_AMKAS)
def test_amka_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_AMKAS)
def test_amka_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_amka_embedded(s: Scrubber) -> None:
    text = "AMKA: 01013099997 (Ελλάδα)"
    m = s.scan(text)
    assert len(m) == 1


def test_amka_not_inside_longer_number(s: Scrubber) -> None:
    assert s.scan("010130999970") == []


def test_amka_stable_token() -> None:
    scrubber = Scrubber(detectors=["gr_amka"], stable_tokens=True)
    result = scrubber.clean("01013099997 and 01013099997")
    assert result.count("{{GR_AMKA_1}}") == 2
