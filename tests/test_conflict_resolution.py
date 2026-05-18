from __future__ import annotations

from piigex import Scrubber

# ---------------------------------------------------------------------------
# Alphabetical tie-break (same span length, both candidates valid)
# ---------------------------------------------------------------------------


def test_alphabetical_tiebreak_rtn_siren() -> None:
    # 011000015 passes both the ABA RTN weighted checksum and the French SIREN
    # Luhn check. Both detectors match the same 9-character span. fr_siren sorts
    # before us_rtn, so fr_siren is returned.
    s = Scrubber(detectors=["us_rtn", "fr_siren"])
    matches = [m for m in s.scan("011000015") if m.valid]
    assert len(matches) == 1
    assert matches[0].name == "fr_siren"


def test_alphabetical_tiebreak_validate_false() -> None:
    # With validate=False, invalid candidates are no longer filtered before
    # tie-break; both candidates here are valid, so fr_siren still wins.
    s = Scrubber(detectors=["us_rtn", "fr_siren"], validate=False)
    matches = s.scan("011000015")
    assert len(matches) == 1
    assert matches[0].name == "fr_siren"


def test_isolation_removes_collision() -> None:
    # Enabling only one of the colliding detectors gives the correct token.
    s = Scrubber(detectors=["us_rtn"])
    matches = [m for m in s.scan("011000015") if m.valid]
    assert len(matches) == 1
    assert matches[0].name == "us_rtn"


# ---------------------------------------------------------------------------
# Validate=True: invalid candidate is excluded
# ---------------------------------------------------------------------------


def test_invalid_match_not_redacted_by_default() -> None:
    # A value that matches the RTN pattern but fails the checksum is returned
    # by scan() with valid=False and is left untouched by clean().
    bad = "011000014"  # last digit corrupted from 5 → 4
    s = Scrubber(detectors=["us_rtn"])
    matches = s.scan(bad)
    assert len(matches) == 1
    assert not matches[0].valid
    assert s.clean(bad) == bad


# ---------------------------------------------------------------------------
# Phone-shaped value overlapping with a checksummed detector
# ---------------------------------------------------------------------------


def test_npi_wins_over_phone_same_span_shape_only() -> None:
    # 3024567893 satisfies the NANP phone shape (area 302, exchange 456) and
    # also matches the 10-digit NPI pattern. With validate=False, both
    # detectors treat it as a shape match. us_npi sorts before us_phone, so
    # us_npi is returned.
    s = Scrubber(detectors=["us_npi", "us_phone"], validate=False)
    matches = s.scan("3024567893")
    assert len(matches) == 1
    assert matches[0].name == "us_npi"


def test_phone_wins_without_npi() -> None:
    # Same value with only us_phone active: the phone detector claims it.
    s = Scrubber(detectors=["us_phone"], validate=False)
    matches = s.scan("3024567893")
    assert len(matches) == 1
    assert matches[0].name == "us_phone"
