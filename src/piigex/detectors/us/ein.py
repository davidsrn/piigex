from __future__ import annotations

import re

from stdnum.us import ein as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class EinDetector(Detector):
    # stdnum.us.ein: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.us.ein
    # Nine digits, xx-xxxxxxx. First two digits restricted to IRS-assigned prefixes.
    # Hyphenated form only: compact 9 digits collides with us_rtn (and many EIN
    # prefixes also pass the ABA weighted checksum). Hyphenated form is the
    # IRS-canonical written form, so recall loss is minor.
    name = "us_ein"
    token = "US_EIN"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])\d{2}-\d{7}(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(EinDetector())
