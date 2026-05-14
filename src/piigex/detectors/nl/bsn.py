from __future__ import annotations

import re

from stdnum.nl import bsn as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class BsnDetector(Detector):
    # stdnum.nl.bsn: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.nl.bsn
    # 9 digits; elfproef: sum((9-i)*d[i] for i=0..7) - d[8] ≡ 0 (mod 11).
    name = "nl_bsn"
    token = "NL_BSN"
    region = "nl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{9}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(BsnDetector())
