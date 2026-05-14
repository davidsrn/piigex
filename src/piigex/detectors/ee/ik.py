from __future__ import annotations

import re

from stdnum.ee import ik as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.ee.ik: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ee.ik
# 11 digits: 1-digit gender/century + 6-digit birthdate + 3-digit serial + 1 check.
_STRIP = re.compile(r"[\s\-]")


class EeIkDetector(Detector):
    name = "ee_ik"
    token = "EE_IK"
    region = "ee"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[1-6]\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(EeIkDetector())
