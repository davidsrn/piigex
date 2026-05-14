from __future__ import annotations

import re

from stdnum.be import bis as _stdnum

from piigex.detectors import register
from piigex.detectors.base import Detector


class BisDetector(Detector):
    # stdnum.be.bis: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.be.bis
    # BIS number for persons not registered in the national register.
    # Same structure as NN but month field +20 (gender unknown) or +40 (gender known).
    # Same mod-97 check as NN.
    name = "be_bis"
    token = "BE_BIS"
    region = "be"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(r"(?<!\d)\d{11}(?!\d)", re.ASCII)

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(BisDetector())
