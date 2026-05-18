from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# US passport book/card numbers since ~2007: 1 letter + 8 digits. No checksum.
# The pre-2007 9-digit format is intentionally not matched because it overlaps
# with SSN/EIN/RTN compact forms and would generate false positives. `P` is
# excluded from the leading letter to avoid colliding with `us_ptin` (P + 8 digits).
_STRIP = re.compile(r"[\s\-]")
_FULL = re.compile(r"[A-OQ-Z]\d{8}", re.ASCII)


class UsPassportDetector(Detector):
    name = "us_passport"
    token = "US_PASSPORT"
    region = "us"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(r"(?<![A-Za-z0-9])[A-OQ-Z]\d{8}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate).upper()
        return bool(_FULL.fullmatch(s))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(UsPassportDetector())
