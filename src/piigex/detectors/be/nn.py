from __future__ import annotations

import re

from stdnum.be import nn as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class NnDetector(Detector):
    # stdnum.be.nn: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.be.nn
    # Rijksregisternummer / Numéro de registre national
    # 11 digits: YYMMDD(6) + 3-digit counter + 2-digit check (97 - first_9 mod 97).
    # Post-2000: century ambiguity resolved by prepending "2" before modulo.
    name = "be_nn"
    token = "BE_NN"
    region = "be"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{11}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(NnDetector())
