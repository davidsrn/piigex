from __future__ import annotations

import re

from stdnum.it import iva as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class PartitaIvaDetector(Detector):
    # stdnum.it.iva: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.it.iva
    # 11 digits: 7-digit company ID + 3-digit province code (001-100, 120, 121, 888, 999)
    # + 1 Luhn check digit.
    name = "it_partita_iva"
    token = "IT_IVA"
    region = "it"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{11}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(PartitaIvaDetector())
