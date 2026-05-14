"""Tests for Slovenian (si) detectors.

Vectors sourced from:
  stdnum.si.emso docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.si.emso
  stdnum.si.maticna docstring: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.si.maticna
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# SI_EMSO
# ---------------------------------------------------------------------------

VALID_EMSOS = [
    "0101006500006",  # from stdnum docs
]
INVALID_EMSOS = [
    "0101006500007",  # from stdnum docs: wrong check digit
    "0000000000000",  # all zeros
]


@pytest.fixture()
def emso_s() -> Scrubber:
    return Scrubber(detectors=["si_emso"])


@pytest.mark.parametrize("v", VALID_EMSOS)
def test_emso_valid(emso_s: Scrubber, v: str) -> None:
    matches = emso_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_EMSOS)
def test_emso_invalid(emso_s: Scrubber, bad: str) -> None:
    matches = emso_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_emso_embedded(emso_s: Scrubber) -> None:
    text = "EMŠO: 0101006500006 (Slovenija)"
    m = emso_s.scan(text)
    assert len(m) == 1


def test_emso_stable_token() -> None:
    scrubber = Scrubber(detectors=["si_emso"], stable_tokens=True)
    result = scrubber.clean("0101006500006 and 0101006500006")
    assert result.count("{{SI_EMSO_1}}") == 2


# ---------------------------------------------------------------------------
# SI_MATICNA
# ---------------------------------------------------------------------------

VALID_MATICNAS = [
    "9331310",  # from stdnum docs
    "9331310000",  # from stdnum docs: with unit suffix
]
INVALID_MATICNAS = [
    "9331320",  # from stdnum docs: wrong check digit
    "9331320000",  # wrong check digit
]


@pytest.fixture()
def mat_s() -> Scrubber:
    return Scrubber(detectors=["si_maticna"])


@pytest.mark.parametrize("v", VALID_MATICNAS)
def test_maticna_valid(mat_s: Scrubber, v: str) -> None:
    matches = mat_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_MATICNAS)
def test_maticna_invalid(mat_s: Scrubber, bad: str) -> None:
    matches = mat_s.scan(bad)
    if matches:
        assert not matches[0].valid


def test_maticna_embedded(mat_s: Scrubber) -> None:
    text = "Mat. st.: 9331310 (podjetje)"
    m = mat_s.scan(text)
    assert len(m) == 1


def test_maticna_stable_token() -> None:
    scrubber = Scrubber(detectors=["si_maticna"], stable_tokens=True)
    result = scrubber.clean("9331310 and 9331310")
    assert result.count("{{SI_MATICNA_1}}") == 2
