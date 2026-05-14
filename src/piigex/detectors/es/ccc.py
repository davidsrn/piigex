from __future__ import annotations

import re

from stdnum.es import ccc as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class CccDetector(Detector):
    # stdnum.es.ccc: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.es.ccc
    # Format: EEEE OOOO DD NNNNNNNNNN  (4-digit bank + 4-digit branch + 2 check + 10 account)
    # Two mod-11 check digits using powers-of-2 weighting.
    name = "es_ccc"
    token = "ES_CCC"
    region = "es"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{2}[ -]?\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(CccDetector())
