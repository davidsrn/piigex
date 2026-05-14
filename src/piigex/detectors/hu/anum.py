from __future__ import annotations

import re

from stdnum.hu import anum as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.hu.anum: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.hu.anum
# 8-digit taxpayer registration number with weighted checksum. Optional HU prefix.
_STRIP = re.compile(r"[\s\-]")


class HuAnumDetector(Detector):
    name = "hu_anum"
    token = "HU_ANUM"
    region = "hu"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])\d{8}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(HuAnumDetector())
