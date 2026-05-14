"""Tests for German (de) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# DE_IDNR: Steuerliche Identifikationsnummer
# ---------------------------------------------------------------------------


@pytest.fixture()
def idnr_scrubber() -> Scrubber:
    return Scrubber(detectors=["de_idnr"])


def _valid_idnrs() -> list[str]:
    from stdnum.de import idnr

    candidates = [
        "86095742719",
        "47036892816",
        "65929970489",
        "57549285017",
        "25768131411",
    ]
    return [c for c in candidates if idnr.is_valid(c)]


VALID_IDNRS = _valid_idnrs()


@pytest.mark.parametrize("v", VALID_IDNRS)
def test_idnr_valid(idnr_scrubber: Scrubber, v: str) -> None:
    matches = idnr_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_idnr_invalid(idnr_scrubber: Scrubber) -> None:
    bad = "86095742710"  # wrong check digit
    from stdnum.de import idnr

    if not idnr.is_valid(bad):
        matches = idnr_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_idnr_embedded(idnr_scrubber: Scrubber) -> None:
    if not VALID_IDNRS:
        pytest.skip("no valid IdNrs available")
    v = VALID_IDNRS[0]
    text = f"Steuer-IdNr: {v}."
    m = idnr_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: IdNr (11 digits, first non-zero) must not fire on 10 or 12 digits
def test_idnr_no_fire_on_10_digits(idnr_scrubber: Scrubber) -> None:
    assert idnr_scrubber.scan("8609574271") == []


def test_idnr_no_fire_on_12_digits(idnr_scrubber: Scrubber) -> None:
    assert idnr_scrubber.scan("860957427190") == []


# ---------------------------------------------------------------------------
# DE_VAT: Umsatzsteuer-Identifikationsnummer
# ---------------------------------------------------------------------------


@pytest.fixture()
def de_vat_scrubber() -> Scrubber:
    return Scrubber(detectors=["de_vat"])


def _valid_de_vats() -> list[str]:
    from stdnum.de import vat

    candidates = ["DE123456789", "DE811428818", "DE129274202", "DE303786076"]
    return [c for c in candidates if vat.is_valid(c)]


VALID_DE_VATS = _valid_de_vats()


@pytest.mark.parametrize("v", VALID_DE_VATS)
def test_de_vat_valid(de_vat_scrubber: Scrubber, v: str) -> None:
    matches = de_vat_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_de_vat_no_fire_on_fr_vat(de_vat_scrubber: Scrubber) -> None:
    assert de_vat_scrubber.scan("FR40303265045") == []


def test_de_vat_no_fire_on_nl_btw(de_vat_scrubber: Scrubber) -> None:
    assert de_vat_scrubber.scan("NL123456789B01") == []


# ---------------------------------------------------------------------------
# DE_SVNR: Sozialversicherungsnummer
# ---------------------------------------------------------------------------


@pytest.fixture()
def svnr_scrubber() -> Scrubber:
    return Scrubber(detectors=["de_svnr"])


def _compute_svnr_check(s11: str) -> int:
    """s11: 11-char prefix (area + birthdate + letter + serial)."""
    weights = (2, 1, 2, 5, 7, 1, 2, 1, 2, 1, 2, 1)
    letter_val = ord(s11[8].upper()) - ord("A") + 10
    expanded = s11[:8] + str(letter_val) + s11[9:11]
    assert len(expanded) == 12
    total = 0
    for d, w in zip(expanded, weights, strict=False):
        p = int(d) * w
        total += p // 10 + p % 10
    return total % 10


def _make_svnr(area: str, dob: str, letter: str, serial: str) -> str:
    prefix = area + dob + letter.upper() + serial
    assert len(prefix) == 11
    check = _compute_svnr_check(prefix)
    return prefix + str(check)


VALID_SVNRS = [
    _make_svnr("65", "070193", "J", "00"),
    _make_svnr("12", "010180", "A", "15"),
    _make_svnr("30", "151265", "M", "42"),
    _make_svnr("28", "230490", "S", "07"),
    _make_svnr("10", "050375", "Z", "99"),
]


@pytest.mark.parametrize("v", VALID_SVNRS)
def test_svnr_valid(svnr_scrubber: Scrubber, v: str) -> None:
    matches = svnr_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("v", VALID_SVNRS)
def test_svnr_invalid_wrong_check(svnr_scrubber: Scrubber, v: str) -> None:
    bad_check = str((int(v[-1]) + 1) % 10)
    bad = v[:-1] + bad_check
    matches = svnr_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_svnr_embedded(svnr_scrubber: Scrubber) -> None:
    v = VALID_SVNRS[0]
    text = f"Rentenversicherung: {v}."
    m = svnr_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: SVNR has embedded uppercase letter: DNI (8d+L) is shorter and no area code
def test_svnr_no_fire_on_dni(svnr_scrubber: Scrubber) -> None:
    assert svnr_scrubber.scan("12345678Z") == []


def test_svnr_no_fire_on_iban(svnr_scrubber: Scrubber) -> None:
    assert svnr_scrubber.scan("DE89370400440532013000") == []
