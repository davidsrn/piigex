from __future__ import annotations

import re

from stdnum.cz import rc as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.cz.rc: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.cz.rc
# 9 or 10 digits (post-1954: 10 digits divisible by 11); YYMMDD + 3-digit serial + optional check.
# Optional slash separator between date and serial parts.
_STRIP = re.compile(r"[\s/]")


class CzRcDetector(Detector):
    name = "cz_rc"
    token = "CZ_RC"
    region = "cz"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{6}/?[\d]{3,4}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(CzRcDetector())
