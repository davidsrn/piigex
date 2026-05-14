from __future__ import annotations

import re

from stdnum import bic as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class BicDetector(Detector):
    # stdnum.bic: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.bic
    # ISO 9362: 4-letter institution + 2-letter country + 2-char location + optional 3-char branch.
    # 8 or 11 alphanumeric characters.
    name = "intl_bic"
    token = "BIC"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(BicDetector())
