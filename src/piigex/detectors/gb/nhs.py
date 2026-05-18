from __future__ import annotations

import re

from stdnum.gb import nhs as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class NhsDetector(Detector):
    # stdnum.gb.nhs: weighted mod-11 checksum over 9 leading digits.
    name = "gb_nhs"
    token = "GB_NHS"
    region = "gb"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])\d{10}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(NhsDetector())
