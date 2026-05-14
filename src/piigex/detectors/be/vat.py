from __future__ import annotations

import re

from stdnum.be import vat as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class VatDetector(Detector):
    # stdnum.be.vat: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.be.vat
    # BTW/TVA enterprise number: optional "BE" prefix + 10 digits, first digit 0 or 1.
    # Check: (first_8 + last_2) mod 97 == 0.
    name = "be_vat"
    token = "BE_VAT"
    region = "be"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"(?:BE[ ]?)?"  # optional country prefix
        r"[01]\d{9}"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(VatDetector())
