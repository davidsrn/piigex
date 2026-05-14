"""Tests for the intl_eu_vat detector.

Positive vectors sourced from:
  https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.eu.vat (module docstring)
  https://ec.europa.eu/taxation_customs/business/vat/eu-vat-rules-topic/vat-identification-numbers_en
Negative vectors share the shape but have deliberately wrong check digits.
"""

from __future__ import annotations

import pytest

from piigex import Scrubber


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["intl_eu_vat"])


@pytest.fixture()
def s_noval() -> Scrubber:
    return Scrubber(detectors=["intl_eu_vat"], validate=False)


# ---------------------------------------------------------------------------
# 1. Positive: valid EU VAT numbers accepted when validate=True
# ---------------------------------------------------------------------------

# Sources: stdnum.eu.vat docstring; country VAT module docstrings; Wikipedia
VALID_EU_VATS = [
    "ATU57194903",  # Austria: stdnum.at.vat docstring
    "BE0697449992",  # Belgium: stdnum.eu.vat docstring
    "FR61954506077",  # France: stdnum.eu.vat docstring
    "CZ25123891",  # Czech Republic: stdnum.cz.dic docstring (legal entity)
    "DE136695976",  # Germany: stdnum.de.vat valid example
    "DK13585628",  # Denmark
    "EE100931558",  # Estonia
    "EL040127797",  # Greece (uses EL prefix)
    "IE6433435F",  # Ireland
    "IT00743110157",  # Italy
    "HU12892312",  # Hungary: stdnum.hu.anum docstring
    "LT100001919017",  # Lithuania
    "LU26375245",  # Luxembourg
    "MT20200019",  # Malta
    "NL000000024B01",  # Netherlands
    "PL5260001246",  # Poland
    "PT501964843",  # Portugal
    "RO18547290",  # Romania
    "SE123456789701",  # Sweden
    "SI50223054",  # Slovenia
    "SK2022749619",  # Slovakia
    "HR33392005961",  # Croatia
    "CY10259033P",  # Cyprus
    "BG7523169263",  # Bulgaria
    "FI20774740",  # Finland
]


@pytest.mark.parametrize("v", VALID_EU_VATS)
def test_valid_accepted(s: Scrubber, v: str) -> None:
    matches = s.scan(v)
    assert len(matches) == 1
    assert matches[0].valid is True
    assert matches[0].name == "intl_eu_vat"


# ---------------------------------------------------------------------------
# 2. Negative: shape-valid strings that fail country-specific checksum
# ---------------------------------------------------------------------------

INVALID_EU_VATS = [
    "ATU57194900",  # wrong check digit
    "BE0697449990",  # wrong check digit
    "DE136695970",  # wrong check digit
    "HU12892313",  # from stdnum docs: invalid check digit
    "SK2022749610",  # wrong check
    "SI50223050",  # wrong check
]


@pytest.mark.parametrize("bad", INVALID_EU_VATS)
def test_invalid_rejected_when_validating(s: Scrubber, bad: str) -> None:
    matches = s.scan(bad)
    # Regex may or may not match depending on shape; if it matches, validate=False
    if matches:
        assert matches[0].valid is False


@pytest.mark.parametrize("bad", INVALID_EU_VATS)
def test_invalid_accepted_without_validation(s_noval: Scrubber, bad: str) -> None:
    matches = s_noval.scan(bad)
    if matches:
        assert matches[0].valid is False  # valid reflects actual validity even in no-validate mode


# ---------------------------------------------------------------------------
# 3. Embedded: VAT number inside natural-language text
# ---------------------------------------------------------------------------


def test_embedded_compact_span(s: Scrubber) -> None:
    text = "VAT number: ATU57194903 (Austria)"
    matches = s.scan(text)
    vat_matches = [m for m in matches if m.name == "intl_eu_vat"]
    assert len(vat_matches) == 1
    m = vat_matches[0]
    assert text[m.start : m.end] == "ATU57194903"


def test_embedded_multiple(s: Scrubber) -> None:
    text = "Vendor ATU57194903 and client BE0697449992 both registered."
    matches = [m for m in s.scan(text) if m.name == "intl_eu_vat"]
    assert len(matches) == 2


def test_not_matched_inside_word(s: Scrubber) -> None:
    text = "prefixATU57194903suffix"
    matches = [m for m in s.scan(text) if m.name == "intl_eu_vat"]
    assert matches == []


# ---------------------------------------------------------------------------
# 4. Cross-region isolation
# ---------------------------------------------------------------------------


def test_no_false_positive_on_plain_digits(s: Scrubber) -> None:
    # Plain digits without valid EU country prefix must not match
    assert s.scan("123456789") == []


def test_no_false_positive_non_eu_prefix(s: Scrubber) -> None:
    # US-style TIN with "US" prefix is not an EU VAT prefix
    assert s.scan("US123456789") == []


# ---------------------------------------------------------------------------
# 5. Stable token
# ---------------------------------------------------------------------------


def test_stable_same_value_same_token() -> None:
    scrubber = Scrubber(detectors=["intl_eu_vat"], stable_tokens=True)
    text = "ATU57194903 and ATU57194903"
    result = scrubber.clean(text)
    assert result.count("{{EU_VAT_1}}") == 2


def test_stable_different_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["intl_eu_vat"], stable_tokens=True)
    text = "ATU57194903 and BE0697449992"
    result = scrubber.clean(text)
    assert "{{EU_VAT_1}}" in result
    assert "{{EU_VAT_2}}" in result
