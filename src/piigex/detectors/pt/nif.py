from __future__ import annotations

import re

from stdnum.pt import nif as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class NifDetector(Detector):
    # stdnum.pt.nif: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pt.nif
    # 9 digits; first digit non-zero.
    # Check: (11 - sum(digit_i * (9-i) for i=0..7)) mod 11 mod 10
    name = "pt_nif"
    token = "PT_NIF"
    region = "pt"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[1-9]\d{8}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(NifDetector())
