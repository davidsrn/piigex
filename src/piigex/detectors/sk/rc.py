from __future__ import annotations

import re

from stdnum.sk import rc as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.sk.rc: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.sk.rc
# Slovak birth number (rodné číslo): 9 or 10 digits YYMMDD + 3-digit serial + optional check.
# Identical structure to CZ RC; optional slash separator.
_STRIP = re.compile(r"[\s/]")


class SkRcDetector(Detector):
    name = "sk_rc"
    token = "SK_RC"
    region = "sk"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{6}/?[\d]{3,4}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(SkRcDetector())
