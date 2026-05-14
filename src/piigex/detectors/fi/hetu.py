from __future__ import annotations

import re

from stdnum.fi import hetu as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.fi.hetu: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.fi.hetu
# Format: DDMMYY + century marker (-, +, or letter A-Y) + 3-digit serial + 1 check char.
_STRIP = re.compile(r"[\s]")


class FiHetuDetector(Detector):
    name = "fi_hetu"
    token = "FI_HETU"
    region = "fi"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<!\d)\d{6}[-+ABCDEFUVWXY]\d{3}[A-Z0-9](?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate).upper()


register(FiHetuDetector())
