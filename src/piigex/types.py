from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Match:
    name: str
    token: str
    start: int
    end: int
    value: str
    valid: bool
    path: str = ""
