from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_France
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+33|0033)")


class FrPhoneDetector(Detector):
    name = "fr_phone"
    token = "FR_PHONE"
    region = "fr"
    feasibility = "medium"
    default_enabled = False

    # Local: 0[1-9] then 8 more digits, pairs separated by optional space/dot/dash
    # International: +33 or 0033 then [1-9] then 8 more digits
    pattern = re.compile(
        r"(?<![\w+])(?:"
        r"(?:(?:\+33|0033)[ .\-]?[1-9]|\b0[1-9])"
        r"(?:[ .\-]?\d{2}){4}"
        r")(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        if local.startswith("0"):
            local = local[1:]
        return len(local) == 9 and local[0] in "123456789"

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(FrPhoneDetector())
