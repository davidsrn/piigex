from __future__ import annotations

import ipaddress
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_H = r"[0-9A-Fa-f]{1,4}"


class Ipv6Detector(Detector):
    # IPv6 addresses per RFC 4291. https://tools.ietf.org/html/rfc4291
    # Covers full form, :: compressed forms, and ::1 loopback.
    name = "intl_ipv6"
    token = "IPV6"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![:\w])"
        r"(?:"
        rf"(?:{_H}:){{7}}{_H}"  # full: 8 groups
        rf"|(?:{_H}:){{1,7}}:"  # ends with ::
        rf"|(?:{_H}:){{1,6}}:{_H}"  # one :: gap
        rf"|(?:{_H}:){{1,5}}(?::{_H}){{2}}"
        rf"|(?:{_H}:){{1,4}}(?::{_H}){{3}}"
        rf"|(?:{_H}:){{1,3}}(?::{_H}){{4}}"
        rf"|(?:{_H}:){{1,2}}(?::{_H}){{5}}"
        rf"|{_H}:(?::{_H}){{6}}"
        rf"|::(?:{_H}:){{0,6}}{_H}"  # starts with ::
        r"|::"  # all-zeros
        r")"
        r"(?![:\w])",
    )

    def validate(self, candidate: str) -> bool:
        try:
            ipaddress.IPv6Address(candidate)
            return True
        except ValueError:
            return False

    def normalize(self, candidate: str) -> str:
        try:
            return str(ipaddress.IPv6Address(candidate).compressed)
        except ValueError:
            return candidate


register(Ipv6Detector())
