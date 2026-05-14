from __future__ import annotations

import re

from stdnum.ro import cf as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.ro.cf: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.ro.cf
# Romanian VAT/tax number: optional RO prefix + 2-10 digits. Delegates to CUI/CNP.
# Regex requires RO prefix to disambiguate from bare digit strings.
_STRIP = re.compile(r"[\s]")


class RoCfDetector(Detector):
    name = "ro_cf"
    token = "RO_CF"
    region = "ro"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<![A-Za-z0-9])RO\d{2,10}(?![A-Za-z0-9])", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(RoCfDetector())
