from __future__ import annotations

import re

from stdnum.cz import dic as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.cz.dic: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.cz.dic
# Tax identification number: CZ + 8-10 digits.
_STRIP = re.compile(r"[\s]")


class CzDicDetector(Detector):
    name = "cz_dic"
    token = "CZ_DIC"
    region = "cz"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])CZ\d{8,10}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(CzDicDetector())
