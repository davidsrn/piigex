from __future__ import annotations

import re

from stdnum.pl import pesel as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.pl.pesel: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pl.pesel
# 11 digits: 6-digit birthdate + 4-digit serial + 1 weighted check digit.
_STRIP = re.compile(r"[\s\-]")


class PlPeselDetector(Detector):
    name = "pl_pesel"
    token = "PL_PESEL"
    region = "pl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{11}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(PlPeselDetector())
