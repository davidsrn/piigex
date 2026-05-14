from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

# stdnum.us.atin is shape-only and accepts any 9xx-xx-xxxx, which would make ATIN
# a catch-all for 9-digit numbers that fail SSN/EIN/ITIN. The IRS reserves the
# middle group "93" for ATIN, so we hand-roll the validator to enforce that.
_STRIP_RE = re.compile(r"-")


class AtinDetector(Detector):
    name = "us_atin"
    token = "US_ATIN"
    region = "us"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9])(?:9\d{2}-93-\d{4}|9\d{2}93\d{4})(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        compact = _STRIP_RE.sub("", candidate)
        return bool(re.fullmatch(r"9\d{2}93\d{4}", compact))

    def normalize(self, candidate: str) -> str:
        return _STRIP_RE.sub("", candidate)


register(AtinDetector())
