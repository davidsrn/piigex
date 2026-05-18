from __future__ import annotations

import re

from stdnum.gb import utr as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class UtrDetector(Detector):
    # stdnum.gb.utr: mod-11 check digit at position 0 using weights
    # (6,7,8,9,10,5,4,3,2) over digits 1-9.
    name = "gb_utr"
    token = "GB_UTR"
    region = "gb"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])\d{10}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(UtrDetector())
