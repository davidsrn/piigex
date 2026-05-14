from __future__ import annotations

import re

from stdnum.pt import cc as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class CcDetector(Detector):
    # stdnum.pt.cc: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pt.cc
    # Cartão de Cidadão: 12 alphanumeric: 8 civil-ID digits + 1 digit + 2-letter version + 1 check.
    # Check: right-to-left, even positions × 2 (subtract 9 if >9), sum mod 10 == 0.
    name = "pt_cc"
    token = "PT_CC"
    region = "pt"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])\d{9}[A-Z]{2}\d(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(CcDetector())
