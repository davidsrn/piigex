from __future__ import annotations

import re

from stdnum.at import vnr as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.at.vnr: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.at.vnr
# 10 digits: 3-digit serial + 1 check digit + 6-digit birthdate (DDMMYY).
_STRIP = re.compile(r"[\s]")


class AtVnrDetector(Detector):
    name = "at_vnr"
    token = "AT_VNR"
    region = "at"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{4}[ ]?\d{6}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(AtVnrDetector())
