"""Tests for Finnish (fi) detectors.

Vectors sourced from:
  stdnum.fi.hetu docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fi.hetu
  stdnum.fi.ytunnus docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fi.ytunnus
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# FI_HETU
# ---------------------------------------------------------------------------

VALID_HETUS = [
    "131052-308T",  # from stdnum docs
    "311280-888Y",  # valid
]
INVALID_HETUS = [
    "131052-308U",  # from stdnum docs: wrong check digit
    "310252-308Y",  # from stdnum docs: invalid date
]


@pytest.fixture()
def hetu_s() -> Scrubber:
    return Scrubber(detectors=["fi_hetu"])


@pytest.mark.parametrize("v", VALID_HETUS)
def test_hetu_valid(hetu_s: Scrubber, v: str) -> None:
    matches = hetu_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_HETUS)
def test_hetu_invalid(hetu_s: Scrubber, bad: str) -> None:
    matches = hetu_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_hetu_embedded(hetu_s: Scrubber) -> None:
    text = "Henkilötunnus: 131052-308T (Suomi)"
    m = hetu_s.scan(text)
    assert len(m) == 1


def test_hetu_cross_region(hetu_s: Scrubber) -> None:
    # BIC should not match hetu
    assert hetu_s.scan("BNPAFRPP") == []


def test_hetu_stable_token() -> None:
    scrubber = Scrubber(detectors=["fi_hetu"], stable_tokens=True)
    result = scrubber.clean("131052-308T and 131052-308T")
    assert result.count("{{FI_HETU_1}}") == 2


# ---------------------------------------------------------------------------
# FI_YTUNNUS
# ---------------------------------------------------------------------------

VALID_YTUNNUSES = [
    "2077474-0",  # valid
    "1000000-4",  # valid
    "1000001-2",  # valid
]
INVALID_YTUNNUSES = [
    "1234567-9",  # wrong check digit
    "2077474-1",  # wrong check digit
]


@pytest.fixture()
def ytunnus_s() -> Scrubber:
    return Scrubber(detectors=["fi_ytunnus"])


@pytest.mark.parametrize("v", VALID_YTUNNUSES)
def test_ytunnus_valid(ytunnus_s: Scrubber, v: str) -> None:
    matches = ytunnus_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_YTUNNUSES)
def test_ytunnus_invalid(ytunnus_s: Scrubber, bad: str) -> None:
    matches = ytunnus_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_ytunnus_embedded(ytunnus_s: Scrubber) -> None:
    text = "Y-tunnus: 2077474-0 (yritys)"
    m = ytunnus_s.scan(text)
    assert len(m) == 1


def test_ytunnus_stable_token() -> None:
    scrubber = Scrubber(detectors=["fi_ytunnus"], stable_tokens=True)
    result = scrubber.clean("2077474-0 and 2077474-0")
    assert result.count("{{FI_YTUNNUS_1}}") == 2
