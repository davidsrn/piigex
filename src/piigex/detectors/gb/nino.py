from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_RESERVED = frozenset({"BG", "GB", "KN", "NK", "NT", "TN", "ZZ"})


class NinoDetector(Detector):
    # No stdnum module exists for NINO. Validation is structural only.
    # First letter excludes D,F,I,Q,U,V; second also excludes O.
    # Reserved prefixes are rejected in validate() because they fall within
    # the allowed character classes.
    name = "gb_nino"
    token = "GB_NINO"
    region = "gb"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-CEG-HJ-NOPR-TW-Z][A-CEG-HJ-NPR-TW-Z]"
        r" ?\d{2} ?\d{2} ?\d{2} ?[A-D]"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return candidate.replace(" ", "").upper()[:2] not in _RESERVED

    def normalize(self, candidate: str) -> str:
        return candidate.replace(" ", "").upper()


register(NinoDetector())
