"""Tests for Austrian (at) detectors.

Vectors sourced from:
  stdnum.at.vnr docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.at.vnr
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# AT_VNR
# ---------------------------------------------------------------------------

# Format: 10 digits: 3-digit serial + 1 check digit + 6-digit birthdate (DDMMYY)
VALID_VNRS = [
    "1237010180",  # from stdnum docs: validate('1237 010180')
    "1237 010180",  # with space separator
]
INVALID_VNRS = [
    "2237010180",  # from stdnum docs: wrong check digit
    "9999010180",  # wrong check digit
    "0000000000",  # starts with 0: invalid
]


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["at_vnr"])


@pytest.mark.parametrize("v", VALID_VNRS)
def test_vnr_valid(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_VNRS)
def test_vnr_invalid(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_vnr_embedded(s: Scrubber) -> None:
    text = "SVNr: 1237010180 (geboren 01.01.80)"
    m = s.scan(text)
    assert len(m) == 1
    assert m[0].value == "1237010180"


def test_vnr_not_inside_longer_number(s: Scrubber) -> None:
    # 11-digit number should not match (boundary check)
    assert s.scan("12370101800") == []


def test_vnr_cross_region(s: Scrubber) -> None:
    # IBAN-like string should not match AT_VNR
    assert s.scan("ATU57194903") == []


def test_vnr_stable_token() -> None:
    scrubber = Scrubber(detectors=["at_vnr"], stable_tokens=True)
    result = scrubber.clean("1237010180 and 1237010180")
    assert result.count("{{AT_VNR_1}}") == 2


def test_vnr_two_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["at_vnr"], stable_tokens=True)
    result = scrubber.clean("1237010180 and 1237010181")
    assert "{{AT_VNR_1}}" in result
