from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector


class EmailDetector(Detector):
    # Email addresses per RFC 5321 practical approximation.
    # https://tools.ietf.org/html/rfc5321
    name = "intl_email"
    token = "EMAIL"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<![A-Za-z0-9._%+\-])"
        r"[A-Za-z0-9._%+\-]{1,64}"
        r"@"
        r"[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)*"
        r"\.[A-Za-z]{2,}",
    )

    def validate(self, candidate: str) -> bool:
        if len(candidate) > 254 or "@" not in candidate:
            return False
        local, _, domain = candidate.partition("@")
        return 1 <= len(local) <= 64 and "." in domain

    def normalize(self, candidate: str) -> str:
        return candidate.lower()


register(EmailDetector())
