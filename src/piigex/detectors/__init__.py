from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from piigex.detectors.base import Detector

_REGISTRY: dict[str, Detector] = {}

_FEASIBILITY_RANK: dict[str, int] = {"high": 0, "medium": 1, "low": 2}


def register(detector: Detector) -> None:
    _REGISTRY[detector.name] = detector


def get_registry() -> dict[str, Detector]:
    return dict(_REGISTRY)


def get_detectors(
    *,
    names: list[str] | None = None,
    regions: list[str] | None = None,
    min_feasibility: str = "medium",
    exclude: list[str] | None = None,
) -> list[Detector]:
    min_rank = _FEASIBILITY_RANK.get(min_feasibility, 1)
    result: list[Detector] = []

    for name, det in _REGISTRY.items():
        if exclude and name in exclude:
            continue

        if names is not None:
            # Explicit list: include if named, regardless of default_enabled
            if name not in names:
                continue
        else:
            # Default set: respect default_enabled, region, and feasibility filters
            if not det.default_enabled:
                continue
            if regions is not None and det.region not in regions:
                continue
            if _FEASIBILITY_RANK.get(det.feasibility, 99) > min_rank:
                continue

        result.append(det)

    return result


def _load_all() -> None:
    base = Path(__file__).parent
    for pkg_dir in sorted(base.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("_"):
            continue
        modules = sorted(
            name
            for _f, name, _p in pkgutil.iter_modules([str(pkg_dir)])
            if not name.startswith("_")
        )
        for mod_name in modules:
            importlib.import_module(f"piigex.detectors.{pkg_dir.name}.{mod_name}")


_load_all()
