from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)"


class Ipv4Detector(Detector):
    # IPv4 addresses per RFC 791. https://tools.ietf.org/html/rfc791
    name = "intl_ipv4"
    token = "IPV4"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        rf"(?<![.\d]){_OCTET}\.{_OCTET}\.{_OCTET}\.{_OCTET}(?![.\d])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        parts = candidate.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def normalize(self, candidate: str) -> str:
        return candidate


register(Ipv4Detector())
