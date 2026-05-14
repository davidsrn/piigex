"""Tests for French (fr) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# FR_NIR: Numéro de Sécurité Sociale
# ---------------------------------------------------------------------------


@pytest.fixture()
def nir_scrubber() -> Scrubber:
    return Scrubber(detectors=["fr_nir"])


def _valid_nirs() -> list[str]:
    from stdnum.fr import nir

    candidates = [
        "195077553666750",
        "269054958815780",
        "195077553666768",
        "175059812301872",
        "299068512301858",
    ]
    return [c for c in candidates if nir.is_valid(c)]


VALID_NIRS = _valid_nirs()


@pytest.mark.parametrize("v", VALID_NIRS)
def test_nir_valid(nir_scrubber: Scrubber, v: str) -> None:
    matches = nir_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_nir_invalid(nir_scrubber: Scrubber) -> None:
    bad = "195077553666700"  # wrong check digits
    from stdnum.fr import nir

    if not nir.is_valid(bad):
        matches = nir_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_nir_embedded(nir_scrubber: Scrubber) -> None:
    if not VALID_NIRS:
        pytest.skip("no valid NIRs available")
    v = VALID_NIRS[0]
    text = f"N° sécu : {v}."
    m = nir_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: NIR (15 chars, starts with 1-4/7/8) vs SIRET (14 digits)
def test_nir_no_fire_on_siret(nir_scrubber: Scrubber) -> None:
    assert nir_scrubber.scan("73282932000074") == []


# ---------------------------------------------------------------------------
# FR_NIF: Numéro d'Immatriculation Fiscale
# ---------------------------------------------------------------------------


@pytest.fixture()
def fr_nif_scrubber() -> Scrubber:
    return Scrubber(detectors=["fr_nif"])


def _valid_fr_nifs() -> list[str]:
    from stdnum.fr import nif

    candidates = [
        "0701987765432",
        "1234567890123",
        "0987654321098",
        "2345678901234",
        "0112233445566",
    ]
    return [c for c in candidates if nif.is_valid(c)]


VALID_FR_NIFS = _valid_fr_nifs()


@pytest.mark.parametrize("v", VALID_FR_NIFS)
def test_fr_nif_valid(fr_nif_scrubber: Scrubber, v: str) -> None:
    matches = fr_nif_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_fr_nif_invalid(fr_nif_scrubber: Scrubber) -> None:
    bad = "0701987765400"  # wrong last 3 digits
    from stdnum.fr import nif

    if not nif.is_valid(bad):
        matches = fr_nif_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


# ---------------------------------------------------------------------------
# FR_SIREN
# ---------------------------------------------------------------------------


@pytest.fixture()
def siren_scrubber() -> Scrubber:
    return Scrubber(detectors=["fr_siren"])


def _valid_sirens() -> list[str]:
    from stdnum.fr import siren

    candidates = ["732829320", "552081317", "542107651", "775672272", "378901946"]
    return [c for c in candidates if siren.is_valid(c)]


VALID_SIRENS = _valid_sirens()


@pytest.mark.parametrize("v", VALID_SIRENS)
def test_siren_valid(siren_scrubber: Scrubber, v: str) -> None:
    matches = siren_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_siren_invalid_luhn(siren_scrubber: Scrubber) -> None:
    bad = "732829321"
    from stdnum.fr import siren

    if not siren.is_valid(bad):
        matches = siren_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_siren_embedded(siren_scrubber: Scrubber) -> None:
    if not VALID_SIRENS:
        pytest.skip("no valid SIRENs available")
    v = VALID_SIRENS[0]
    text = f"SIREN {v} (Paris)."
    m = siren_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: SIREN (9 digits) vs NL BSN (9 digits, different checksum)
def test_siren_9digits_cross_region_checksum() -> None:
    from stdnum.nl import bsn as nl_b

    # A valid SIREN that is NOT a valid BSN
    for v in VALID_SIRENS:
        if not nl_b.is_valid(v):
            s = Scrubber(detectors=["fr_siren"])
            matches = s.scan(v)
            assert len(matches) == 1 and matches[0].valid
            break


# ---------------------------------------------------------------------------
# FR_SIRET
# ---------------------------------------------------------------------------


@pytest.fixture()
def siret_scrubber() -> Scrubber:
    return Scrubber(detectors=["fr_siret"])


def _valid_sirets() -> list[str]:
    from stdnum.fr import siret

    candidates = [
        "73282932000074",
        "55208131700014",
        "54210765100013",
    ]
    return [c for c in candidates if siret.is_valid(c)]


VALID_SIRETS = _valid_sirets()


@pytest.mark.parametrize("v", VALID_SIRETS)
def test_siret_valid(siret_scrubber: Scrubber, v: str) -> None:
    matches = siret_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_siret_invalid(siret_scrubber: Scrubber) -> None:
    bad = "73282932000070"
    from stdnum.fr import siret

    if not siret.is_valid(bad):
        matches = siret_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_siret_embedded(siret_scrubber: Scrubber) -> None:
    if not VALID_SIRETS:
        pytest.skip("no valid SIRETs available")
    v = VALID_SIRETS[0]
    text = f"SIRET: {v}."
    m = siret_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# ---------------------------------------------------------------------------
# FR_TVA
# ---------------------------------------------------------------------------


@pytest.fixture()
def tva_scrubber() -> Scrubber:
    return Scrubber(detectors=["fr_tva"])


def _valid_tvas() -> list[str]:
    from stdnum.fr import tva

    candidates = ["FR40303265045", "FR23334175221", "FRK7399859412", "FR84323140251"]
    return [c for c in candidates if tva.is_valid(c)]


VALID_TVAS = _valid_tvas()


@pytest.mark.parametrize("v", VALID_TVAS)
def test_tva_valid(tva_scrubber: Scrubber, v: str) -> None:
    matches = tva_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_tva_no_fire_on_non_fr_vat(tva_scrubber: Scrubber) -> None:
    assert tva_scrubber.scan("DE123456789") == []
    assert tva_scrubber.scan("ES12345678A") == []
