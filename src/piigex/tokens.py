from __future__ import annotations


class TokenMap:
    """Per-call counter that maps (detector_name, normalized_value) → stable index."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._seen: dict[tuple[str, str], int] = {}

    def get(self, detector_name: str, normalized: str) -> int:
        key = (detector_name, normalized)
        if key not in self._seen:
            count = self._counters.get(detector_name, 0) + 1
            self._counters[detector_name] = count
            self._seen[key] = count
        return self._seen[key]

    def reset(self) -> None:
        self._counters.clear()
        self._seen.clear()
