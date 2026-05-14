from __future__ import annotations

import re

from stdnum.hr import oib as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.hr.oib: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.hr.oib
# 11 digits: 10-digit base + 1 check digit (ISO 7064 mod-11-10).
_STRIP = re.compile(r"[\s\-]")


class HrOibDetector(Detector):
    name = "hr_oib"
    token = "HR_OIB"
    region = "hr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{11}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(HrOibDetector())
