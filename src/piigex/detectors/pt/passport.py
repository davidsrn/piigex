from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# Portuguese passport: 2 letters + 6 digits; 8 chars total. No checksum.
# Spec: https://en.wikipedia.org/wiki/Portuguese_passport
_STRIP = re.compile(r"[\s\-]")
_FULL = re.compile(r"[A-Z]{2}\d{6}", re.ASCII)


class PtPassportDetector(Detector):
    name = "pt_passport"
    token = "PT_PASSPORT"
    region = "pt"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}\d{6}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate).upper()
        return bool(_FULL.fullmatch(s))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(PtPassportDetector())
