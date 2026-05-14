from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_PAIR = r"[0-9A-Fa-f]{2}"


class MacDetector(Detector):
    # MAC / EUI-48 hardware addresses.
    # https://en.wikipedia.org/wiki/MAC_address
    # Three common separator styles: colon (:), hyphen (-), or Cisco dot notation (.).
    name = "intl_mac"
    token = "MAC"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![0-9A-Fa-f:.\-])"
        r"(?:"
        rf"{_PAIR}:{_PAIR}:{_PAIR}:{_PAIR}:{_PAIR}:{_PAIR}"  # colon
        r"|"
        rf"{_PAIR}-{_PAIR}-{_PAIR}-{_PAIR}-{_PAIR}-{_PAIR}"  # hyphen
        r"|"
        r"[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}"  # Cisco dot
        r")"
        r"(?![0-9A-Fa-f:.\-])",
    )

    def validate(self, candidate: str) -> bool:
        normalized = re.sub(r"[:\-.]", "", candidate)
        return len(normalized) == 12 and all(c in "0123456789ABCDEFabcdef" for c in normalized)

    def normalize(self, candidate: str) -> str:
        return re.sub(r"[:\-.]", "", candidate).lower()


register(MacDetector())
