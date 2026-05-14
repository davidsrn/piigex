from __future__ import annotations

import re

from stdnum.dk import cpr as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.dk.cpr: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.dk.cpr
# 10 digits: DDMMYY + 4-digit serial (last digit is check via mod-11 for pre-2007).
# Optional hyphen between date and serial parts.
_STRIP = re.compile(r"[\s\-]")


class DkCprDetector(Detector):
    name = "dk_cpr"
    token = "DK_CPR"
    region = "dk"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{6}-?\d{4}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(DkCprDetector())
