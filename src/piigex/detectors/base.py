from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import ClassVar


class Detector(ABC):
    name: ClassVar[str]
    token: ClassVar[str]
    pattern: ClassVar[re.Pattern[str]]
    region: ClassVar[str]
    feasibility: ClassVar[str]
    default_enabled: ClassVar[bool]

    @abstractmethod
    def validate(self, candidate: str) -> bool: ...

    def normalize(self, candidate: str) -> str:
        return candidate.lower().replace(" ", "").replace(".", "").replace("-", "")
