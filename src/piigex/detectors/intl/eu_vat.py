from __future__ import annotations

import re

from stdnum.eu import vat as _stdnum_eu_vat

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.eu.vat: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.eu.vat
# Prefixes: AT(ATU), BE, BG, CY, CZ, DE, DK, EE, EL(GR), ES, FI, FR, HR, HU, IE,
# IT, LT, LU, LV, MT, NL, PL, PT, RO, SE, SI, SK; also XI (Northern Ireland).
_PREFIXES = "ATU|BE|BG|CY|CZ|DE|DK|EE|EL|ES|FI|FR|HR|HU|IE|IT|LT|LU|LV|MT|NL|PL|PT|RO|SE|SI|SK|XI"


class EuVatDetector(Detector):
    name = "intl_eu_vat"
    token = "EU_VAT"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        rf"(?:{_PREFIXES})"
        r"[A-Z0-9]{2,15}"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum_eu_vat.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        try:
            return str(_stdnum_eu_vat.compact(candidate))
        except Exception:
            return candidate.replace(" ", "").replace(".", "").replace("-", "").upper()


register(EuVatDetector())
