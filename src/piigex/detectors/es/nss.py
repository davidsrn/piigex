from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP = re.compile(r"[\s/.]")


class NssDetector(Detector):
    # Número de Afiliación a la Seguridad Social (NAF / NSS)
    # Spec: https://www.seg-social.es/wps/portal/wss/internet/Ciudadanos/Afiliacion/10817/10819
    # Format: PP NNNNNNN[N] CC  (2-digit province + 7-8 digit affiliation + 2-digit control)
    # Checksum: (province * 10_000_000 + affiliation) % 97  if affiliation < 10_000_000
    #           int(str(province) + str(affiliation)) % 97   otherwise
    name = "es_nss"
    token = "ES_NSS"
    region = "es"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{2}[/ ]?\d{7,8}[/ ]?\d{2}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate)
        if not s.isdigit() or len(s) not in (11, 12):
            return False
        province = int(s[:2])
        if len(s) == 11:
            affiliation, control = int(s[2:9]), int(s[9:11])
        else:
            affiliation, control = int(s[2:10]), int(s[10:12])
        if affiliation < 10_000_000:
            expected = (province * 10_000_000 + affiliation) % 97
        else:
            expected = int(f"{province:02d}{affiliation}") % 97
        return control == expected

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(NssDetector())
