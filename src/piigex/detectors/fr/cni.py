from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# French national ID card: new CNIF format (2021+) only.
# Format: 1 digit + 2 letters + 6 alphanumeric chars (I and O excluded); 9 chars.
# Old 12-digit format is too ambiguous to detect reliably. Not implemented.
# Spec: https://www.service-public.fr/particuliers/vosdroits/F1399
_STRIP = re.compile(r"[\s\-]")
_ALPHA = "A-HJ-NP-Z"  # letters excluding I and O
_FULL = re.compile(rf"[0-9][A-Z]{{2}}[0-9{_ALPHA}]{{6}}", re.ASCII)


class FrCniDetector(Detector):
    name = "fr_cni"
    token = "FR_CNI"
    region = "fr"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(
        r"(?<![A-Za-z0-9])[0-9][A-Z]{2}[0-9A-HJ-NP-Z]{6}(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        s = _STRIP.sub("", candidate).upper()
        return bool(_FULL.fullmatch(s))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(FrCniDetector())
