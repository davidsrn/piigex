from __future__ import annotations

import re

from stdnum.bg import egn as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.bg.egn: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.bg.egn
# 10 digits: YYMMDD (month +20 for 1800s, +40 for 2000s) + 3-digit serial + check digit.
_STRIP = re.compile(r"[\s\-\.]")


class BgEgnDetector(Detector):
    name = "bg_egn"
    token = "BG_EGN"
    region = "bg"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(BgEgnDetector())
