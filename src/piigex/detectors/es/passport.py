from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# Spanish passport: 3 letters + 6 digits; 9 chars.
# Spec: https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/tramites-y-gestiones/dni-y-pasaporte/pasaporte/
_STRIP = re.compile(r"[\s\-]")


class EsPassportDetector(Detector):
    name = "es_passport"
    token = "ES_PASSPORT"
    region = "es"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(r"(?<![A-Za-z0-9])[A-Z]{3}\d{6}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate).upper()
        return bool(re.fullmatch(r"[A-Z]{3}\d{6}", s))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(EsPassportDetector())
