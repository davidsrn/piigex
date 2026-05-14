from __future__ import annotations

import re

from stdnum.se import orgnr as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.se.orgnr: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.se.orgnr
# 10 digits (Luhn check); formatted as XXXXXX-XXXX.
_STRIP = re.compile(r"[\s\-]")


class SeOrgnrDetector(Detector):
    name = "se_orgnr"
    token = "SE_ORGNR"
    region = "se"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{6}-\d{4}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(SeOrgnrDetector())
