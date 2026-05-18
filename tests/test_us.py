"""Tests for US detectors.

Valid samples are either hardcoded canonical values or computed via the same
stdnum library used by the detectors, so they stay self-consistent. Negative
samples share the shape but break a structural rule or check digit.
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _wrong_last_digit(value: str) -> str:
    last = value[-1]
    if last.isdigit():  # noqa: SIM108  — clearer than a nested ternary
        replacement = "0" if last != "0" else "1"
    else:
        replacement = "A" if last != "A" else "B"
    return value[:-1] + replacement


# ---------------------------------------------------------------------------
# US_SSN
# ---------------------------------------------------------------------------

VALID_SSNS = ["001-01-0001", "001010001", "123-45-6789", "123456789"]
INVALID_SSN_SHAPES = [
    "000-12-3456",  # area 000 reserved
    "666-12-3456",  # area 666 reserved
    "900-12-3456",  # area 9xx reserved for ITIN/ATIN
    "123-00-4567",  # group 00 reserved
    "123-45-0000",  # serial 0000 reserved
    "078-05-1120",  # promotional / advertising SSN
]


@pytest.fixture()
def ssn_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_ssn"])


@pytest.mark.parametrize("v", VALID_SSNS)
def test_ssn_valid(ssn_scrubber: Scrubber, v: str) -> None:
    matches = ssn_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_SSN_SHAPES)
def test_ssn_structural_invalid(ssn_scrubber: Scrubber, bad: str) -> None:
    matches = ssn_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_ssn_embedded(ssn_scrubber: Scrubber) -> None:
    text = "SSN on file: 001-01-0001, thanks."
    m = ssn_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "001-01-0001"


def test_ssn_not_inside_word(ssn_scrubber: Scrubber) -> None:
    assert ssn_scrubber.scan("ref001010001abc") == []


# ---------------------------------------------------------------------------
# US_EIN
# ---------------------------------------------------------------------------

VALID_EINS = ["12-3456789", "04-1234567"]
INVALID_EIN_PREFIXES = ["00-1234567", "07-1234567", "08-1234567"]


@pytest.fixture()
def ein_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_ein"])


@pytest.mark.parametrize("v", VALID_EINS)
def test_ein_valid(ein_scrubber: Scrubber, v: str) -> None:
    matches = ein_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_EIN_PREFIXES)
def test_ein_invalid_prefix(ein_scrubber: Scrubber, bad: str) -> None:
    matches = ein_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_ein_compact_form_not_matched(ein_scrubber: Scrubber) -> None:
    # Compact form is intentionally not accepted to avoid collisions with
    # us_rtn and us_ssn. Hyphenated form is the IRS-canonical written form.
    assert ein_scrubber.scan("123456789") == []


def test_ein_embedded(ein_scrubber: Scrubber) -> None:
    text = "Federal EIN: 12-3456789 (W-9 attached)."
    m = ein_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "12-3456789"


# ---------------------------------------------------------------------------
# US_ITIN
# ---------------------------------------------------------------------------

VALID_ITINS = ["900-70-0000", "999-88-9999", "912-95-1234"]
INVALID_ITINS = [
    "900-50-0000",  # second group below 70
    "900-66-0000",  # below 70
    "900-89-0000",  # 89 explicitly excluded
    "900-93-0000",  # 93 reserved for ATIN
    "123-70-0000",  # area must start with 9
]


@pytest.fixture()
def itin_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_itin"])


@pytest.mark.parametrize("v", VALID_ITINS)
def test_itin_valid(itin_scrubber: Scrubber, v: str) -> None:
    matches = itin_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_ITINS)
def test_itin_invalid(itin_scrubber: Scrubber, bad: str) -> None:
    matches = itin_scrubber.scan(bad)
    # Pattern accepts 9xx-xx-xxxx; validator rejects out-of-range cases.
    # 123-70-0000 doesn't match the itin pattern at all because area must start with 9.
    if bad.startswith("9"):
        assert len(matches) == 1 and not matches[0].valid
    else:
        assert matches == []


# ---------------------------------------------------------------------------
# US_ATIN
# ---------------------------------------------------------------------------

VALID_ATINS = ["900-93-0000", "912-93-1234", "999-93-9999"]
INVALID_ATINS = ["900-94-0000", "900-92-0000", "123-93-0000"]


@pytest.fixture()
def atin_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_atin"])


@pytest.mark.parametrize("v", VALID_ATINS)
def test_atin_valid(atin_scrubber: Scrubber, v: str) -> None:
    matches = atin_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_ATINS)
def test_atin_invalid(atin_scrubber: Scrubber, bad: str) -> None:
    # Non-93 middle group should not even pattern-match (regex enforces 93).
    assert atin_scrubber.scan(bad) == []


def test_atin_compact_form(atin_scrubber: Scrubber) -> None:
    matches = atin_scrubber.scan("900930000")
    assert len(matches) == 1 and matches[0].valid


# ---------------------------------------------------------------------------
# US_PTIN
# ---------------------------------------------------------------------------

VALID_PTINS = ["P12345678", "P00000000", "P99999999"]


@pytest.fixture()
def ptin_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_ptin"])


@pytest.mark.parametrize("v", VALID_PTINS)
def test_ptin_valid(ptin_scrubber: Scrubber, v: str) -> None:
    matches = ptin_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_ptin_wrong_prefix(ptin_scrubber: Scrubber) -> None:
    # Q-prefix is not a PTIN
    assert ptin_scrubber.scan("Q12345678") == []


def test_ptin_embedded(ptin_scrubber: Scrubber) -> None:
    text = "Preparer PTIN: P12345678 on file."
    m = ptin_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "P12345678"


# ---------------------------------------------------------------------------
# US_RTN
# ---------------------------------------------------------------------------

VALID_RTNS = ["011000015", "122000247"]


@pytest.fixture()
def rtn_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_rtn"])


@pytest.mark.parametrize("v", VALID_RTNS)
def test_rtn_valid(rtn_scrubber: Scrubber, v: str) -> None:
    matches = rtn_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_rtn_invalid_checksum(rtn_scrubber: Scrubber) -> None:
    bad = _wrong_last_digit(VALID_RTNS[0])
    matches = rtn_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


# ---------------------------------------------------------------------------
# US_NPI
# ---------------------------------------------------------------------------

VALID_NPIS = ["1234567893", "1003000126"]  # 1234567893 is the canonical CMS test value.


@pytest.fixture()
def npi_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_npi"])


@pytest.mark.parametrize("v", VALID_NPIS)
def test_npi_valid(npi_scrubber: Scrubber, v: str) -> None:
    matches = npi_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_npi_invalid_checksum(npi_scrubber: Scrubber) -> None:
    bad = _wrong_last_digit(VALID_NPIS[0])
    matches = npi_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_npi_wrong_length(npi_scrubber: Scrubber) -> None:
    # Nine-digit numbers must not fire NPI.
    assert npi_scrubber.scan("123456789") == []


# ---------------------------------------------------------------------------
# US_DEA
# ---------------------------------------------------------------------------

VALID_DEAS = ["AB1234563"]


@pytest.fixture()
def dea_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_dea"])


@pytest.mark.parametrize("v", VALID_DEAS)
def test_dea_valid(dea_scrubber: Scrubber, v: str) -> None:
    matches = dea_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_dea_invalid_checksum(dea_scrubber: Scrubber) -> None:
    bad = _wrong_last_digit(VALID_DEAS[0])
    matches = dea_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_dea_embedded(dea_scrubber: Scrubber) -> None:
    text = "Prescriber DEA AB1234563 verified."
    m = dea_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "AB1234563"


# ---------------------------------------------------------------------------
# US_MBI
# ---------------------------------------------------------------------------

VALID_MBIS = ["1EG4-TE5-MK73", "1EG4TE5MK73"]
INVALID_MBIS_BY_ALPHABET = [
    "1SG4-TE5-MK73",  # S not allowed
    "1EG4-LE5-MK73",  # L not allowed
    "1EG4-TE5-OK73",  # O not allowed
]
INVALID_MBI_BY_POSITION = [
    "EEG4-TE5-MK73",  # position 1 must be digit
    "12G4-TE5-MK73",  # position 2 must be letter
]


@pytest.fixture()
def mbi_scrubber() -> Scrubber:
    return Scrubber(detectors=["us_mbi"])


@pytest.mark.parametrize("v", VALID_MBIS)
def test_mbi_valid(mbi_scrubber: Scrubber, v: str) -> None:
    matches = mbi_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_MBIS_BY_ALPHABET + INVALID_MBI_BY_POSITION)
def test_mbi_invalid_does_not_match(mbi_scrubber: Scrubber, bad: str) -> None:
    # Restricted-alphabet/position violations should not pattern-match at all.
    assert mbi_scrubber.scan(bad) == []


def test_mbi_embedded(mbi_scrubber: Scrubber) -> None:
    text = "Medicare MBI: 1EG4-TE5-MK73 on claim."
    m = mbi_scrubber.scan(text)[0]
    assert text[m.start : m.end] == "1EG4-TE5-MK73"


# ---------------------------------------------------------------------------
# Cross-detector / mixed-region integration
# ---------------------------------------------------------------------------


def test_mixed_us_document_values_scrubbed() -> None:
    # The default Scrubber loads every default-on detector. For US identifiers
    # with hyphens or unique prefixes (SSN, EIN, DEA, MBI), the US detector
    # wins because no other region produces a same-length match. For compact
    # 9- and 10-digit IDs (NPI, RTN), the alphabetical-fallback tie-break can
    # hand the match to another region — see test_known_cross_region_collisions.
    # Either way, the value is replaced with *some* token; that is the
    # property end users care about.
    s = Scrubber()
    text = (
        "Patient SSN 001-01-0001, EIN 12-3456789 for billing, "
        "NPI 1234567893, DEA AB1234563, MBI 1EG4-TE5-MK73, "
        "routing 011000015."
    )
    redacted = s.clean(text)
    for raw in (
        "001-01-0001",
        "12-3456789",
        "1234567893",
        "AB1234563",
        "1EG4-TE5-MK73",
        "011000015",
    ):
        assert raw not in redacted, f"{raw!r} leaked into redacted output"


def test_us_specific_tokens_when_disambiguated() -> None:
    # When US detectors are loaded in isolation (or alongside non-overlapping
    # regions), the US token is preserved exactly.
    s = Scrubber(detectors=["us_npi", "us_rtn"])
    text = "NPI 1234567893 and routing 011000015."
    redacted = s.clean(text)
    assert "{{US_NPI}}" in redacted
    assert "{{US_RTN}}" in redacted


def test_known_cross_region_collisions() -> None:
    # Documenting the engine's existing behavior: a 9-digit value that passes
    # both fr_siren's Luhn check and the ABA weighted checksum is tagged
    # fr_siren (alphabetical wins on tied length). Same idea for NPI vs
    # bg_pnf. The value is still scrubbed; only the token label differs.
    s = Scrubber()
    matches = {m.value: m.name for m in s.scan("NPI 1234567893") if m.valid}
    assert matches.get("1234567893") in {"us_npi", "bg_pnf"}
    matches = {m.value: m.name for m in s.scan("routing 011000015") if m.valid}
    assert matches.get("011000015") in {"us_rtn", "fr_siren"}


def test_us_and_eu_in_same_document() -> None:
    s = Scrubber()
    text = "SSN 001-01-0001 and Spanish DNI 12345678Z and IBAN DE89370400440532013000."
    matches = s.scan(text)
    names = {m.name for m in matches if m.valid}
    assert "us_ssn" in names
    assert "es_dni" in names
    assert "intl_iban" in names
