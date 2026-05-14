from __future__ import annotations

import re

from stdnum.ie import pps as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.ie.pps: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ie.pps
# 7 digits + 1 check letter + optional 1 type letter (A/H/B for 2013+ format).
_STRIP = re.compile(r"[\s]")


class IePpsDetector(Detector):
    name = "ie_pps"
    token = "IE_PPS"
    region = "ie"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])\d{7}[A-W][ABHWTX]?(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(IePpsDetector())
