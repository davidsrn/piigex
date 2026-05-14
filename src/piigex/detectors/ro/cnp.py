from __future__ import annotations

import re

from stdnum.ro import cnp as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.ro.cnp: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ro.cnp
# 13 digits: 1-digit gender/century + 6-digit birthdate + 2-digit county + 3-digit serial + 1 check.
_STRIP = re.compile(r"[\s\-]")


class RoCnpDetector(Detector):
    name = "ro_cnp"
    token = "RO_CNP"
    region = "ro"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[1-9]\d{12}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(RoCnpDetector())
