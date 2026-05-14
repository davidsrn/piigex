from __future__ import annotations

import pytest

from piigex import Scrubber
from piigex.detectors import get_registry

DEFAULT_VECTORS = [
    # (detector_name, valid_input)
    ("at_vnr", "1237 010180"),
    ("be_bis", "98472899765"),
    ("be_eid", "591191706458"),
    ("be_nn", "00012511148"),
    ("be_vat", "BE0428759497"),
    ("bg_egn", "7523169263"),
    ("bg_pnf", "7111042925"),
    ("cz_dic", "CZ7103192745"),
    ("cz_rc", "7103192745"),
    ("de_idnr", "36574261809"),
    ("de_svnr", "65071839M002"),
    ("de_vat", "DE136695976"),
    ("dk_cpr", "211062-5629"),
    ("dk_cvr", "13585628"),
    ("ee_ik", "47101010033"),
    ("es_ccc", "21000418401234567891"),
    ("es_cif", "A78304516"),
    ("es_dni", "00000023T"),
    ("es_nie", "X0095892M"),
    ("es_nss", "310657449456"),
    ("es_referencia_catastral", "9872023VH5797S0001WX"),
    ("fi_hetu", "131052-308T"),
    ("fi_ytunnus", "1572860-0"),
    ("fr_nif", "1000000000083"),
    ("fr_nir", "295109912611193"),
    ("fr_siren", "552081317"),
    ("fr_siret", "73282932000074"),
    ("fr_tva", "FR40303265045"),
    ("gr_amka", "01013099997"),
    ("hr_oib", "33392005961"),
    ("hu_anum", "12892312"),
    ("ie_pps", "1234567FA"),
    ("intl_bic", "DEUTDEFF"),
    ("intl_credit_card", "4111111111111111"),
    ("intl_email", "alice@example.com"),
    ("intl_eu_vat", "ESA78304516"),
    ("intl_iban", "GB29NWBK60161331926819"),
    ("intl_ipv4", "192.168.1.1"),
    ("intl_ipv6", "2001:db8::1"),
    ("intl_mac", "00:11:22:33:44:55"),
    ("it_codice_fiscale", "MRTMTT25D09F205Z"),
    ("it_partita_iva", "00743110157"),
    # lt_asmens: ee_ik has identical pattern and same checksum algorithm; ee_ik registered first
    ("nl_bsn", "662108735"),
    # nl_btw: intl_eu_vat matches same span and validates; NL BTW is an EU VAT
    ("pl_nip", "5260250274"),
    ("pl_pesel", "44051401359"),
    ("pl_regon", "192598184"),
    ("pt_cc", "000000000AA9"),
    ("pt_nif", "501964843"),
    ("pt_niss", "20000000002"),
    # ro_cf: intl_eu_vat matches same span and validates; RO fiscal code is an EU VAT
    ("ro_cnp", "1800101221144"),
    ("se_orgnr", "556036-0793"),
    ("se_personnummer", "640823+3234"),
    ("si_emso", "0101006500006"),
    ("si_maticna", "5300231000"),
    # sk_rc: cz_rc has identical pattern and is registered first
]

_STRUCTURAL_SKIPS: dict[str, str] = {}

# Detectors whose value also legitimately validates under another detector
# (same pattern + same algorithm, or genuine superset like EU VAT). Any of the
# listed tokens redacting the input is correct.
AMBIGUOUS_VECTORS = [
    # (vector, accepted_token_set, note)
    ("33309240064", {"LT_ASMENS", "EE_IK"}, "ee_ik shares pattern + ISO 7064 algorithm"),
    ("7103192745", {"SK_RC", "CZ_RC"}, "cz_rc shares pattern + divisible-by-11"),
    ("NL000099998B57", {"NL_BTW", "EU_VAT"}, "NL BTW is also an EU VAT"),
    ("RO99908", {"RO_CF", "EU_VAT"}, "RO CF is also an EU VAT"),
]


@pytest.mark.parametrize("name,vector", DEFAULT_VECTORS)
def test_default_scrubber_redacts(name: str, vector: str) -> None:
    registry = get_registry()
    if name not in registry:
        pytest.skip(f"detector {name!r} not registered")
    if name in _STRUCTURAL_SKIPS:
        pytest.skip(_STRUCTURAL_SKIPS[name])

    det = registry[name]
    if not det.validate(vector):
        pytest.skip(f"test vector {vector!r} for {name!r} not actually valid; fix the vector")

    s = Scrubber()
    matches = s.scan(vector)
    matching = [m for m in matches if m.name == name and m.valid]
    assert matching, f"expected {name!r} to match {vector!r}, got {matches}"

    result = s.clean(f"prefix {vector} suffix")
    assert f"{{{{{det.token}}}}}" in result, f"clean() did not redact {vector!r} as {det.token!r}"


def test_ipv4_no_leading_zeros() -> None:
    s = Scrubber(detectors=["intl_ipv4"])
    assert s.scan("01.02.03.04") == [], "01.02.03.04 must not match intl_ipv4"
    assert s.scan("192.168.001.001") == [], "192.168.001.001 must not match intl_ipv4"


@pytest.mark.parametrize("vector,tokens,_note", AMBIGUOUS_VECTORS)
def test_default_scrubber_ambiguous(vector: str, tokens: set[str], _note: str) -> None:
    s = Scrubber()
    result = s.clean(f"prefix {vector} suffix")
    assert any(f"{{{{{t}}}}}" in result for t in tokens), f"expected one of {tokens} in {result!r}"
