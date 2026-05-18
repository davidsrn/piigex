"""Regenerate docs/coverage.md from the live detector registry.

Run from the repo root:

    python scripts/gen_coverage.py > docs/coverage.md
"""

from __future__ import annotations

import sys

from piigex.detectors import get_registry

REGION_NAMES = {
    "at": "Austria", "be": "Belgium", "bg": "Bulgaria", "cz": "Czech Republic",
    "de": "Germany", "dk": "Denmark", "ee": "Estonia", "es": "Spain",
    "fi": "Finland", "fr": "France", "gb": "United Kingdom", "gr": "Greece", "hr": "Croatia",
    "hu": "Hungary", "ie": "Ireland", "it": "Italy", "lt": "Lithuania",
    "nl": "Netherlands", "pl": "Poland", "pt": "Portugal", "ro": "Romania",
    "se": "Sweden", "si": "Slovenia", "sk": "Slovakia", "us": "United States",
    "intl": "International",
}


def main() -> None:
    reg = get_registry()
    by_region: dict[str, list[tuple[str, str, str, bool]]] = {}
    for name, d in sorted(reg.items()):
        by_region.setdefault(d.region, []).append(
            (name, d.token, d.feasibility, d.default_enabled)
        )

    total = len(reg)
    default_on = sum(1 for _, d in reg.items() if d.default_enabled)
    opt_in = total - default_on

    out = sys.stdout
    out.write("# Coverage\n\n")
    out.write(
        f"piigex has {total} detectors across {len(by_region)} regions. "
        f"{default_on} of them are on by default. The other {opt_in} are opt-in: "
        "phone numbers and shape-only identifiers, kept off because they produce "
        "more false positives.\n\n"
    )
    out.write(
        "Each detector pairs a pre-compiled regex with a checksum validator. "
        "Validators delegate to `python-stdnum` where possible and are hand-rolled "
        "otherwise. With `validate=True` (the default), only checksum-valid matches "
        "are redacted.\n\n"
    )

    out.write("## Feasibility tiers\n\n")
    out.write(
        "- high: distinctive shape and a strong checksum. Very low false-positive risk.\n"
        "- medium: distinctive shape but weak or absent checksum, or a strong checksum "
        "with an ambiguous shape. Phone numbers and shape-only IDs fall here and are off "
        "by default.\n"
        "- low: reserved for future detectors with high false-positive risk.\n\n"
    )

    out.write("## Summary by region\n\n")
    out.write("| Region | Detectors | Default-on | Opt-in |\n")
    out.write("|---|---|---|---|\n")
    for region in sorted(by_region):
        dets = by_region[region]
        region_name = REGION_NAMES.get(region, region.upper())
        on = sum(1 for _, _, _, e in dets if e)
        off = len(dets) - on
        out.write(f"| {region_name} (`{region}`) | {len(dets)} | {on} | {off} |\n")
    out.write("\n")

    out.write("## Detectors by region\n")
    ordering = ["intl"] + [r for r in sorted(by_region) if r != "intl"]
    for region in ordering:
        dets = by_region[region]
        region_name = REGION_NAMES.get(region, region.upper())
        out.write(f"\n### {region_name} (`{region}`)\n\n")
        out.write("| Detector name | Token | Feasibility | Default |\n")
        out.write("|---|---|---|---|\n")
        for name, token, feas, enabled in sorted(dets):
            default = "on" if enabled else "off"
            out.write(f"| `{name}` | `{{{{{token}}}}}` | {feas} | {default} |\n")

    out.write(
        "\n## Notes on opt-in detectors\n\n"
        "Phone numbers and shape-only identifiers (passports, vehicle plates, French CNI, "
        "Belgian payment references) are off by default. They either lack a strong checksum "
        "or share a shape with plenty of non-PII strings. Enable them by name:\n\n"
        "```python\n"
        "from piigex import Scrubber\n\n"
        's = Scrubber(detectors=["us_phone", "us_passport", "intl_phone_e164"])\n'
        "```\n\n"
        "`min_feasibility` and `regions` only narrow the default set; they do not "
        "promote a `default_enabled=False` detector into the active set. Always pass "
        "opt-in detectors by name.\n\n"
        "## Regenerating this page\n\n"
        "This file is generated from the live detector registry. After you add or modify "
        "a detector, regenerate it with:\n\n"
        "```sh\n"
        "python scripts/gen_coverage.py > docs/coverage.md\n"
        "```\n"
    )


if __name__ == "__main__":
    main()
