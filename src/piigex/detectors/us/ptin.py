from __future__ import annotations

import re

from stdnum.us import ptin as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class PtinDetector(Detector):
    # stdnum.us.ptin: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.us.ptin
    # Preparer Tax Identification Number: literal "P" + 8 digits.
    name = "us_ptin"
    token = "US_PTIN"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])P\d{8}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(PtinDetector())
