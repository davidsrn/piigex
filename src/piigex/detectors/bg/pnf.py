from __future__ import annotations

import re

from stdnum.bg import pnf as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.bg.pnf: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.bg.pnf
# 10 digits: personal number for foreigners; weighted checksum mod 10.
_STRIP = re.compile(r"[\s\-\.]")


class BgPnfDetector(Detector):
    name = "bg_pnf"
    token = "BG_PNF"
    region = "bg"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(BgPnfDetector())
