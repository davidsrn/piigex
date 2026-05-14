from __future__ import annotations

import re

from stdnum.es import nie as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class NieDetector(Detector):
    # stdnum.es.nie: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.es.nie
    # Covers both NIE (number) and TIE (card): same format, same algorithm.
    # Algorithm: replace X→0, Y→1, Z→2, then apply DNI mod-23 check.
    name = "es_nie"
    token = "ES_NIE"
    region = "es"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])[XYZ]\d{7}[A-Z](?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(NieDetector())
