from __future__ import annotations

import re

from stdnum.fi import ytunnus as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.fi.ytunnus: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fi.ytunnus
# 7 digits + hyphen + 1 check digit; e.g. 2077474-0.
_STRIP = re.compile(r"[\s]")


class FiYtunnusDetector(Detector):
    name = "fi_ytunnus"
    token = "FI_YTUNNUS"
    region = "fi"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{7}-\d(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(FiYtunnusDetector())
