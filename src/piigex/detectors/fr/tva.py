from __future__ import annotations

import re

from stdnum.fr import tva as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class TvaDetector(Detector):
    # stdnum.fr.tva: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fr.tva
    # FR + 2-char key (alphanumeric, excluding I and O) + 9-digit SIREN; 13 chars with prefix.
    # Key can be two digits (old) or two letters/digits (new alphanumeric format).
    name = "fr_tva"
    token = "FR_TVA"
    region = "fr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])FR[A-HJ-NP-Z0-9]{2}\d{9}(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(TvaDetector())
