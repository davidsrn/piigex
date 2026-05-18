from __future__ import annotations

import re

from stdnum import luhn

from piigex.detectors import register
from piigex.detectors.base import Detector

# NPI: 10 digits. Luhn-checksum over the ISO 7812 issuer prefix "80840" + first 9
# digits == last (10th) digit. https://www.cms.gov/Regulations-and-Guidance/Administrative-Simplification/NationalProvIdentStand
_DIGITS_RE = re.compile(r"\D")


class NpiDetector(Detector):
    name = "us_npi"
    token = "US_NPI"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        digits = _DIGITS_RE.sub("", candidate)
        if len(digits) != 10:
            return False
        return bool(luhn.is_valid("80840" + digits))

    def normalize(self, candidate: str) -> str:
        return _DIGITS_RE.sub("", candidate)


register(NpiDetector())
