from __future__ import annotations

import re

from stdnum.es import dni as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class DniDetector(Detector):
    # stdnum.es.dni: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.es.dni
    # Algorithm: int(first_8) % 23, index into TRWAGMYFPDXBNJZSQVHLCKE
    name = "es_dni"
    token = "ES_DNI"
    region = "es"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])\d{8}[A-Z](?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(DniDetector())
