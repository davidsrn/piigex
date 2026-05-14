"""Command-line interface for piigex."""

from __future__ import annotations

import argparse
import json
import sys

from piigex.core import Scrubber


def _build_scrubber(args: argparse.Namespace) -> Scrubber:
    regions = [r.strip() for r in args.regions.split(",")] if args.regions else None
    detectors = [d.strip() for d in args.detectors.split(",")] if args.detectors else None
    exclude = [d.strip() for d in args.exclude.split(",")] if args.exclude else None
    return Scrubber(
        detectors=detectors,
        exclude=exclude,
        regions=regions,
        min_feasibility=args.min_feasibility,
        validate=not args.no_validate,
        stable_tokens=getattr(args, "stable_tokens", False),
        token_format=getattr(args, "token_format", "{{{name}}}"),
    )


def _cmd_scrub(args: argparse.Namespace) -> None:
    scrubber = _build_scrubber(args)
    text = sys.stdin.read()
    if args.json:
        sys.stdout.write(json.dumps(scrubber.clean_json(json.loads(text))))
    else:
        sys.stdout.write(scrubber.clean(text))


def _cmd_scan(args: argparse.Namespace) -> None:
    scrubber = _build_scrubber(args)
    text = sys.stdin.read()
    matches = scrubber.scan_json(json.loads(text)) if args.json else scrubber.scan(text)
    output = [
        {
            "name": m.name,
            "token": m.token,
            "start": m.start,
            "end": m.end,
            "value": m.value,
            "valid": m.valid,
            "path": m.path,
        }
        for m in matches
    ]
    sys.stdout.write(json.dumps(output))


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--regions", default=None, metavar="ES,IT,intl")
    parser.add_argument("--detectors", default=None, metavar="es_dni,intl_iban")
    parser.add_argument("--exclude", default=None, metavar="es_phone,it_phone")
    parser.add_argument(
        "--min-feasibility",
        default="medium",
        choices=["high", "medium", "low"],
        dest="min_feasibility",
    )
    parser.add_argument("--no-validate", action="store_true", dest="no_validate")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Parse stdin as JSON, walk the structure, and scrub string values only.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="piigex", description="Detect and redact PII.")
    sub = parser.add_subparsers(dest="command", required=True)

    scrub_p = sub.add_parser("scrub", help="Read stdin, write scrubbed output to stdout.")
    _add_common_args(scrub_p)
    scrub_p.add_argument("--token-format", default="{{{name}}}", dest="token_format")
    scrub_p.add_argument("--stable-tokens", action="store_true", dest="stable_tokens")
    scrub_p.set_defaults(func=_cmd_scrub)

    scan_p = sub.add_parser("scan", help="Read stdin, write JSON matches to stdout.")
    _add_common_args(scan_p)
    scan_p.set_defaults(func=_cmd_scan)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
