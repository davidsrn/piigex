"""Tests for international (intl) detectors."""

from __future__ import annotations

import pytest

from piigex import Scrubber

# ---------------------------------------------------------------------------
# INTL_BIC: Bank Identifier Code (ISO 9362)
# ---------------------------------------------------------------------------


@pytest.fixture()
def bic_scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_bic"])


def _valid_bics() -> list[str]:
    from stdnum import bic

    candidates = ["DEUTDEDB", "BNPAFRPP", "CITIUS33", "DEUTDEDDXXX", "INGBNL2A"]
    return [c for c in candidates if bic.is_valid(c)]


VALID_BICS = _valid_bics()


@pytest.mark.parametrize("v", VALID_BICS)
def test_bic_valid(bic_scrubber: Scrubber, v: str) -> None:
    matches = bic_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_bic_invalid(bic_scrubber: Scrubber) -> None:
    bad = "XXXXXYYY"  # invalid country code
    from stdnum import bic

    if not bic.is_valid(bad):
        matches = bic_scrubber.scan(bad)
        if matches:
            assert not matches[0].valid


def test_bic_embedded(bic_scrubber: Scrubber) -> None:
    if not VALID_BICS:
        pytest.skip("no valid BICs available")
    v = VALID_BICS[0]
    text = f"BIC: {v} (bank)."
    m = bic_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_bic_8char_and_11char(bic_scrubber: Scrubber) -> None:
    bic8 = next((b for b in VALID_BICS if len(b) == 8), None)
    bic11 = next((b for b in VALID_BICS if len(b) == 11), None)
    if bic8:
        assert bic_scrubber.scan(bic8)[0].valid
    if bic11:
        assert bic_scrubber.scan(bic11)[0].valid


# ---------------------------------------------------------------------------
# INTL_CREDIT_CARD: Payment card numbers (Luhn)
# ---------------------------------------------------------------------------


@pytest.fixture()
def cc_scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_credit_card"])


# Standard test card numbers (Luhn valid, not real)
VALID_CARDS = [
    "4111111111111111",  # Visa 16-digit
    "5500005555555559",  # Mastercard
    "371449635398431",  # Amex 15-digit
    "6011111111111117",  # Discover
]

VALID_CARDS_SPACED = [
    "4111 1111 1111 1111",
    "5500 0055 5555 5559",
    "3714 496353 98431",  # Amex 4-6-5 grouping
]


@pytest.mark.parametrize("v", VALID_CARDS)
def test_cc_valid(cc_scrubber: Scrubber, v: str) -> None:
    matches = cc_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


@pytest.mark.parametrize("v", VALID_CARDS_SPACED)
def test_cc_valid_spaced(cc_scrubber: Scrubber, v: str) -> None:
    matches = cc_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_cc_invalid_luhn(cc_scrubber: Scrubber) -> None:
    bad = "4111111111111110"  # wrong Luhn check digit
    matches = cc_scrubber.scan(bad)
    assert len(matches) == 1 and not matches[0].valid


def test_cc_embedded(cc_scrubber: Scrubber) -> None:
    v = VALID_CARDS[0]
    text = f"Card: {v} (expires 12/26)."
    m = cc_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_cc_not_redacted_when_invalid(cc_scrubber: Scrubber) -> None:
    bad = "4111111111111110"
    result = cc_scrubber.clean(f"Card: {bad}")
    assert bad in result


# ---------------------------------------------------------------------------
# INTL_EMAIL: Email addresses (RFC 5321)
# ---------------------------------------------------------------------------


@pytest.fixture()
def email_scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_email"])


VALID_EMAILS = [
    "user@example.com",
    "test.email+filter@domain.co.uk",
    "john.doe@sub.company.org",
    "admin@localhost.io",
]


@pytest.mark.parametrize("v", VALID_EMAILS)
def test_email_valid(email_scrubber: Scrubber, v: str) -> None:
    matches = email_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_email_embedded(email_scrubber: Scrubber) -> None:
    v = VALID_EMAILS[0]
    text = f"Contact us at {v} for details."
    m = email_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_email_normalize_lowercases(email_scrubber: Scrubber) -> None:
    from piigex.detectors import get_registry

    det = get_registry()["intl_email"]
    assert det.normalize("User@EXAMPLE.COM") == "user@example.com"


def test_email_no_fire_on_no_at(email_scrubber: Scrubber) -> None:
    assert email_scrubber.scan("notanemail") == []


def test_email_no_fire_on_no_domain(email_scrubber: Scrubber) -> None:
    assert email_scrubber.scan("user@") == []


# ---------------------------------------------------------------------------
# INTL_IPV4: IPv4 addresses
# ---------------------------------------------------------------------------


@pytest.fixture()
def ipv4_scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_ipv4"])


VALID_IPV4S = [
    "192.168.1.1",
    "10.0.0.1",
    "255.255.255.255",
    "0.0.0.0",
    "172.16.254.1",
]


@pytest.mark.parametrize("v", VALID_IPV4S)
def test_ipv4_valid(ipv4_scrubber: Scrubber, v: str) -> None:
    matches = ipv4_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_ipv4_embedded(ipv4_scrubber: Scrubber) -> None:
    v = "192.168.1.1"
    text = f"Server at {v} is unreachable."
    m = ipv4_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_ipv4_invalid_octet(ipv4_scrubber: Scrubber) -> None:
    assert ipv4_scrubber.scan("256.1.1.1") == []
    assert ipv4_scrubber.scan("192.168.1.999") == []


def test_ipv4_no_fire_on_too_few_octets(ipv4_scrubber: Scrubber) -> None:
    assert ipv4_scrubber.scan("192.168.1") == []


def test_ipv4_no_fire_on_too_many_octets(ipv4_scrubber: Scrubber) -> None:
    assert ipv4_scrubber.scan("192.168.1.1.1") == []


def test_ipv4_no_fire_on_leading_zeros(ipv4_scrubber: Scrubber) -> None:
    assert ipv4_scrubber.scan("01.02.03.04") == []
    assert ipv4_scrubber.scan("192.168.001.001") == []


# ---------------------------------------------------------------------------
# INTL_IPV6: IPv6 addresses
# ---------------------------------------------------------------------------


@pytest.fixture()
def ipv6_scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_ipv6"])


VALID_IPV6S = [
    "::1",
    "2001:db8::1",
    "fe80::1",
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
    "::",
]


@pytest.mark.parametrize("v", VALID_IPV6S)
def test_ipv6_valid(ipv6_scrubber: Scrubber, v: str) -> None:
    matches = ipv6_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_ipv6_embedded(ipv6_scrubber: Scrubber) -> None:
    v = "::1"
    text = f"Loopback is {v}."
    m = ipv6_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_ipv6_normalize(ipv6_scrubber: Scrubber) -> None:
    from piigex.detectors import get_registry

    det = get_registry()["intl_ipv6"]
    assert det.normalize("2001:0DB8:0000:0000:0000:0000:0000:0001") == "2001:db8::1"


def test_ipv6_invalid(ipv6_scrubber: Scrubber) -> None:
    bad = "gggg::1"  # invalid hex chars
    matches = ipv6_scrubber.scan(bad)
    if matches:
        assert not matches[0].valid


# ---------------------------------------------------------------------------
# INTL_MAC: MAC / EUI-48 addresses
# ---------------------------------------------------------------------------


@pytest.fixture()
def mac_scrubber() -> Scrubber:
    return Scrubber(detectors=["intl_mac"])


VALID_MACS = [
    "00:11:22:33:44:55",  # colon-separated
    "00-11-22-33-44-55",  # hyphen-separated
    "0011.2233.4455",  # Cisco dot notation
    "aa:bb:cc:dd:ee:ff",  # lowercase colon
    "FF:EE:DD:CC:BB:AA",  # uppercase colon
]


@pytest.mark.parametrize("v", VALID_MACS)
def test_mac_valid(mac_scrubber: Scrubber, v: str) -> None:
    matches = mac_scrubber.scan(v)
    assert len(matches) == 1 and matches[0].valid


def test_mac_embedded(mac_scrubber: Scrubber) -> None:
    v = "00:11:22:33:44:55"
    text = f"Interface MAC: {v} (hardware)"
    m = mac_scrubber.scan(text)[0]
    assert text[m.start : m.end] == v


def test_mac_normalize(mac_scrubber: Scrubber) -> None:
    from piigex.detectors import get_registry

    det = get_registry()["intl_mac"]
    assert det.normalize("00:11:22:33:44:55") == "001122334455"


def test_mac_no_fire_on_too_few_pairs(mac_scrubber: Scrubber) -> None:
    assert mac_scrubber.scan("00:11:22:33:44") == []


def test_mac_no_fire_on_non_hex(mac_scrubber: Scrubber) -> None:
    assert mac_scrubber.scan("ZZ:11:22:33:44:55") == []
