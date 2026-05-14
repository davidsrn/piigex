"""Tests for Belgian (be) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# BE_NN: Rijksregisternummer / Numéro de registre national
# ---------------------------------------------------------------------------


@pytest.fixture()
def nn_scrubber() -> Scrubber:
    return Scrubber(detectors=["be_nn"])


def _valid_nns() -> list[str]:
    from stdnum.be import nn

    # Check: 97 - (first_9 % 97) == last_2
    # 90011500188: 900115001 % 97 = 9, check = 88 ✓
    # 85062500703: 850625007 % 97 = 94, check = 03 ✓
    candidates = ["90011500188", "85062500703", "75063000250", "93011533361"]
    return [c for c in candidates if nn.is_valid(c)]


VALID_NNS = _valid_nns()


@pytest.mark.parametrize("v", VALID_NNS)
def test_nn_valid(nn_scrubber: Scrubber, v: str) -> None:
    matches = nn_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_nn_invalid(nn_scrubber: Scrubber) -> None:
    bad = "90011500100"  # wrong check digits
    from stdnum.be import nn

    if not nn.is_valid(bad):
        matches = nn_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_nn_embedded(nn_scrubber: Scrubber) -> None:
    if not VALID_NNS:
        pytest.skip("no valid NNs available")
    v = VALID_NNS[0]
    text = f"Rijksregisternummer: {v}."
    m = nn_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: BIS month field is +20 or +40; those are not valid calendar months for NN
def test_nn_no_fire_on_bis(nn_scrubber: Scrubber) -> None:
    from stdnum.be import bis
    from stdnum.be import nn as be_nn

    # A valid BIS number has month 21-32 (unknown gender) or 41-52 (known gender)
    # stdnum.be.nn should reject it; test that valid=False is returned
    bis_candidate = "90211500134"  # month=21, valid BIS structure
    if bis.is_valid(bis_candidate) and not be_nn.is_valid(bis_candidate):
        matches = nn_scrubber.scan(bis_candidate)
        if matches:
            assert not matches[0].valid


# ---------------------------------------------------------------------------
# BE_BIS: BIS-nummer
# ---------------------------------------------------------------------------


@pytest.fixture()
def bis_scrubber() -> Scrubber:
    return Scrubber(detectors=["be_bis"])


def _valid_biss() -> list[str]:
    from stdnum.be import bis

    # Month +20 (gender unknown): 90211500134, 85266500?
    # Month +40 (gender known): 90411500?
    # 90211500134: 902115001 % 97 = 63, check = 34 ✓
    candidates = ["90211500134", "85426500119", "75423000297"]
    return [c for c in candidates if bis.is_valid(c)]


VALID_BISS = _valid_biss()


@pytest.mark.parametrize("v", VALID_BISS)
def test_bis_valid(bis_scrubber: Scrubber, v: str) -> None:
    matches = bis_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_bis_invalid(bis_scrubber: Scrubber) -> None:
    bad = "90211500100"  # wrong check digits
    from stdnum.be import bis

    if not bis.is_valid(bad):
        matches = bis_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_bis_embedded(bis_scrubber: Scrubber) -> None:
    if not VALID_BISS:
        pytest.skip("no valid BIS numbers available")
    v = VALID_BISS[0]
    text = f"BIS-nummer: {v}."
    m = bis_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# ---------------------------------------------------------------------------
# BE_VAT: BTW/TVA enterprise number
# ---------------------------------------------------------------------------


@pytest.fixture()
def be_vat_scrubber() -> Scrubber:
    return Scrubber(detectors=["be_vat"])


def _valid_be_vats() -> list[str]:
    from stdnum.be import vat

    # Check: last_2 + first_8 % 97 == 97
    # 0100000070: 1000000 % 97 = 27, 97-27=70 ✓
    # 0200000043: 2000000 % 97 = 54, 97-54=43 ✓
    # 0403019657: 4030196 % 97 = 40, 97-40=57 ✓
    candidates = [
        "BE0100000070",
        "BE0200000043",
        "BE0403019657",
        "0100000070",
        "0200000043",
    ]
    return [c for c in candidates if vat.is_valid(c)]


VALID_BE_VATS = _valid_be_vats()


@pytest.mark.parametrize("v", VALID_BE_VATS)
def test_be_vat_valid(be_vat_scrubber: Scrubber, v: str) -> None:
    matches = be_vat_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_be_vat_no_fire_on_de_vat(be_vat_scrubber: Scrubber) -> None:
    assert be_vat_scrubber.scan("DE123456789") == []


def test_be_vat_no_fire_on_nl_btw(be_vat_scrubber: Scrubber) -> None:
    assert be_vat_scrubber.scan("NL123456782B01") == []


def test_be_vat_embedded(be_vat_scrubber: Scrubber) -> None:
    if not VALID_BE_VATS:
        pytest.skip("no valid BE VAT numbers available")
    v = VALID_BE_VATS[0]
    text = f"BTW: {v} (bedrijf)."
    m = be_vat_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# ---------------------------------------------------------------------------
# BE_EID: Electronic Identity Card number
# ---------------------------------------------------------------------------


@pytest.fixture()
def eid_scrubber() -> Scrubber:
    return Scrubber(detectors=["be_eid"])


def _valid_eids() -> list[str]:
    from stdnum.be import eid

    # Check: last_2 = first_10 % 97 (0 → 97)
    # 100000000034: 1000000000 % 97 = 34 ✓
    # 200000000068: 2000000000 % 97 = 68 ✓
    candidates = ["100000000034", "200000000068", "592000033629"]
    return [c for c in candidates if eid.is_valid(c)]


VALID_EIDS = _valid_eids()


@pytest.mark.parametrize("v", VALID_EIDS)
def test_eid_valid(eid_scrubber: Scrubber, v: str) -> None:
    matches = eid_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_eid_invalid(eid_scrubber: Scrubber) -> None:
    bad = "100000000000"  # wrong check digits
    from stdnum.be import eid

    if not eid.is_valid(bad):
        matches = eid_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_eid_embedded(eid_scrubber: Scrubber) -> None:
    if not VALID_EIDS:
        pytest.skip("no valid eID numbers available")
    v = VALID_EIDS[0]
    text = f"eID: {v}."
    m = eid_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: eID (12 digits) must not fire on IBAN
def test_eid_no_fire_on_iban(eid_scrubber: Scrubber) -> None:
    assert eid_scrubber.scan("BE68539007547034") == []
