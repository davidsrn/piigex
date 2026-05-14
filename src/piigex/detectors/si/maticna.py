from __future__ import annotations

import re

from stdnum.si import maticna as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.si.maticna: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.si.maticna
# 7 or 10 digits: 6-digit base + check digit (+ optional 3-digit unit suffix).
_STRIP = re.compile(r"[\s\.]")


class SiMaticnaDetector(Detector):
    name = "si_maticna"
    token = "SI_MATICNA"
    region = "si"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{7}(?:\d{3})?(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(SiMaticnaDetector())
