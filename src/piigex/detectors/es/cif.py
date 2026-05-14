from __future__ import annotations

import re

from stdnum.es import cif as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class CifDetector(Detector):
    # stdnum.es.cif: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.es.cif
    # First letter: A-H, J, N, P-U, V, W (never I, K, L, M, O, X, Y, Z).
    # Check char: digit 0-9 or letter A-J (both encode the same 0-9 value).
    name = "es_cif"
    token = "ES_CIF"
    region = "es"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])[A-HJNP-UVW]\d{7}[\dA-J](?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(CifDetector())
