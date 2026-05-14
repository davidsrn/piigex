from __future__ import annotations

import re

from stdnum.be import eid as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class EidDetector(Detector):
    # stdnum.be.eid: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.be.eid
    # Belgian eID card number: 12 digits; last 2 = first_10 mod 97 (if 0 → 97).
    name = "be_eid"
    token = "BE_EID"
    region = "be"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{12}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(EidDetector())
