from __future__ import annotations

import re

from stdnum.fr import nir as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class NirDetector(Detector):
    # stdnum.fr.nir: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fr.nir
    # 15 chars: gender(1) + year(2) + month(2) + dept(2) + municipality(3) + serial(3) + check(2)
    # Dept is usually 2 digits (01-99); Corsica uses 2A or 2B (hence alphanumeric).
    # Check: 97 - (N mod 97), where 2A→19 and 2B→18 before the modulo.
    name = "fr_nir"
    token = "FR_NIR"
    region = "fr"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<!\d)"
        r"[1-478]"  # gender (1/2 standard; 3/4/7/8 exceptional)
        r"\d{2}"  # birth year
        r"(?:0[1-9]|1[0-2]|[2-9]\d)"  # birth month: 01-12 or 13-99 exceptional
        r"(?:\d{2}|2[AB])"  # dept: 01-99 or 2A/2B (Corsica)
        r"\d{3}"  # municipality
        r"\d{3}"  # serial
        r"\d{2}"  # check
        r"(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(NirDetector())
