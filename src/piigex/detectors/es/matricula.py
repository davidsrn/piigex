from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# Spanish vehicle plate (post-2000): 4 digits + 3 consonant letters.
# Consonants used: BCDFGHJKLMNPRSTVWXYZ (vowels AEIOU and Q excluded).
# Spec: https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Spain
_STRIP = re.compile(r"[\s\-]")
_CONSONANTS = "BCDFGHJKLMNPRSTVWXYZ"
_FULL = re.compile(rf"[0-9]{{4}}[{_CONSONANTS}]{{3}}", re.ASCII)


class EsMatriculaDetector(Detector):
    name = "es_matricula"
    token = "ES_MATRICULA"
    region = "es"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(
        rf"(?<![A-Za-z0-9])\d{{4}}[\s\-]?[{_CONSONANTS}]{{3}}(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate).upper()
        return bool(_FULL.fullmatch(s))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(EsMatriculaDetector())
