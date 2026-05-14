from __future__ import annotations

import re

from stdnum.pl import regon as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.pl.regon: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pl.regon
# 9 or 14 digits: statistical company register number; weighted mod-11 check.
_STRIP = re.compile(r"[\s\-]")


class PlRegonDetector(Detector):
    name = "pl_regon"
    token = "PL_REGON"
    region = "pl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{9}(?!\d)|\d{14}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(PlRegonDetector())
