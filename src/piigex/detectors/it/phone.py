from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_Italy
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+39|0039)")

_SEP = r"[ .\-]?"


class ItPhoneDetector(Detector):
    name = "it_phone"
    token = "IT_PHONE"
    region = "it"
    feasibility = "medium"
    default_enabled = False

    # Mobile: optional CC, then 3xx xxx xxxx (10 digits total, groups 3+3+4)
    # Fixed:  optional CC, then 0xx(x) yyy zzzz (area code 2-5 + subscriber, 9-11 total)
    pattern = re.compile(
        r"(?<![\w+])(?:(?:\+39|0039)" + _SEP + r")?"
        r"(?:"
        r"3\d{2}" + _SEP + r"\d{3}" + _SEP + r"\d{4}"  # mobile 3xx-xxx-xxxx (10)
        r"|0\d{1,4}" + _SEP + r"\d{3,4}" + _SEP + r"\d{3,4}"  # fixed
        r")(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        if not local:
            return False
        if local[0] == "3":
            return len(local) == 10
        if local[0] == "0":
            return 9 <= len(local) <= 11
        return False

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(ItPhoneDetector())
