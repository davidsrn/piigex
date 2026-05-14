from __future__ import annotations

import re

from stdnum.nl import btw as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class BtwDetector(Detector):
    # stdnum.nl.btw: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.nl.btw
    # NL + 9-digit RSIN + B + 2-digit entity code; e.g. NL123456789B01
    name = "nl_btw"
    token = "NL_BTW"
    region = "nl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])NL\d{9}B\d{2}(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(BtwDetector())
