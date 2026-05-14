from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# MBI alphabet excludes S, L, O, I, B, Z to avoid digit/letter confusion.
# CMS spec: https://www.cms.gov/medicare/new-medicare-card/understanding-the-mbi.pdf
# Positions (1-indexed):
#   1, 4, 7, 10, 11 -> digit
#   2, 5, 8, 9      -> letter from restricted alphabet
#   3, 6            -> digit OR letter from restricted alphabet
_ALPHA = "ACDEFGHJKMNPQRTUVWXY"
_L = f"[{_ALPHA}]"
_AN = f"[{_ALPHA}0-9]"
_STRIP_RE = re.compile(r"[\s\-]")
_COMPACT_RE = re.compile(rf"^\d{_L}{_AN}\d{_L}{_AN}\d{_L}{_L}\d\d$")


class MbiDetector(Detector):
    name = "us_mbi"
    token = "US_MBI"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        rf"(?<![A-Za-z0-9])"
        rf"(?:"
        rf"\d{_L}{_AN}\d{_L}{_AN}\d{_L}{_L}\d\d"
        rf"|"
        rf"\d{_L}{_AN}\d-{_L}{_AN}\d-{_L}{_L}\d\d"
        rf")"
        rf"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        compact = _STRIP_RE.sub("", candidate).upper()
        return bool(_COMPACT_RE.match(compact))

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate).upper()


register(MbiDetector())
