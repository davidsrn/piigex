from __future__ import annotations

# https://en.wikipedia.org/wiki/North_American_Numbering_Plan
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+1|1|001)")


class UsPhoneDetector(Detector):
    name = "us_phone"
    token = "US_PHONE"
    region = "us"
    feasibility = "medium"
    default_enabled = False

    # NANP: optional +1/1/001 country prefix, then area code [2-9]NN, exchange
    # [2-9]NN, subscriber NNNN. Separators are optional space/dot/dash, and the
    # area code may be wrapped in parens.
    pattern = re.compile(
        r"(?<![\w+])(?:"
        r"(?:\+1|001)[ .\-]?\(?[2-9]\d{2}\)?[ .\-]?[2-9]\d{2}[ .\-]?\d{4}"
        r"|"
        r"1[ .\-]\(?[2-9]\d{2}\)?[ .\-]?[2-9]\d{2}[ .\-]?\d{4}"
        r"|"
        r"\(?[2-9]\d{2}\)?[ .\-]?[2-9]\d{2}[ .\-]?\d{4}"
        r")(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        return len(local) == 10 and local[0] in "23456789" and local[3] in "23456789"

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(UsPhoneDetector())
