from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# DEA registration number: 2 letters + 7 digits. https://en.wikipedia.org/wiki/DEA_number
# Checksum: last digit of (d1+d3+d5 + 2*(d2+d4+d6)) must equal d7.


class DeaDetector(Detector):
    name = "us_dea"
    token = "US_DEA"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}\d{7}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        m = re.fullmatch(r"[A-Z]{2}(\d{6})(\d)", candidate)
        if not m:
            return False
        d = m.group(1)
        check = m.group(2)
        odd = int(d[0]) + int(d[2]) + int(d[4])
        even = int(d[1]) + int(d[3]) + int(d[5])
        return (odd + 2 * even) % 10 == int(check)

    def normalize(self, candidate: str) -> str:
        return candidate.upper()


register(DeaDetector())
