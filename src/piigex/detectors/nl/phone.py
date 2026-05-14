from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_the_Netherlands
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+31|0031)")

_SEP = r"[ .\-]?"


class NlPhoneDetector(Detector):
    name = "nl_phone"
    token = "NL_PHONE"
    region = "nl"
    feasibility = "medium"
    default_enabled = False

    # Local: 0[1-9] followed by 8 more digits (10 total), with optional separators
    # International: +31/0031 then [1-9] followed by 8 more digits
    pattern = re.compile(
        r"(?<![\w+])(?:"
        r"(?:\+31|0031)" + _SEP + r"[1-9](?:" + _SEP + r"\d){8}"
        r"|0[1-9](?:" + _SEP + r"\d){8}"
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


register(NlPhoneDetector())
