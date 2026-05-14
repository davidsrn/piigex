from __future__ import annotations

import re

from piigex.detectors import register
from piigex.detectors.base import Detector

_STRIP = re.compile(r"[\s\-]")


def _luhn_valid(number: str) -> bool:
    # https://en.wikipedia.org/wiki/Luhn_algorithm
    total = 0
    for i, d in enumerate(reversed(number)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


class CreditCardDetector(Detector):
    # Payment card numbers (Visa, Mastercard, Amex, Discover, UnionPay).
    # Luhn algorithm: https://en.wikipedia.org/wiki/Payment_card_number
    # Patterns cover 15-digit Amex (4-6-5 groups) and 16-digit cards (4-4-4-4 groups).
    name = "intl_credit_card"
    token = "CREDIT_CARD"
    region = "intl"
    feasibility = "high"
    default_enabled = True

    pattern = re.compile(
        r"(?<!\d)"
        r"(?:"
        # Amex: 3[47]XX XXXXXX XXXXX (15 digits)
        r"3[47]\d{2}[ \-]?\d{6}[ \-]?\d{5}"
        r"|"
        # 16-digit cards: XXXX XXXX XXXX XXXX (Visa 4x, MC 5x, Discover 6x, UnionPay 62)
        r"(?:4\d{3}|5[1-5]\d{2}|2[2-7]\d{2}|6(?:011|22[1-9]|[45]\d{2}))"
        r"[ \-]?\d{4}[ \-]?\d{4}[ \-]?\d{4}"
        r")"
        r"(?!\d)",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        digits = _STRIP.sub("", candidate)
        if not digits.isdigit() or len(digits) not in range(13, 20):
            return False
        return _luhn_valid(digits)

    def normalize(self, candidate: str) -> str:
        return _STRIP.sub("", candidate)


register(CreditCardDetector())
