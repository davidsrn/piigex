from __future__ import annotations

import re

from stdnum.nl import identiteitskaartnummer as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.nl.identiteitskaartnummer: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.nl.identiteitskaartnummer
# 9 chars: 2 letters + 6 alphanumeric + 1 digit; letter O excluded from all positions.
_STRIP = re.compile(r"[\s]")


class NlPassportDetector(Detector):
    name = "nl_passport"
    token = "NL_PASSPORT"
    region = "nl"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(
        r"(?<![A-Za-z0-9])[A-NP-Z]{2}[0-9A-NP-Z]{6}[0-9](?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(NlPassportDetector())
