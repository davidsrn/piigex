"""Tests for Bucket 2 detectors: es_passport, es_matricula, fr_cni, pt_passport,
nl_passport, be_ogm_vcs_delimited.

Positive vectors sourced from detector spec comments and Wikipedia.
"""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# ES_PASSPORT
# ---------------------------------------------------------------------------

# Spanish passport: 3 letters + 6 digits; no checksum: shape only.
# Source: https://www.interior.gob.es/
VALID_ES_PASSPORTS = [
    "PAE123456",
    "ABC000000",
    "XYZ999999",
    "PAB654321",
    "ZZZ123456",
]
INVALID_ES_PASSPORTS = [
    "PA123456",  # only 2 letters
    "ABCD12345",  # 4 letters
    "PAE12345",  # only 5 digits
    "PAE1234567",  # 7 digits
    "123456789",  # no letters
]


@pytest.fixture()
def esp_s() -> Scrubber:
    return Scrubber(detectors=["es_passport"])


@pytest.mark.parametrize("v", VALID_ES_PASSPORTS)
def test_es_passport_valid(esp_s: Scrubber, v: str) -> None:
    matches = esp_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_ES_PASSPORTS)
def test_es_passport_invalid(esp_s: Scrubber, bad: str) -> None:
    matches = esp_s.scan(bad)
    assert matches == [] or not matches[0].valid


def test_es_passport_embedded(esp_s: Scrubber) -> None:
    text = "Passport: PAE123456, issued in Madrid."
    m = esp_s.scan(text)
    assert len(m) == 1
    assert text[m[0].start : m[0].end] == "PAE123456"


def test_es_passport_not_inside_word(esp_s: Scrubber) -> None:
    assert esp_s.scan("xPAE123456") == []


def test_es_passport_cross_region(esp_s: Scrubber) -> None:
    # DNI (8d+L) should not fire on es_passport detector
    assert esp_s.scan("12345678Z") == []


def test_es_passport_stable_token() -> None:
    scrubber = Scrubber(detectors=["es_passport"], stable_tokens=True)
    result = scrubber.clean("PAE123456 and PAE123456")
    assert result.count("{{ES_PASSPORT_1}}") == 2


# ---------------------------------------------------------------------------
# ES_MATRICULA
# ---------------------------------------------------------------------------

# Spanish vehicle plate: 4 digits + 3 consonant letters (no vowels, no Q).
# Source: https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Spain
VALID_MATRICULAS = [
    "1234BCD",
    "5678FGH",
    "9999ZZZ",
    "0000BCB",
    "1234 BCD",  # with space separator
]
INVALID_MATRICULAS = [
    "1234ABC",  # A is a vowel
    "1234QRS",  # Q is excluded
    "123BCD",  # only 3 digits
    "12345BCD",  # 5 digits
    "1234BCDE",  # 4 letters
]


@pytest.fixture()
def mat_s() -> Scrubber:
    return Scrubber(detectors=["es_matricula"])


@pytest.mark.parametrize("v", VALID_MATRICULAS)
def test_matricula_valid(mat_s: Scrubber, v: str) -> None:
    matches = mat_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_MATRICULAS)
def test_matricula_invalid(mat_s: Scrubber, bad: str) -> None:
    matches = mat_s.scan(bad)
    assert matches == [] or not matches[0].valid


def test_matricula_embedded(mat_s: Scrubber) -> None:
    text = "Vehicle plate: 1234BCD (sedan)"
    m = mat_s.scan(text)
    assert len(m) == 1
    assert text[m[0].start : m[0].end] == "1234BCD"


def test_matricula_not_inside_word(mat_s: Scrubber) -> None:
    assert mat_s.scan("x1234BCDy") == []


def test_matricula_cross_region(mat_s: Scrubber) -> None:
    # DNI shape (8d+L) should not trigger matricula
    assert mat_s.scan("12345678Z") == []


def test_matricula_stable_token() -> None:
    scrubber = Scrubber(detectors=["es_matricula"], stable_tokens=True)
    result = scrubber.clean("1234BCD and 1234BCD")
    assert result.count("{{ES_MATRICULA_1}}") == 2


# ---------------------------------------------------------------------------
# FR_CNI (new CNIF format only)
# ---------------------------------------------------------------------------

# New CNIF: 1 digit + 2 letters + 6 alphanumeric (I and O excluded); 9 chars.
# Source: https://www.service-public.fr/particuliers/vosdroits/F1399
VALID_FR_CNIS = [
    "1AB123456",
    "2CD789012",
    "3EF345678",
    "9GH901234",
    "0JK567890",
]
INVALID_FR_CNIS = [
    "AB1123456",  # starts with letter, not digit
    "1A1123456",  # only 1 letter at position 2-3
    "1AB12345I",  # I is excluded
    "1AB12345O",  # O is excluded
]


@pytest.fixture()
def cni_s() -> Scrubber:
    return Scrubber(detectors=["fr_cni"])


@pytest.mark.parametrize("v", VALID_FR_CNIS)
def test_fr_cni_valid(cni_s: Scrubber, v: str) -> None:
    matches = cni_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_FR_CNIS)
def test_fr_cni_invalid(cni_s: Scrubber, bad: str) -> None:
    matches = cni_s.scan(bad)
    assert matches == [] or not matches[0].valid


def test_fr_cni_embedded(cni_s: Scrubber) -> None:
    text = "Carte nationale d'identité: 1AB123456."
    m = cni_s.scan(text)
    assert len(m) == 1
    assert text[m[0].start : m[0].end] == "1AB123456"


def test_fr_cni_not_inside_word(cni_s: Scrubber) -> None:
    assert cni_s.scan("x1AB123456") == []


def test_fr_cni_stable_token() -> None:
    scrubber = Scrubber(detectors=["fr_cni"], stable_tokens=True)
    result = scrubber.clean("CNI 1AB123456 and 1AB123456")
    assert result.count("{{FR_CNI_1}}") == 2


# ---------------------------------------------------------------------------
# PT_PASSPORT
# ---------------------------------------------------------------------------

# Portuguese passport: 2 letters + 6 digits; 8 chars. No checksum.
# Source: https://en.wikipedia.org/wiki/Portuguese_passport
VALID_PT_PASSPORTS = [
    "AB123456",
    "CD789012",
    "EF000000",
    "GH999999",
    "IJ456789",
]
INVALID_PT_PASSPORTS = [
    "A123456",  # only 1 letter
    "ABC12345",  # 3 letters
    "AB12345",  # only 5 digits
    "AB1234567",  # 7 digits
]


@pytest.fixture()
def ptp_s() -> Scrubber:
    return Scrubber(detectors=["pt_passport"])


@pytest.mark.parametrize("v", VALID_PT_PASSPORTS)
def test_pt_passport_valid(ptp_s: Scrubber, v: str) -> None:
    matches = ptp_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_PT_PASSPORTS)
def test_pt_passport_invalid(ptp_s: Scrubber, bad: str) -> None:
    matches = ptp_s.scan(bad)
    assert matches == [] or not matches[0].valid


def test_pt_passport_embedded(ptp_s: Scrubber) -> None:
    text = "Passaporte: AB123456 emitido em Lisboa."
    m = ptp_s.scan(text)
    assert len(m) == 1
    assert text[m[0].start : m[0].end] == "AB123456"


def test_pt_passport_not_inside_word(ptp_s: Scrubber) -> None:
    assert ptp_s.scan("xAB123456") == []


def test_pt_passport_stable_token() -> None:
    scrubber = Scrubber(detectors=["pt_passport"], stable_tokens=True)
    result = scrubber.clean("AB123456 and AB123456")
    assert result.count("{{PT_PASSPORT_1}}") == 2


# ---------------------------------------------------------------------------
# NL_PASSPORT
# ---------------------------------------------------------------------------

# Dutch passport: 9 chars: 2 letters + 6 alphanumeric + 1 digit; letter O excluded.
# Source: stdnum.nl.identiteitskaartnummer
VALID_NL_PASSPORTS = [
    "EM0000000",  # from stdnum docs
    "XR1001R58",  # from stdnum docs
    "AB1234561",  # 2 letters + 6 alphanum + 1 digit
    "CD5678902",
    "GH123B4C5",
]
INVALID_NL_PASSPORTS = [
    "OA1234567",  # O in first position
    "AO1234567",  # O in second position
    "AB12345O8",  # O in middle
    "AB12345",  # too short
    "AB1234567890",  # too long
]


@pytest.fixture()
def nlp_s() -> Scrubber:
    return Scrubber(detectors=["nl_passport"])


@pytest.mark.parametrize("v", VALID_NL_PASSPORTS)
def test_nl_passport_valid(nlp_s: Scrubber, v: str) -> None:
    matches = nlp_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_NL_PASSPORTS)
def test_nl_passport_invalid(nlp_s: Scrubber, bad: str) -> None:
    matches = nlp_s.scan(bad)
    assert matches == [] or not matches[0].valid


def test_nl_passport_embedded(nlp_s: Scrubber) -> None:
    text = "Passport number: XR1001R58 (Netherlands)"
    m = nlp_s.scan(text)
    assert len(m) == 1
    assert text[m[0].start : m[0].end] == "XR1001R58"


def test_nl_passport_not_inside_word(nlp_s: Scrubber) -> None:
    assert nlp_s.scan("xXR1001R58") == []


def test_nl_passport_stable_token() -> None:
    scrubber = Scrubber(detectors=["nl_passport"], stable_tokens=True)
    result = scrubber.clean("XR1001R58 and XR1001R58")
    assert result.count("{{NL_PASSPORT_1}}") == 2


# ---------------------------------------------------------------------------
# BE_OGM_VCS_DELIMITED
# ---------------------------------------------------------------------------

# Belgian structured payment reference in +++NNN/NNNN/NNNNN+++ form.
# Source: stdnum.be.ogm_vcs, https://febelfin.be
VALID_BE_OGMS = [
    "+++010/8068/17183+++",  # from stdnum docs
    "+++108/0681/71862+++",  # base 1080681718, check 62
    "+++123/4567/89002+++",  # base 1234567890, check 02
]
INVALID_BE_OGMS = [
    "+++010/8068/17180+++",  # wrong check (from stdnum docs)
    "+++010/8068/17185+++",  # wrong check
]


@pytest.fixture()
def ogm_s() -> Scrubber:
    return Scrubber(detectors=["be_ogm_vcs_delimited"])


@pytest.fixture()
def ogm_s_noval() -> Scrubber:
    return Scrubber(detectors=["be_ogm_vcs_delimited"], validate=False)


@pytest.mark.parametrize("v", VALID_BE_OGMS)
def test_be_ogm_valid(ogm_s: Scrubber, v: str) -> None:
    matches = ogm_s.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("bad", INVALID_BE_OGMS)
def test_be_ogm_invalid(ogm_s: Scrubber, bad: str) -> None:
    matches = ogm_s.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


@pytest.mark.parametrize("bad", INVALID_BE_OGMS)
def test_be_ogm_invalid_accepted_without_validation(ogm_s_noval: Scrubber, bad: str) -> None:
    matches = ogm_s_noval.scan(bad)
    # valid reflects the actual checksum result even in no-validate mode
    assert len(matches) == 1 and not matches[0].valid


def test_be_ogm_embedded(ogm_s: Scrubber) -> None:
    text = "Mededeling: +++010/8068/17183+++ voor betaling."
    m = ogm_s.scan(text)
    assert len(m) == 1
    assert text[m[0].start : m[0].end] == "+++010/8068/17183+++"


def test_be_ogm_raw_not_matched(ogm_s: Scrubber) -> None:
    # Raw 12-digit form without delimiters should not match
    assert ogm_s.scan("010806817183") == []


def test_be_ogm_stable_token() -> None:
    scrubber = Scrubber(detectors=["be_ogm_vcs_delimited"], stable_tokens=True)
    result = scrubber.clean("+++010/8068/17183+++ and +++010/8068/17183+++")
    assert result.count("{{BE_OGM_VCS_1}}") == 2


def test_be_ogm_different_values_different_tokens() -> None:
    scrubber = Scrubber(detectors=["be_ogm_vcs_delimited"], stable_tokens=True)
    result = scrubber.clean("+++010/8068/17183+++ and +++123/4567/89002+++")
    assert "{{BE_OGM_VCS_1}}" in result
    assert "{{BE_OGM_VCS_2}}" in result
