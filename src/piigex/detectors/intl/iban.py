from __future__ import annotations

import re

from stdnum import iban as _stdnum_iban

from piigex.detectors import register
from piigex.detectors.base import Detector


class IbanDetector(Detector):
    # stdnum.iban: https://arthurdejong.org/python-stdnum/doc/1.20/stdnum.iban
    name = "intl_iban"
    token = "IBAN"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    # Matches compact form (no spaces) or standard formatted form (4-char groups
    # separated by single spaces). Lookarounds prevent matching substrings of
    # longer alphanumeric sequences.
    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{2}[0-9]{2}"
        r"(?:"
        r"[A-Z0-9]{11,30}"  # compact BBAN: 11–30 chars (total 15–34)
        r"|"
        r"(?:[ ][A-Z0-9]{4}){2,7}(?:[ ][A-Z0-9]{1,4})?"  # space-grouped form
        r")"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum_iban.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum_iban.compact(candidate))


register(IbanDetector())
