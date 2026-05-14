from __future__ import annotations

import re

from stdnum.fr import siren as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class SirenDetector(Detector):
    # stdnum.fr.siren: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fr.siren
    # 9 digits; Luhn check digit.
    name = "fr_siren"
    token = "FR_SIREN"
    region = "fr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{9}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(SirenDetector())
