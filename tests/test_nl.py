"""Tests for Dutch (nl) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# NL_BSN: Burgerservicenummer
# ---------------------------------------------------------------------------


@pytest.fixture()
def bsn_scrubber() -> Scrubber:
    return Scrubber(detectors=["nl_bsn"])


def _valid_bsns() -> list[str]:
    from stdnum.nl import bsn

    # Elfproef: sum((9-i)*d[i] for i=0..7) - d[8] ≡ 0 mod 11
    # 123456782: 9+16+21+24+25+24+21+16-2=154, 154%11=0 ✓
    # 111222333: 9+8+7+12+10+8+9+6-3=66, 66%11=0 ✓
    candidates = ["123456782", "111222333", "100000009", "999999990", "020020028"]
    return [c for c in candidates if bsn.is_valid(c)]


VALID_BSNS = _valid_bsns()


@pytest.mark.parametrize("v", VALID_BSNS)
def test_bsn_valid(bsn_scrubber: Scrubber, v: str) -> None:
    matches = bsn_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_bsn_invalid(bsn_scrubber: Scrubber) -> None:
    bad = "123456780"  # wrong check digit
    from stdnum.nl import bsn

    if not bsn.is_valid(bad):
        matches = bsn_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_bsn_embedded(bsn_scrubber: Scrubber) -> None:
    if not VALID_BSNS:
        pytest.skip("no valid BSNs available")
    v = VALID_BSNS[0]
    text = f"BSN: {v} (burger)."
    m = bsn_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


# Cross-region: a valid FR SIREN that is not a valid BSN should return invalid
def test_bsn_checksum_differs_from_siren(bsn_scrubber: Scrubber) -> None:
    from stdnum.fr import siren as fr_s
    from stdnum.nl import bsn as nl_b

    for v in ["732829320", "552081317"]:
        if fr_s.is_valid(v) and not nl_b.is_valid(v):
            matches = bsn_scrubber.scan(v)
            if matches:
                assert not matches[0].valid
            break


# ---------------------------------------------------------------------------
# NL_BTW: BTW-nummer (Dutch VAT)
# ---------------------------------------------------------------------------


@pytest.fixture()
def btw_scrubber() -> Scrubber:
    return Scrubber(detectors=["nl_btw"])


def _valid_btwns() -> list[str]:
    from stdnum.nl import btw

    # RSIN (9-digit) shares elfproef with BSN; 123456782 passes elfproef
    candidates = ["NL123456782B01", "NL800265863B01", "NL002205864B01"]
    return [c for c in candidates if btw.is_valid(c)]


VALID_BTWNS = _valid_btwns()


@pytest.mark.parametrize("v", VALID_BTWNS)
def test_btw_valid(btw_scrubber: Scrubber, v: str) -> None:
    matches = btw_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_btw_embedded(btw_scrubber: Scrubber) -> None:
    if not VALID_BTWNS:
        pytest.skip("no valid BTW numbers available")
    v = VALID_BTWNS[0]
    text = f"BTW-nummer: {v}."
    m = btw_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_btw_no_fire_on_de_vat(btw_scrubber: Scrubber) -> None:
    assert btw_scrubber.scan("DE123456789") == []


def test_btw_no_fire_on_fr_tva(btw_scrubber: Scrubber) -> None:
    assert btw_scrubber.scan("FR40303265045") == []


def test_btw_no_fire_on_be_vat(btw_scrubber: Scrubber) -> None:
    assert btw_scrubber.scan("BE0403019657") == []
