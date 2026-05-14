from __future__ import annotations

# https://www.itu.int/rec/T-REC-E.164/
import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP_RE = re.compile(r"[ .\-()]")


class PhoneE164Detector(Detector):
    name = "intl_phone_e164"
    token = "INTL_PHONE_E164"
    region = "intl"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(
        r"(?<![\w+])\+[1-9]\d{0,2}(?:[ .\-()]*\d){6,14}(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        digits = _STRIP_RE.sub("", candidate)
        if not digits.startswith("+"):
            return False
        digits = digits[1:]
        return len(digits) >= 7 and len(digits) <= 15 and digits[0] in "123456789"

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate.lower())


register(PhoneE164Detector())
