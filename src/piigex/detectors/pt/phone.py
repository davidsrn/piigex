from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_Portugal
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+351|00351)")


class PtPhoneDetector(Detector):
    name = "pt_phone"
    token = "PT_PHONE"
    region = "pt"
    feasibility = "medium"
    default_enabled = False

    # 9 digits starting with 2 (fixed) or 9 (mobile); optional +351/00351 prefix
    # Two grouping variants: 3+3+3 (9xx xxx xxx) or 2+3+4 (21 xxx xxxx)
    pattern = re.compile(
        r"(?<![\w+])(?:(?:\+351|00351)[ .\-]?)?"
        r"(?:[29]\d{2}[ .\-]?\d{3}[ .\-]?\d{3}"
        r"|[29]\d[ .\-]?\d{3}[ .\-]?\d{4})(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        return len(local) == 9 and local[0] in "29"

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(PtPhoneDetector())
