from __future__ import annotations

import re

from stdnum.fr import nif as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class NifDetector(Detector):
    # stdnum.fr.nif: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fr.nif
    # 13 digits; first digit 0-3; last 3 digits = first 10 digits mod 511.
    name = "fr_nif"
    token = "FR_NIF"
    region = "fr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[0-3]\d{12}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(NifDetector())
