from __future__ import annotations

import re

from stdnum.dk import cvr as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.dk.cvr: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.dk.cvr
# 8 digits: company register number; weighted mod-11 check.
_STRIP = re.compile(r"[\s\-]")


class DkCvrDetector(Detector):
    name = "dk_cvr"
    token = "DK_CVR"
    region = "dk"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{8}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(DkCvrDetector())
