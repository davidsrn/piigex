from __future__ import annotations

import re

from stdnum.lt import asmens as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.lt.asmens: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.lt.asmens
# 11 digits: 1-digit gender/century + 6-digit birthdate + 3-digit serial + 1 check.
_STRIP = re.compile(r"[\s\-]")


class LtAsmensDetector(Detector):
    name = "lt_asmens"
    token = "LT_ASMENS"
    region = "lt"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[1-6]\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(LtAsmensDetector())
