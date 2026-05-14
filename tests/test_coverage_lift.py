"""Coverage uplift: exercise normalize() and direct validator paths.

scan() and clean() with default settings don't call every detector's normalize()
(only stable-tokens mode does), and the per-detector regex pre-filters input
before validate() runs, so the validator's defensive shape-check branches
go untested in the per-detector suites. This file calls those code paths
directly so the coverage report reflects them.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from piigex import Scrubber
from piigex.core import _format_key
from piigex.detectors import get_detectors, get_registry, register
from piigex.detectors.base import Detector
from piigex.tokens import TokenMap

# Pairs of (detector_name, a-value-its-regex-accepts). Most pairs are valid
# checksum-wise; a few are shape-only because the detector is shape-only.
NORMALIZE_VECTORS = [
    ("at_vnr", "1237 010180"),
    ("be_bis", "98472899765"),
    ("be_eid", "591191706458"),
    ("be_nn", "00012511148"),
    ("be_ogm_vcs_delimited", "+++000/0000/00097+++"),
    ("be_phone", "0470 12 34 56"),
    ("be_vat", "BE0428759497"),
    ("bg_egn", "7523169263"),
    ("bg_pnf", "7111042925"),
    ("cz_dic", "CZ7103192745"),
    ("cz_rc", "710319/2745"),
    ("de_idnr", "36574261809"),
    ("de_phone", "+49 30 12345678"),
    ("de_svnr", "65071839M002"),
    ("de_vat", "DE136695976"),
    ("dk_cpr", "211062-5629"),
    ("dk_cvr", "13585628"),
    ("ee_ik", "47101010033"),
    ("es_ccc", "2100 0418 40 1234567891"),
    ("es_cif", "A78304516"),
    ("es_dni", "00000023T"),
    ("es_matricula", "1234 BCD"),
    ("es_nie", "X0095892M"),
    ("es_nss", "31/0657449/56"),
    ("es_passport", "PAE123456"),
    ("es_phone", "+34 612 345 678"),
    ("es_referencia_catastral", "9872023VH5797S0001WX"),
    ("fi_hetu", "131052-308T"),
    ("fi_ytunnus", "1572860-0"),
    ("fr_cni", "1AB123456"),
    ("fr_nif", "1000000000083"),
    ("fr_nir", "295109912611193"),
    ("fr_phone", "+33 1 23 45 67 89"),
    ("fr_siren", "552081317"),
    ("fr_siret", "73282932000074"),
    ("fr_tva", "FR40303265045"),
    ("gr_amka", "01013099997"),
    ("hr_oib", "33392005961"),
    ("hu_anum", "12892312"),
    ("ie_pps", "1234567FA"),
    ("intl_bic", "DEUTDEFF"),
    ("intl_credit_card", "4111-1111-1111-1111"),
    ("intl_email", "Alice@EXAMPLE.com"),
    ("intl_eu_vat", "ESA78304516"),
    ("intl_iban", "GB29 NWBK 6016 1331 9268 19"),
    ("intl_ipv4", "192.168.1.1"),
    ("intl_ipv6", "2001:0DB8:0000:0000:0000:0000:0000:0001"),
    ("intl_mac", "00:11:22:33:44:55"),
    ("intl_phone_e164", "+34999888777"),
    ("it_codice_fiscale", "MRTMTT25D09F205Z"),
    ("it_partita_iva", "00743110157"),
    ("it_phone", "+39 333 1234567"),
    ("lt_asmens", "33309240064"),
    ("nl_bsn", "662108735"),
    ("nl_btw", "NL000099998B57"),
    ("nl_passport", "AB1234561"),
    ("nl_phone", "+31 6 12345678"),
    ("pl_nip", "5260250274"),
    ("pl_pesel", "44051401359"),
    ("pl_regon", "192598184"),
    ("pt_cc", "000000000AA9"),
    ("pt_nif", "501964843"),
    ("pt_niss", "20000000002"),
    ("pt_passport", "AB123456"),
    ("pt_phone", "+351 912345678"),
    ("ro_cf", "RO99908"),
    ("ro_cnp", "1800101221144"),
    ("se_orgnr", "556036-0793"),
    ("se_personnummer", "640823+3234"),
    ("si_emso", "0101006500006"),
    ("si_maticna", "5300231000"),
    ("sk_rc", "710319/2745"),
]


@pytest.mark.parametrize("name,vector", NORMALIZE_VECTORS)
def test_normalize_runs(name: str, vector: str) -> None:
    """Every detector's normalize() returns a non-empty string for an accepted shape."""
    det = get_registry().get(name)
    if det is None:
        pytest.skip(f"{name} not registered")
    out = det.normalize(vector)
    assert isinstance(out, str)
    assert out


# Hand-rolled validators contain `return False` early-exit branches for inputs
# that don't match the expected shape. The regex pre-filter normally hides
# them from the per-detector tests; call validate() directly.


def test_svnr_validate_rejects_wrong_length() -> None:
    det = get_registry()["de_svnr"]
    assert det.validate("12345") is False
    assert det.validate("123456789012345") is False
    assert det.validate("abcdefghIJKL") is False


def test_nss_validate_rejects_wrong_length() -> None:
    det = get_registry()["es_nss"]
    assert det.validate("12") is False
    assert det.validate("abc") is False


def test_niss_validate_rejects_wrong_length() -> None:
    det = get_registry()["pt_niss"]
    assert det.validate("12") is False
    assert det.validate("123456789012345") is False


def test_ipv4_validate_rejects_garbage() -> None:
    det = get_registry()["intl_ipv4"]
    assert det.validate("1.2.3") is False
    assert det.validate("a.b.c.d") is False


def test_ipv6_validate_and_normalize_handle_garbage() -> None:
    det = get_registry()["intl_ipv6"]
    assert det.validate("not-an-ipv6") is False
    # normalize falls back to the original string on parse failure
    assert det.normalize("not-an-ipv6") == "not-an-ipv6"


def test_eu_vat_normalize_fallback_on_unparseable() -> None:
    det = get_registry()["intl_eu_vat"]
    # An unrecognised prefix makes stdnum.eu.vat.compact raise; the fallback
    # branch should strip separators and uppercase.
    out = det.normalize("XX 12-34.56")
    assert out == "XX123456"


def test_credit_card_validate_rejects_non_digit() -> None:
    det = get_registry()["intl_credit_card"]
    assert det.validate("abcdefghij") is False
    assert det.validate("123") is False  # too short


def test_email_validate_rejects_oversize_and_missing_at() -> None:
    det = get_registry()["intl_email"]
    assert det.validate("a" * 300) is False  # > 254 chars, no @
    assert det.validate("no-at-here") is False  # missing @
    assert det.validate("only@nodot") is False  # no dot in domain
    assert det.validate("@nolocal.com") is False  # empty local


def test_phone_e164_validate_rejects_missing_plus() -> None:
    det = get_registry()["intl_phone_e164"]
    assert det.validate("34999888777") is False  # no leading +
    assert det.validate("+1") is False  # too short
    assert det.validate("+0123456789") is False  # leading 0 after +


def test_it_phone_validate_rejects_non_canonical() -> None:
    det = get_registry()["it_phone"]
    # validate() is called via direct dispatch; empty and bad-prefix exits
    assert det.validate("") is False  # empty
    assert det.validate("+39") is False  # CC only
    assert det.validate("1234567890") is False  # doesn't start with 3 or 0


# ----- core.py edge cases -----


def test_format_key_brackets_when_dots_or_brackets_present() -> None:
    assert _format_key("normal") == "normal"
    assert _format_key("with.dot") == '["with.dot"]'
    assert _format_key("with[bracket") == '["with[bracket"]'
    assert _format_key("with]close") == '["with]close"]'


def test_scan_json_uses_bracket_path_for_dotted_keys() -> None:
    s = Scrubber()
    payload: dict[str, Any] = {"weird.key": "alice@example.com"}
    matches = s.scan_json(payload)
    assert any('["weird.key"]' in m.path for m in matches)


def test_empty_scrubber_scan_returns_empty() -> None:
    # Construct a Scrubber whose filter excludes every detector.
    all_names = list(get_registry())
    s = Scrubber(detectors=all_names, exclude=all_names)
    assert s.scan("anything 12345678Z") == []
    assert s.clean("anything 12345678Z") == "anything 12345678Z"


def test_scrubber_rejects_detector_with_unsupported_flag() -> None:
    class BadFlagDetector(Detector):
        name = "_test_bad_flag"
        token = "BAD"
        region = "intl"
        feasibility = "high"
        default_enabled = False
        pattern = re.compile(r"abc", re.IGNORECASE)

        def validate(self, candidate: str) -> bool:
            return True

    bad = BadFlagDetector()
    register(bad)
    try:
        with pytest.raises(ValueError, match="not allowed in the combined engine"):
            Scrubber(detectors=["_test_bad_flag"])
    finally:
        # Unregister so other tests are unaffected.
        from piigex.detectors import _REGISTRY

        _REGISTRY.pop("_test_bad_flag", None)


def test_default_scrubber_via_module_clean() -> None:
    # Exercise piigex.core._get_default's cached-path branch.
    import piigex

    assert "{{IBAN}}" in piigex.clean("IBAN GB29NWBK60161331926819")
    assert piigex.clean("IBAN GB29NWBK60161331926819")  # second call uses cache


def test_clean_with_per_call_token_map() -> None:
    s = Scrubber(stable_tokens=True)
    tm = TokenMap()
    out1 = s.clean("IBAN GB29NWBK60161331926819", token_map=tm)
    out2 = s.clean("Same IBAN: GB29NWBK60161331926819", token_map=tm)
    assert "{{IBAN_1}}" in out1
    assert "{{IBAN_1}}" in out2


# ----- detectors/__init__.py: feasibility filter (line 49) -----


def test_min_feasibility_filters_low_tier_detector() -> None:
    """A detector with feasibility='low' is excluded when min_feasibility='medium' (default)
    but included when min_feasibility='low'."""

    class LowFeasDetector(Detector):
        name = "_test_low_feas"
        token = "LOW"
        region = "intl"
        feasibility = "low"
        default_enabled = True
        pattern = re.compile(r"_TESTLOW_\d{4}")

        def validate(self, candidate: str) -> bool:
            return True

    low = LowFeasDetector()
    register(low)
    try:
        default_names = {d.name for d in get_detectors()}
        assert "_test_low_feas" not in default_names

        low_names = {d.name for d in get_detectors(min_feasibility="low")}
        assert "_test_low_feas" in low_names
    finally:
        from piigex.detectors import _REGISTRY

        _REGISTRY.pop("_test_low_feas", None)


# ----- detectors/base.py: default normalize() (line 20) -----


def test_default_normalize_strips_and_lowercases() -> None:
    class Plain(Detector):
        name = "_test_plain"
        token = "PLAIN"
        region = "intl"
        feasibility = "high"
        default_enabled = False
        pattern = re.compile(r"plain")

        def validate(self, candidate: str) -> bool:
            return True

    p = Plain()
    # Hit the inherited default: base.normalize lowercases and strips separators.
    assert p.normalize("Hello World.foo-bar") == "helloworldfoobar"
