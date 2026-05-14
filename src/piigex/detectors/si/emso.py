from __future__ import annotations

import re

from stdnum.si import emso as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.si.emso: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.si.emso
# 13 digits: DDMMYYY (day+month+3-digit year) + 2-digit region + 3-digit serial + 1 check.
_STRIP = re.compile(r"[\s\-]")


class SiEmsoDetector(Detector):
    name = "si_emso"
    token = "SI_EMSO"
    region = "si"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{13}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(SiEmsoDetector())
