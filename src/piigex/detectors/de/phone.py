from __future__ import annotations

# https://en.wikipedia.org/wiki/Telephone_numbers_in_Germany
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")
_CC_RE = re.compile(r"^(?:\+49|0049)")

_SEP = r"[ .\-]?"


class DePhoneDetector(Detector):
    name = "de_phone"
    token = "DE_PHONE"
    region = "de"
    feasibility = "medium"
    default_enabled = False

    # +49/0049 optional prefix, then trunk 0 + area (2-5 digits) + subscriber (3-8 digits)
    # Allow up to 3 separator groups in subscriber number
    pattern = re.compile(
        r"(?<![\w+])(?:(?:\+49|0049)" + _SEP + r"|(?<!\d)0)"
        r"\d{2,5}" + _SEP + r"\d{2,4}(?:" + _SEP + r"\d{2,4}){0,2}(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        stripped = _STRIP_RE.sub("", candidate)
        local = _CC_RE.sub("", stripped)
        if local.startswith("0"):
            local = local[1:]
        return 6 <= len(local) <= 13

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(DePhoneDetector())
