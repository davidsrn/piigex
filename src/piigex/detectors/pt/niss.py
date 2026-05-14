from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP = re.compile(r"[\s\-]")


class NissDetector(Detector):
    # Número de Identificação de Segurança Social (NISS)
    # Spec: https://www.seg-social.pt/identificacao-e-inscricao-de-segurados
    # 11 digits; first digit encodes type: 1=worker, 2=pensioner, 5=foreigner, 6=company, 7/8=other.
    # Weights: [29,23,19,17,13,11,7,5,3,2] on first 10 digits.
    # Check: (10 - (sum % 10)) % 10
    # Note: algorithm sourced from secondary documentation; verify against official ISS spec.
    name = "pt_niss"
    token = "PT_NISS"
    region = "pt"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)[125678]\d{10}(?!\d)", re.ASCII)

    _WEIGHTS = (29, 23, 19, 17, 13, 11, 7, 5, 3, 2)

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate)
        if len(s) != 11 or not s.isdigit():
            return False
        total = sum(int(d) * w for d, w in zip(s[:10], self._WEIGHTS, strict=False))
        expected = (10 - (total % 10)) % 10
        return expected == int(s[10])

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(NissDetector())
