from __future__ import annotations

import re

from stdnum.us import itin as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class ItinDetector(Detector):
    # stdnum.us.itin: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.us.itin
    # Nine digits, 9xx-xx-xxxx. Middle group restricted to 70-99 excluding 89 and 93
    # (93 is reserved for ATIN).
    name = "us_itin"
    token = "US_ITIN"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])(?:9\d{2}-\d{2}-\d{4}|9\d{8})(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(ItinDetector())
