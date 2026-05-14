from __future__ import annotations

import re

from stdnum.us import ssn as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class SsnDetector(Detector):
    # stdnum.us.ssn: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.us.ssn
    # Nine digits, xxx-xx-xxxx. Area excludes 000/666/9xx; group excludes 00;
    # serial excludes 0000. Promotional and reserved numbers also rejected.
    name = "us_ssn"
    token = "US_SSN"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])(?:\d{3}-\d{2}-\d{4}|\d{9})(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(SsnDetector())
