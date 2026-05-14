from __future__ import annotations

import re

from stdnum.de import idnr as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class IdnrDetector(Detector):
    # stdnum.de.idnr: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.de.idnr
    # 11 digits; first digit 1-9; within first 10 digits exactly one digit repeats
    # 2-3 times and all others appear exactly once; ISO 7064 mod-11-10 check.
    name = "de_idnr"
    token = "DE_IDNR"
    region = "de"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[1-9]\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(IdnrDetector())
