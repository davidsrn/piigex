from __future__ import annotations

import re

from stdnum.it import codicefiscale as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class CodiceFiscaleDetector(Detector):
    # stdnum.it.codicefiscale: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.it.codicefiscale
    # 16 chars: 3 surname + 3 name letters + 2-digit year + 1 month letter +
    # 2-digit day (+40 for female) + 4-char municipality code + 1 check letter.
    # Month letters: A=Jan, B=Feb, C=Mar, D=Apr, E=May, H=Jun,
    #                L=Jul, M=Aug, P=Sep, R=Oct, S=Nov, T=Dec
    name = "it_codice_fiscale"
    token = "IT_CF"
    region = "it"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(CodiceFiscaleDetector())
