from __future__ import annotations

import re

from stdnum.fr import siret as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class SiretDetector(Detector):
    # stdnum.fr.siret: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fr.siret
    # 14 digits = 9-digit SIREN + 5-digit NIC; Luhn check on full 14 digits.
    name = "fr_siret"
    token = "FR_SIRET"
    region = "fr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{14}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(SiretDetector())
