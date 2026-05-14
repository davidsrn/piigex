from __future__ import annotations

import re

from stdnum.gr import amka as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.gr.amka: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.gr.amka
# 11 digits: DDMMYY + 4-digit serial + 1 Luhn check digit.
_STRIP = re.compile(r"[\s\-]")


class GrAmkaDetector(Detector):
    name = "gr_amka"
    token = "GR_AMKA"
    region = "gr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{11}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(GrAmkaDetector())
