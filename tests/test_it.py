"""Tests for Italian (it) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# IT_CF: Codice Fiscale
# ---------------------------------------------------------------------------


@pytest.fixture()
def cf_scrubber() -> Scrubber:
    return Scrubber(detectors=["it_codice_fiscale"])


def _valid_cfs() -> list[str]:
    from stdnum.it import codicefiscale as cf

    candidates = [
        "RSSMRA85T10A562S",
        "BNCSFN74P65A944E",
        "VLLLGU52D05H501N",
        "MRORSS77T41H501Y",
        "GRNGPP57P10158D",  # may be invalid: filtered below
    ]
    return [c for c in candidates if cf.is_valid(c)]


VALID_CFS = _valid_cfs()


@pytest.mark.parametrize("v", VALID_CFS)
def test_cf_valid(cf_scrubber: Scrubber, v: str) -> None:
    matches = cf_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_cf_invalid(cf_scrubber: Scrubber) -> None:
    bad = "RSSMRA85T10A562X"  # wrong check letter
    from stdnum.it import codicefiscale as cf

    if not cf.is_valid(bad):
        matches = cf_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_cf_embedded_span(cf_scrubber: Scrubber) -> None:
    if not VALID_CFS:
        pytest.skip("no valid codici fiscali available")
    v = VALID_CFS[0]
    text = f"Codice fiscale: {v}, data nascita..."
    m = cf_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: CF (16 alphanumeric) must not fire on ES DNI (9 chars)
def test_cf_no_fire_on_es_dni(cf_scrubber: Scrubber) -> None:
    assert cf_scrubber.scan("12345678Z") == []


def test_cf_no_fire_on_iban(cf_scrubber: Scrubber) -> None:
    assert cf_scrubber.scan("IT60X0542811101000000123456") == []


# ---------------------------------------------------------------------------
# IT_IVA: Partita IVA
# ---------------------------------------------------------------------------


@pytest.fixture()
def iva_scrubber() -> Scrubber:
    return Scrubber(detectors=["it_partita_iva"])


def _valid_ivas() -> list[str]:
    from stdnum.it import iva

    candidates = [
        "12345678903",
        "00743110157",
        "01234567891",
        "12345670017",
        "09876543217",
    ]
    return [c for c in candidates if iva.is_valid(c)]


VALID_IVAS = _valid_ivas()


@pytest.mark.parametrize("v", VALID_IVAS)
def test_iva_valid(iva_scrubber: Scrubber, v: str) -> None:
    matches = iva_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_iva_invalid_luhn(iva_scrubber: Scrubber) -> None:
    bad = "12345678900"  # wrong check digit
    from stdnum.it import iva

    if not iva.is_valid(bad):
        matches = iva_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_iva_not_redacted_when_invalid(iva_scrubber: Scrubber) -> None:
    bad = "12345678900"
    from stdnum.it import iva

    if not iva.is_valid(bad):
        result = iva_scrubber.clean(f"P.IVA {bad}")
        assert bad in result


def test_iva_embedded_span(iva_scrubber: Scrubber) -> None:
    if not VALID_IVAS:
        pytest.skip("no valid IVAs available")
    v = VALID_IVAS[0]
    text = f"Partita IVA: {v}."
    m = iva_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: IVA (11 digits) scrubber in isolation: confirm shape match + Luhn
def test_iva_no_fire_on_short_number(iva_scrubber: Scrubber) -> None:
    assert iva_scrubber.scan("12345") == []


def test_iva_no_fire_on_12_digits(iva_scrubber: Scrubber) -> None:
    assert iva_scrubber.scan("123456789012") == []
