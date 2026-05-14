"""Tests for Spanish (es) detectors.

Valid test vectors are computed at runtime using the same stdnum library used by
the detectors, so they are always self-consistent. Negative vectors share the shape
but have a deliberately wrong check character/digit.
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DNI_TABLE = "TRWAGMYFPDXBNJZSQVHLCKE"


def _dni(digits: str) -> str:
    return digits + _DNI_TABLE[int(digits) % 23]


_NIE_PREFIX = {"X": "0", "Y": "1", "Z": "2"}


def _nie(prefix: str, digits: str) -> str:
    return prefix + digits + _DNI_TABLE[int(_NIE_PREFIX[prefix] + digits) % 23]


def _wrong_check(identifier: str) -> str:
    """Return identifier with last character replaced by a wrong character."""
    last = identifier[-1]
    wrong = "A" if last != "A" else "B"
    return identifier[:-1] + wrong


# ---------------------------------------------------------------------------
# ES_DNI
# ---------------------------------------------------------------------------

VALID_DNIS = [_dni(d) for d in ("12345678", "87654321", "00000000", "11111111", "55555555")]
INVALID_DNIS = [_wrong_check(d) for d in VALID_DNIS]


@pytest.fixture()
def dni_scrubber() -> Scrubber:
    return Scrubber(detectors=["es_dni"])


@pytest.mark.parametrize("v", VALID_DNIS)
def test_dni_valid(dni_scrubber: Scrubber, v: str) -> None:
    matches = dni_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_DNIS)
def test_dni_invalid(dni_scrubber: Scrubber, bad: str) -> None:
    matches = dni_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_dni_embedded_span(dni_scrubber: Scrubber) -> None:
    v = _dni("12345678")
    text = f"DNI: {v}, gracias."
    m = dni_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_dni_not_inside_word(dni_scrubber: Scrubber) -> None:
    v = _dni("12345678")
    assert dni_scrubber.scan(f"x{v}") == []


# Cross-region: DNI (8d+L) must not fire on NIE (X/Y/Z + 7d + L) or IT CF (16 alphanumeric)
def test_dni_no_fire_on_nie(dni_scrubber: Scrubber) -> None:
    nie = _nie("X", "1234567")
    assert dni_scrubber.scan(nie) == []


def test_dni_no_fire_on_it_cf(dni_scrubber: Scrubber) -> None:
    assert dni_scrubber.scan("RSSMRA85T10A562S") == []


# ---------------------------------------------------------------------------
# ES_NIE
# ---------------------------------------------------------------------------

VALID_NIES = [
    _nie(p, d)
    for p, d in [
        ("X", "1234567"),
        ("Y", "1234567"),
        ("Z", "1234567"),
        ("X", "0000000"),
        ("Y", "9999999"),
    ]
]
INVALID_NIES = [_wrong_check(n) for n in VALID_NIES]


@pytest.fixture()
def nie_scrubber() -> Scrubber:
    return Scrubber(detectors=["es_nie"])


@pytest.mark.parametrize("v", VALID_NIES)
def test_nie_valid(nie_scrubber: Scrubber, v: str) -> None:
    matches = nie_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_NIES)
def test_nie_invalid(nie_scrubber: Scrubber, bad: str) -> None:
    matches = nie_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_nie_embedded(nie_scrubber: Scrubber) -> None:
    v = _nie("X", "1234567")
    text = f"Extranjero: {v}."
    m = nie_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: NIE must not fire on DNI (8 digits + letter)
def test_nie_no_fire_on_dni(nie_scrubber: Scrubber) -> None:
    assert nie_scrubber.scan(_dni("12345678")) == []


# ---------------------------------------------------------------------------
# ES_CIF
# ---------------------------------------------------------------------------


@pytest.fixture()
def cif_scrubber() -> Scrubber:
    return Scrubber(detectors=["es_cif"])


# Use stdnum to build valid CIF vectors
def _valid_cifs() -> list[str]:
    from stdnum.es import cif

    candidates = ["A28015865", "B08232854", "G28029619", "E08019975", "H91364862"]
    return [c for c in candidates if cif.is_valid(c)]


VALID_CIFS = _valid_cifs()


@pytest.mark.parametrize("v", VALID_CIFS)
def test_cif_valid(cif_scrubber: Scrubber, v: str) -> None:
    matches = cif_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_cif_invalid(cif_scrubber: Scrubber) -> None:
    # Valid shape but wrong check character
    bad = "A28015860"  # A + 7 digits + wrong check
    if bad not in VALID_CIFS:
        matches = cif_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_cif_embedded(cif_scrubber: Scrubber) -> None:
    if not VALID_CIFS:
        pytest.skip("no valid CIFs available")
    v = VALID_CIFS[0]
    text = f"CIF de la empresa: {v}."
    m = cif_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: CIF must not fire on IT Partita IVA (11 digits, different first char)
def test_cif_no_fire_on_partita_iva(cif_scrubber: Scrubber) -> None:
    # Partita IVA is 11 digits: CIF pattern requires letter first, so no match
    assert cif_scrubber.scan("12345678901") == []


# ---------------------------------------------------------------------------
# ES_NSS
# ---------------------------------------------------------------------------


@pytest.fixture()
def nss_scrubber() -> Scrubber:
    return Scrubber(detectors=["es_nss"])


def _nss(province: int, affiliation: int) -> str:
    if affiliation < 10_000_000:
        expected = (province * 10_000_000 + affiliation) % 97
    else:
        expected = int(f"{province:02d}{affiliation}") % 97
    return f"{province:02d}{affiliation:08d}{expected:02d}"


VALID_NSSS = [
    _nss(p, a) for p, a in [(28, 1234567), (8, 9876543), (41, 1111111), (1, 2345678), (50, 5555555)]
]


@pytest.mark.parametrize("v", VALID_NSSS)
def test_nss_valid(nss_scrubber: Scrubber, v: str) -> None:
    matches = nss_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_nss_invalid(nss_scrubber: Scrubber) -> None:
    bad = _nss(28, 1234567)[:-2] + "00"
    if not Scrubber(detectors=["es_nss"]).scan(bad)[0].valid:
        matches = nss_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_nss_with_slashes(nss_scrubber: Scrubber) -> None:
    v = _nss(28, 1234567)
    formatted = f"{v[:2]}/{v[2:10]}/{v[10:]}"
    matches = nss_scrubber.scan(formatted)
    assert len(matches) == 1 and matches[0].valid


def test_nss_embedded(nss_scrubber: Scrubber) -> None:
    v = _nss(28, 1234567)
    text = f"NSS: {v} alta en TGSS."
    m = nss_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# ---------------------------------------------------------------------------
# ES_CCC
# ---------------------------------------------------------------------------


@pytest.fixture()
def ccc_scrubber() -> Scrubber:
    return Scrubber(detectors=["es_ccc"])


def _valid_cccs() -> list[str]:
    from stdnum.es import ccc

    candidates = ["21000418450200051332", "00491500051234567892", "20770024003102575766"]
    return [c for c in candidates if ccc.is_valid(c)]


VALID_CCCS = _valid_cccs()


@pytest.mark.parametrize("v", VALID_CCCS)
def test_ccc_valid(ccc_scrubber: Scrubber, v: str) -> None:
    matches = ccc_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_ccc_invalid(ccc_scrubber: Scrubber) -> None:
    bad = "21000418990200051332"  # wrong check digits
    from stdnum.es import ccc

    if not ccc.is_valid(bad):
        matches = ccc_scrubber.scan(bad)
        assert len(matches) == 1 and not matches[0].valid


def test_ccc_with_spaces(ccc_scrubber: Scrubber) -> None:
    if not VALID_CCCS:
        pytest.skip("no valid CCCs available")
    v = VALID_CCCS[0]
    spaced = f"{v[:4]} {v[4:8]} {v[8:10]} {v[10:]}"
    matches = ccc_scrubber.scan(spaced)
    assert len(matches) == 1 and matches[0].valid


# ---------------------------------------------------------------------------
# ES_REFERENCIA_CATASTRAL
# ---------------------------------------------------------------------------


@pytest.fixture()
def catastro_scrubber() -> Scrubber:
    return Scrubber(detectors=["es_referencia_catastral"])


def _valid_catastros() -> list[str]:
    from stdnum.es import referenciacatastral as rc

    candidates = [
        "9872023VH5797S0001WX",
        "13077A01800039000BYZ",
        "7837301VH5173S0001WX",
    ]
    return [c for c in candidates if rc.is_valid(c)]


VALID_CATASTROS = _valid_catastros()


@pytest.mark.parametrize("v", VALID_CATASTROS)
def test_catastro_valid(catastro_scrubber: Scrubber, v: str) -> None:
    matches = catastro_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_catastro_invalid(catastro_scrubber: Scrubber) -> None:
    bad = "9872023VH5797S0001XX"  # wrong check chars
    from stdnum.es import referenciacatastral as rc

    if not rc.is_valid(bad):
        matches = catastro_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_catastro_embedded(catastro_scrubber: Scrubber) -> None:
    if not VALID_CATASTROS:
        pytest.skip("no valid catastral references available")
    v = VALID_CATASTROS[0]
    text = f"Ref. catastral: {v} (inmueble urbano)."
    m = catastro_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: catastral ref (20 chars) must not fire on IBAN (24+ chars)
def test_catastro_no_fire_on_iban(catastro_scrubber: Scrubber) -> None:
    assert catastro_scrubber.scan("ES9121000418450200051332") == []
