from __future__ import annotations

import re

from stdnum.pl import nip as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.pl.nip: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.pl.nip
# 10-digit tax identification number; weighted mod-11 check.
_STRIP = re.compile(r"[\s\-]")


class PlNipDetector(Detector):
    name = "pl_nip"
    token = "PL_NIP"
    region = "pl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{10}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(PlNipDetector())
