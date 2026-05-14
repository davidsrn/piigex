from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_Belgium
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+32|0032)")

_SEP = r"[ .\-]?"


class BePhoneDetector(Detector):
    name = "be_phone"
    token = "BE_PHONE"
    region = "be"
    feasibility = "medium"
    default_enabled = False

    # Mobile: 04xx = 0 + 4 + 8 more digits = 10 total
    # Fixed: 0[1-9] + 7-8 more digits = 9-10 total
    # International: +32/0032 then [1-9] + 7-8 more digits (no leading 0)
    pattern = re.compile(
        r"(?<![\w+])(?:"
        r"(?:\+32|0032)" + _SEP + r"[1-9](?:" + _SEP + r"\d){7,8}"
        r"|0[1-9](?:" + _SEP + r"\d){7,8}"
        r")(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        if local.startswith("0"):
            local = local[1:]
        return len(local) in (8, 9) and local[0] in "123456789"

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(BePhoneDetector())
