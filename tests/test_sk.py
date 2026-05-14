"""Tests for Slovak (sk) detectors.

Vectors sourced from:
  stdnum.sk.rc docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.sk.rc
  (identical structure to Czech RC)
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# SK_RC
# ---------------------------------------------------------------------------

VALID_RCS = [
    "7103192745",  # valid (shared algorithm with CZ RC)
    "1212121218",  # valid
]
INVALID_RCS = [
    "7103192740",  # wrong check digit
    "9902300000",  # invalid date
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["sk_rc"])


@pytest.mark.parametrize("v", VALID_RCS)
def test_rc_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_RCS)
def test_rc_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_rc_embedded(s: Scrubber) -> None:
    text = "Rodné číslo: 7103192745 (Slovensko)"
    m = s.scan(text)
    assert len(m) == 1


def test_rc_stable_token() -> None:
    scrubber = Scrubber(detectors=["sk_rc"], stable_tokens=True)
    result = scrubber.clean("7103192745 and 7103192745")
    assert result.count("{{SK_RC_1}}") == 2


def test_rc_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["sk_rc"], stable_tokens=True)
    result = scrubber.clean("7103192745 and 1212121218")
    assert "{{SK_RC_1}}" in result
    assert "{{SK_RC_2}}" in result
