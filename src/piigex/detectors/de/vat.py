from __future__ import annotations

import re

from stdnum.de import vat as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class VatDetector(Detector):
    # stdnum.de.vat: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.de.vat
    # DE + 9 digits; mod-11-10 check digit.
    name = "de_vat"
    token = "DE_VAT"
    region = "de"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])DE\d{9}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(VatDetector())
