from __future__ import annotations

import re

from stdnum.gb import vat as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class VatDetector(Detector):
    # stdnum.gb.vat: GB prefix required to avoid collision with fr_siren/us_rtn
    # on the 9-digit compact form. GD[0-4] = govt depts 000-499;
    # HA[5-9] = health authorities 500-999.
    name = "gb_vat"
    token = "GB_VAT"
    region = "gb"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"GB(?:\d{9}(?:\d{3})?|GD[0-4]\d{2}|HA[5-9]\d{2})"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(VatDetector())
