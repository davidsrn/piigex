from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP = re.compile(r"[\s\-]")


class SvnrDetector(Detector):
    # Sozialversicherungsnummer / Rentenversicherungsnummer
    # Spec: https://en.wikipedia.org/wiki/National_identification_number#Germany
    # 12 chars: area(2) + birthdate DDMMYY(6) + first-letter-of-surname(1) + serial(2) + check(1)
    # Weights: [2,1,2,5,7,1,2,1,2,1,2,1] applied after expanding the letter to its 2-digit value
    # (A=10, B=11, ..., Z=35). Products ≥10: sum their individual digits. check = total % 10.
    name = "de_svnr"
    token = "DE_SVNR"
    region = "de"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])\d{8}[A-Z]\d{3}(?![A-Za-z0-9])", re.ASCII)

    _WEIGHTS = (2, 1, 2, 5, 7, 1, 2, 1, 2, 1, 2, 1)

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate).upper()
        if len(s) != 12 or not s[:8].isdigit() or not s[8].isalpha() or not s[9:].isdigit():
            return False
        letter_val = ord(s[8]) - ord("A") + 10
        expanded = s[:8] + str(letter_val) + s[9:11]
        total = 0
        for d, w in zip(expanded, self._WEIGHTS, strict=False):
            p = int(d) * w
            total += p // 10 + p % 10
        return (total % 10) == int(s[11])

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(SvnrDetector())
