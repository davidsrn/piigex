from __future__ import annotations

import re

from stdnum.be import ogm_vcs as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.be.ogm_vcs: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.be.ogm_vcs
# Format: +++NNN/NNNN/NNNNN+++ (12 digits total, mod-97 check on first 10).
# Delimiters required to avoid false positives on bare 12-digit sequences.
_STRIP = re.compile(r"[\s+/]")


class BeOgmVcsDetector(Detector):
    name = "be_ogm_vcs_delimited"
    token = "BE_OGM_VCS"
    region = "be"
    feasibility = "medium"
    default_enabled = False

    pattern = re.compile(
        r"(?<![A-Za-z0-9+])"
        r"\+{3}\d{3}/\d{4}/\d{5}\+{3}"
        r"(?![A-Za-z0-9+])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(BeOgmVcsDetector())
