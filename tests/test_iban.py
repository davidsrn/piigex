"""Tests for the intl_iban detector.

Positive test vectors sourced from:
  https://en.wikipedia.org/wiki/International_Bank_Account_Number#Validating_the_IBAN
  https://www.iban.com/testibans

Negative vectors are shape-valid (correct country prefix + length) with deliberately
wrong check digits (positions 3–4 changed to '00') so mod-97 validation fails.
"""

from __future__ import annotations

import pytest

from piigex import Match, Scrubber, clean, scan
from piigex.tokens import TokenMap

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_iban"])


@pytest.fixture()
def scrubber_noval() -> Scrubber:
    return Scrubber(detectors=["intl_iban"], validate=False)


# ---------------------------------------------------------------------------
# 1. Positive: valid IBANs accepted when validate=True
# ---------------------------------------------------------------------------

VALID_IBANS = [
    # (compact, formatted, country)
    ("GB29NWBK60161331926819", "GB29 NWBK 6016 1331 9268 19", "GB"),
    ("DE89370400440532013000", "DE89 3704 0044 0532 0130 00", "DE"),
    ("FR7630006000011234567890189", "FR76 3000 6000 0112 3456 7890 189", "FR"),
    ("ES9121000418450200051332", "ES91 2100 0418 4502 0005 1332", "ES"),
    ("NL91ABNA0417164300", "NL91 ABNA 0417 1643 00", "NL"),
]


@pytest.mark.parametrize("compact,_formatted,_country", VALID_IBANS)
def test_valid_compact_detected_and_validated(
    scrubber: Scrubber, compact: str, _formatted: str, _country: str
) -> None:
    matches = scrubber.scan(compact)
    assert len(matches) == 1
    assert matches[0].valid is True
    assert matches[0].name == "intl_iban"
    assert matches[0].value == compact


@pytest.mark.parametrize("_compact,formatted,_country", VALID_IBANS)
def test_valid_formatted_detected_and_validated(
    scrubber: Scrubber, _compact: str, formatted: str, _country: str
) -> None:
    matches = scrubber.scan(formatted)
    assert len(matches) == 1
    assert matches[0].valid is True


# ---------------------------------------------------------------------------
# 2. Negative: shape-valid strings that fail the mod-97 checksum
# ---------------------------------------------------------------------------

INVALID_IBANS = [
    "GB00NWBK60161331926819",  # wrong check digits
    "DE00370400440532013000",
    "FR0030006000011234567890189",
    "ES0021000418450200051332",
    "NL00ABNA0417164300",
]


@pytest.mark.parametrize("bad", INVALID_IBANS)
def test_invalid_rejected_when_validating(scrubber: Scrubber, bad: str) -> None:
    matches = scrubber.scan(bad)
    # regex should still find the candidate …
    assert len(matches) == 1
    # … but checksum must fail
    assert matches[0].valid is False


@pytest.mark.parametrize("bad", INVALID_IBANS)
def test_invalid_accepted_when_not_validating(scrubber_noval: Scrubber, bad: str) -> None:
    matches = scrubber_noval.scan(bad)
    assert len(matches) == 1
    assert matches[0].valid is False  # valid reflects actual validity even in no-validate mode


@pytest.mark.parametrize("bad", INVALID_IBANS)
def test_invalid_not_redacted_in_clean(scrubber: Scrubber, bad: str) -> None:
    text = f"Account: {bad}, please verify."
    result = scrubber.clean(text)
    assert bad in result  # not redacted


# ---------------------------------------------------------------------------
# 3. Embedded: IBAN inside natural-language text; verify spans
# ---------------------------------------------------------------------------


def test_embedded_compact_span(scrubber: Scrubber) -> None:
    text = "Wire to ES9121000418450200051332, thanks."
    matches = scrubber.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert m.start == 8
    assert m.end == 32
    assert text[m.start : m.end] == "ES9121000418450200051332"


def test_embedded_formatted_span(scrubber: Scrubber) -> None:
    text = "Send €100 to GB29 NWBK 6016 1331 9268 19 today."
    matches = scrubber.scan(text)
    assert len(matches) == 1
    m = matches[0]
    assert text[m.start : m.end] == "GB29 NWBK 6016 1331 9268 19"


def test_embedded_with_punctuation(scrubber: Scrubber) -> None:
    text = "(IBAN: DE89370400440532013000)"
    matches = scrubber.scan(text)
    assert len(matches) == 1
    assert matches[0].value == "DE89370400440532013000"


def test_embedded_clean_replaces_only_valid(scrubber: Scrubber) -> None:
    text = "Good: ES9121000418450200051332 bad: ES0021000418450200051332"
    result = scrubber.clean(text)
    assert "{{IBAN}}" in result
    assert "ES0021000418450200051332" in result  # invalid, not redacted
    assert "ES9121000418450200051332" not in result  # valid, redacted


def test_multiple_ibans_in_text(scrubber: Scrubber) -> None:
    text = "A=GB29NWBK60161331926819 B=DE89370400440532013000"
    matches = scrubber.scan(text)
    assert len(matches) == 2
    result = scrubber.clean(text)
    assert result.count("{{IBAN}}") == 2


# ---------------------------------------------------------------------------
# 4. Cross-region isolation: IBAN detector must not fire on non-IBAN tokens
# ---------------------------------------------------------------------------


def test_no_false_positive_on_short_alphanumeric(scrubber: Scrubber) -> None:
    # Short strings that start with two letters + two digits but are too short
    for candidate in ["AB12", "ES91", "DE89"]:
        assert scrubber.scan(candidate) == []


def test_no_false_positive_embedded_in_word(scrubber: Scrubber) -> None:
    # Must not match when immediately adjacent to other alphanumeric chars
    text = "theES9121000418450200051332end"
    matches = scrubber.scan(text)
    assert matches == []


def test_no_false_positive_lowercase_prefix(scrubber: Scrubber) -> None:
    # Lowercase prefix touches the candidate: lookbehind should block it
    text = "refES9121000418450200051332"
    matches = scrubber.scan(text)
    assert matches == []


# ---------------------------------------------------------------------------
# 5. Stable tokens
# ---------------------------------------------------------------------------


def test_stable_same_value_same_token() -> None:
    s = Scrubber(detectors=["intl_iban"], stable_tokens=True)
    text = "A=ES9121000418450200051332 B=ES9121000418450200051332"
    result = s.clean(text)
    assert result.count("{{IBAN_1}}") == 2


def test_stable_normalized_equivalents_same_token() -> None:
    s = Scrubber(detectors=["intl_iban"], stable_tokens=True)
    # Compact and formatted forms of the same IBAN
    compact = "ES9121000418450200051332"
    formatted = "ES91 2100 0418 4502 0005 1332"
    result = s.clean(f"A={compact} B={formatted}")
    # Both occurrences are the same IBAN → same token index
    assert result.count("{{IBAN_1}}") == 2
    assert "{{IBAN_2}}" not in result


def test_stable_different_values_different_tokens() -> None:
    s = Scrubber(detectors=["intl_iban"], stable_tokens=True)
    text = "A=ES9121000418450200051332 B=DE89370400440532013000"
    result = s.clean(text)
    assert "{{IBAN_1}}" in result
    assert "{{IBAN_2}}" in result


def test_stable_token_map_resets_each_call() -> None:
    s = Scrubber(detectors=["intl_iban"], stable_tokens=True)
    first = s.clean("ES9121000418450200051332")
    second = s.clean("DE89370400440532013000")
    # Each call gets its own TokenMap, so both get index 1
    assert first == "{{IBAN_1}}"
    assert second == "{{IBAN_1}}"


def test_persistent_token_map_across_calls() -> None:
    tm = TokenMap()
    s = Scrubber(detectors=["intl_iban"], stable_tokens=True, token_map=tm)
    first = s.clean("ES9121000418450200051332")
    second = s.clean("DE89370400440532013000")
    assert first == "{{IBAN_1}}"
    assert second == "{{IBAN_2}}"


# ---------------------------------------------------------------------------
# 6. Module-level convenience functions use default Scrubber
# ---------------------------------------------------------------------------


def test_module_scan_returns_match() -> None:
    matches = scan("Pay to GB29NWBK60161331926819 now")
    iban_matches = [m for m in matches if m.name == "intl_iban"]
    assert len(iban_matches) == 1
    assert iban_matches[0].valid is True


def test_module_clean_redacts() -> None:
    result = clean("IBAN: NL91ABNA0417164300")
    assert "{{IBAN}}" in result
    assert "NL91ABNA0417164300" not in result


# ---------------------------------------------------------------------------
# 7. Match dataclass fields
# ---------------------------------------------------------------------------


def test_match_fields(scrubber: Scrubber) -> None:
    matches = scrubber.scan("GB29NWBK60161331926819")
    assert len(matches) == 1
    m = matches[0]
    assert isinstance(m, Match)
    assert m.name == "intl_iban"
    assert m.token == "IBAN"
    assert m.value == "GB29NWBK60161331926819"
    assert m.start == 0
    assert m.end == 22
    assert m.valid is True


# ---------------------------------------------------------------------------
# 8. Registry / get_detectors filter paths
# ---------------------------------------------------------------------------


def test_get_registry_contains_iban() -> None:
    from piigex.detectors import get_registry

    registry = get_registry()
    assert "intl_iban" in registry


def test_get_detectors_exclude() -> None:
    from piigex.detectors import get_detectors

    result = get_detectors(exclude=["intl_iban"])
    assert all(d.name != "intl_iban" for d in result)


def test_get_detectors_region_filter() -> None:
    from piigex.detectors import get_detectors

    # Only intl region: IBAN should appear
    result = get_detectors(regions=["intl"])
    assert any(d.name == "intl_iban" for d in result)
    # Non-existent region: nothing matches
    result2 = get_detectors(regions=["xx"])
    assert result2 == []


def test_get_detectors_feasibility_high_only() -> None:
    from piigex.detectors import get_detectors

    # IBAN is "high": must be included
    result = get_detectors(min_feasibility="high")
    assert any(d.name == "intl_iban" for d in result)


def test_get_detectors_explicit_names_bypasses_enabled() -> None:
    from piigex.detectors import get_detectors

    # Requesting by explicit name always returns it
    result = get_detectors(names=["intl_iban"])
    assert len(result) == 1
    assert result[0].name == "intl_iban"


def test_get_detectors_explicit_name_not_in_registry() -> None:
    from piigex.detectors import get_detectors

    result = get_detectors(names=["nonexistent_detector"])
    assert result == []


# ---------------------------------------------------------------------------
# 9. Scrubber with no detectors (edge case)
# ---------------------------------------------------------------------------


def test_empty_scrubber_scan() -> None:
    s = Scrubber(detectors=[])
    assert s.scan("GB29NWBK60161331926819") == []


def test_empty_scrubber_clean() -> None:
    s = Scrubber(detectors=[])
    text = "GB29NWBK60161331926819"
    assert s.clean(text) == text


# ---------------------------------------------------------------------------
# 10. Normalize and TokenMap.reset
# ---------------------------------------------------------------------------


def test_normalize_strips_spaces_and_case() -> None:
    from piigex.detectors import get_registry

    det = get_registry()["intl_iban"]
    # stdnum compact strips spaces; normalize() delegates to it
    compact = det.normalize("ES91 2100 0418 4502 0005 1332")
    assert compact == "ES9121000418450200051332"


def test_token_map_reset() -> None:
    tm = TokenMap()
    tm.get("intl_iban", "abc")
    assert tm.get("intl_iban", "abc") == 1
    tm.reset()
    # After reset, counter starts again
    assert tm.get("intl_iban", "abc") == 1
