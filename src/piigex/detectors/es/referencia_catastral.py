from __future__ import annotations

import re

from stdnum.es import referenciacatastral as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class ReferenciaCatastralDetector(Detector):
    # stdnum.es.referenciacatastral: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.es.referenciacatastral
    # 20 alphanumeric chars (may include Ñ, U+00D1): groups 7+7+4+2.
    # Last 2 chars are check characters via weighted-position lookup mod-23 alphabet.
    # Note: re.ASCII restricts \w etc. but explicit Ñ still matches as a literal.
    name = "es_referencia_catastral"
    token = "ES_CATASTRO"
    region = "es"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9Ñ])"
        r"[0-9A-ZÑ]{7}[0-9A-ZÑ]{7}[0-9A-Z]{4}[A-Z]{2}"
        r"(?![A-Za-z0-9Ñ])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(ReferenciaCatastralDetector())
