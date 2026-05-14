from __future__ import annotations

import re

from stdnum.se import personnummer as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.se.personnummer: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.se.personnummer
# 10 or 12 digits with optional hyphen/plus separator; format: YYMMDD-NNNN or YYYYMMDD-NNNN.
# Luhn check digit on last 4 digits applied to 9-digit base.
_STRIP = re.compile(r"[\s]")


class SePersonnummerDetector(Detector):
    name = "se_personnummer"
    token = "SE_PERSONNUMMER"
    region = "se"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<!\d)\d{6}[-+]\d{4}(?!\d)"
        r"|"
        r"(?<!\d)\d{8}[-+]\d{4}(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(SePersonnummerDetector())
