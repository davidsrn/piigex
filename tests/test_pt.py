"""Tests for Portuguese (pt) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# PT_NIF: Número de Identificação Fiscal
# ---------------------------------------------------------------------------


@pytest.fixture()
def nif_scrubber() -> Scrubber:
    return Scrubber(detectors=["pt_nif"])


def _valid_nifs() -> list[str]:
    from stdnum.pt import nif

    candidates = ["123456789", "100000002", "298000008", "272590690", "199999990"]
    return [c for c in candidates if nif.is_valid(c)]


VALID_NIFS = _valid_nifs()


@pytest.mark.parametrize("v", VALID_NIFS)
def test_nif_valid(nif_scrubber: Scrubber, v: str) -> None:
    matches = nif_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_nif_invalid(nif_scrubber: Scrubber) -> None:
    bad = "123456780"  # wrong check digit
    from stdnum.pt import nif

    if not nif.is_valid(bad):
        matches = nif_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_nif_embedded(nif_scrubber: Scrubber) -> None:
    if not VALID_NIFS:
        pytest.skip("no valid NIFs available")
    v = VALID_NIFS[0]
    text = f"NIF: {v}."
    m = nif_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: NIF (9 digits, non-zero first): digit 0 prefix must not fire
def test_nif_no_fire_on_leading_zero(nif_scrubber: Scrubber) -> None:
    assert nif_scrubber.scan("012345678") == []


def test_nif_no_fire_on_8_digits(nif_scrubber: Scrubber) -> None:
    assert nif_scrubber.scan("12345678") == []


def test_nif_no_fire_on_10_digits(nif_scrubber: Scrubber) -> None:
    assert nif_scrubber.scan("1234567890") == []


# ---------------------------------------------------------------------------
# PT_CC: Cartão de Cidadão
# ---------------------------------------------------------------------------


@pytest.fixture()
def cc_scrubber() -> Scrubber:
    return Scrubber(detectors=["pt_cc"])


def _valid_ccs() -> list[str]:
    from stdnum.pt import cc

    candidates = [
        "119145340ZZ8",
        "000000000ZZ4",
        "123456789ZZ6",
    ]
    return [c for c in candidates if cc.is_valid(c)]


VALID_CCS = _valid_ccs()


@pytest.mark.parametrize("v", VALID_CCS)
def test_cc_valid(cc_scrubber: Scrubber, v: str) -> None:
    matches = cc_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_cc_invalid(cc_scrubber: Scrubber) -> None:
    bad = "119145340ZZ0"  # wrong check digit
    from stdnum.pt import cc

    if not cc.is_valid(bad):
        matches = cc_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_cc_embedded(cc_scrubber: Scrubber) -> None:
    if not VALID_CCS:
        pytest.skip("no valid CCs available")
    v = VALID_CCS[0]
    text = f"Cartão de Cidadão: {v}."
    m = cc_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: CC requires 2 uppercase letters mid-string: all-digit sequences must not fire
def test_cc_no_fire_on_all_digits(cc_scrubber: Scrubber) -> None:
    assert cc_scrubber.scan("123456789012") == []


# ---------------------------------------------------------------------------
# PT_NISS: Número de Identificação de Segurança Social
# ---------------------------------------------------------------------------


@pytest.fixture()
def niss_scrubber() -> Scrubber:
    return Scrubber(detectors=["pt_niss"])


_NISS_WEIGHTS = (29, 23, 19, 17, 13, 11, 7, 5, 3, 2)


def _make_niss(prefix: str) -> str:
    assert len(prefix) == 10
    total = sum(int(d) * w for d, w in zip(prefix, _NISS_WEIGHTS, strict=False))
    check = (10 - (total % 10)) % 10
    return prefix + str(check)


VALID_NISSS = [
    _make_niss("1123456789"),
    _make_niss("2098765432"),
    _make_niss("5678901234"),
    _make_niss("6000000001"),
    _make_niss("8999999999"),
]


@pytest.mark.parametrize("v", VALID_NISSS)
def test_niss_valid(niss_scrubber: Scrubber, v: str) -> None:
    matches = niss_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("v", VALID_NISSS)
def test_niss_invalid_wrong_check(niss_scrubber: Scrubber, v: str) -> None:
    bad_check = str((int(v[-1]) + 1) % 10)
    bad = v[:-1] + bad_check
    matches = niss_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_niss_embedded(niss_scrubber: Scrubber) -> None:
    v = VALID_NISSS[0]
    text = f"NISS: {v}."
    m = niss_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: NISS first digit must be in {1,2,5,6,7,8}; 3/4/9 must not fire
def test_niss_no_fire_on_wrong_first_digit(niss_scrubber: Scrubber) -> None:
    assert niss_scrubber.scan("31234567890") == []
    assert niss_scrubber.scan("41234567890") == []
    assert niss_scrubber.scan("91234567890") == []
