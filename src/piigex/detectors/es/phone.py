from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_Spain
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+34|0034)")


class EsPhoneDetector(Detector):
    name = "es_phone"
    token = "ES_PHONE"
    region = "es"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(
        r"(?<![\w+])(?:(?:\+34|0034)[ .\-]?)?[6-9]\d{2}[ .\-]?\d{3}[ .\-]?\d{3}(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        return len(local) == 9 and local[0] in "6789"

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(EsPhoneDetector())
