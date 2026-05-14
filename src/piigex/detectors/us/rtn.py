from __future__ import annotations

import re

from stdnum.us import rtn as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class RtnDetector(Detector):
    # stdnum.us.rtn: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.us.rtn
    # ABA Routing Transit Number: 9 digits, weighted checksum (3*d1+7*d2+d3+...).
    name = "us_rtn"
    token = "US_RTN"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{9}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(RtnDetector())
