from __future__ import annotations

import dataclasses
import re
import threading
from typing import Any

from piigex.detectors import get_detectors
from piigex.detectors.base import Detector
from piigex.tokens import TokenMap
from piigex.types import Match

_SAFE_FLAGS = re.ASCII


def _format_key(k: object) -> str:
    sk = str(k)
    if any(c in sk for c in ".[]"):
        return f'["{sk}"]'
    return sk


class Scrubber:
    def __init__(
        self,
        detectors: list[str] | None = None,
        *,
        exclude: list[str] | None = None,
        regions: list[str] | None = None,
        min_feasibility: str = "medium",
        validate: bool = True,
        stable_tokens: bool = False,
        token_format: str = "{{{name}}}",
        token_map: TokenMap | None = None,
    ) -> None:
        self._validate = validate
        self._stable_tokens = stable_tokens
        self._token_format = token_format
        self._persistent_token_map = token_map

        self._detectors: list[Detector] = get_detectors(
            names=detectors,
            regions=regions,
            min_feasibility=min_feasibility,
            exclude=exclude,
        )
        self._det_by_name: dict[str, Detector] = {d.name: d for d in self._detectors}

        if self._detectors:
            parts = [f"(?P<{d.name}>{d.pattern.pattern})" for d in self._detectors]
            combined_flags = _SAFE_FLAGS
            for d in self._detectors:
                extra = d.pattern.flags & ~(re.UNICODE | _SAFE_FLAGS)
                if extra:
                    # int() forces a stable numeric format across Python versions;
                    # IntFlag.__format__ changed between 3.10 and 3.13.
                    raise ValueError(
                        f"Detector {d.name!r} uses regex flags "
                        f"({int(extra):#x}) not allowed in the combined engine"
                    )
            self._pattern: re.Pattern[str] = re.compile("|".join(parts), combined_flags)
        else:
            self._pattern = re.compile(r"(?!)")  # never matches

    def scan(self, text: str) -> list[Match]:
        results: list[Match] = []
        if not self._detectors:
            return results
        pos = 0
        text_len = len(text)
        while pos <= text_len:
            m = self._pattern.search(text, pos)
            if m is None:
                break
            start = m.start()
            candidates: list[tuple[Detector, int, str, bool]] = []
            for det in self._detectors:
                dm = det.pattern.match(text, start)
                if dm is None:
                    continue
                value = dm.group(0)
                valid = det.validate(value)
                candidates.append((det, dm.end(), value, valid))
            if not candidates:  # pragma: no cover
                # Defensive: the combined regex matched here, so at least one
                # detector pattern must also match. Guard against infinite loop.
                pos = start + 1
                continue
            if self._validate:
                valid_candidates = [c for c in candidates if c[3]]
                if valid_candidates:
                    candidates = valid_candidates
            best = max(candidates, key=lambda c: c[1])
            det, end, value, valid = best
            results.append(
                Match(
                    name=det.name,
                    token=det.token,
                    start=start,
                    end=end,
                    value=value,
                    valid=valid,
                )
            )
            pos = end if end > start else start + 1
        return results

    def clean(self, text: str, *, token_map: TokenMap | None = None) -> str:
        # Explicit if/else (not a ternary) because operator precedence makes the
        # ternary form misread; this version was a deliberate fix for that.
        if self._stable_tokens:  # noqa: SIM108
            tm = token_map or self._persistent_token_map or TokenMap()
        else:
            tm = None

        matches = self.scan(text)
        if self._validate:
            matches = [m for m in matches if m.valid]

        parts: list[str] = []
        pos = 0
        for m in matches:
            parts.append(text[pos : m.start])
            if tm is not None:
                det = self._det_by_name[m.name]
                normalized = det.normalize(m.value)
                idx = tm.get(m.name, normalized)
                effective = f"{m.token}_{idx}"
            else:
                effective = m.token
            parts.append(self._token_format.replace("{name}", effective))
            pos = m.end
        parts.append(text[pos:])
        return "".join(parts)

    def clean_json(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return self.clean(obj)
        if isinstance(obj, dict):
            return {k: self.clean_json(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.clean_json(v) for v in obj]
        if isinstance(obj, tuple):
            return tuple(self.clean_json(v) for v in obj)
        return obj

    def scan_json(self, obj: Any) -> list[Match]:
        results: list[Match] = []
        self._scan_json_walk(obj, "", results)
        return results

    def _scan_json_walk(self, obj: Any, path: str, results: list[Match]) -> None:
        if isinstance(obj, str):
            for m in self.scan(obj):
                results.append(dataclasses.replace(m, path=path))
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                sk = _format_key(k)
                child = f"{path}.{sk}" if path and not sk.startswith("[") else f"{path}{sk}"
                self._scan_json_walk(v, child, results)
            return
        if isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                child = f"{path}[{i}]"
                self._scan_json_walk(v, child, results)
            return


_default: Scrubber | None = None
_default_lock = threading.Lock()


def _get_default() -> Scrubber:
    global _default
    if _default is None:
        with _default_lock:
            if _default is None:
                _default = Scrubber()
    return _default


def scan(text: str) -> list[Match]:
    return _get_default().scan(text)


def clean(text: str) -> str:
    return _get_default().clean(text)


def clean_json(obj: Any) -> Any:
    return _get_default().clean_json(obj)


def scan_json(obj: Any) -> list[Match]:
    return _get_default().scan_json(obj)
