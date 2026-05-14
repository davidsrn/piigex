"""Tests for the piigex CLI (scrub and scan subcommands)."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from unittest.mock import patch

from piigex.cli import main


def _run(args: list[str], stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "piigex.cli"] + args,
        input=stdin,
        capture_output=True,
        text=True,
    )


def _run_direct(args: list[str], stdin: str) -> str:
    with (
        patch("sys.argv", ["piigex"] + args),
        patch("sys.stdin", io.StringIO(stdin)),
        patch("sys.stdout", new_callable=io.StringIO) as mock_out,
    ):
        main()
        return mock_out.getvalue()


# ---------------------------------------------------------------------------
# scrub subcommand
# ---------------------------------------------------------------------------


def test_scrub_happy_path() -> None:
    result = _run(["scrub", "--detectors", "intl_iban"], "Pay to GB29NWBK60161331926819 now")
    assert result.returncode == 0
    assert "{{IBAN}}" in result.stdout
    assert "GB29NWBK60161331926819" not in result.stdout


def test_scrub_with_regions() -> None:
    result = _run(
        ["scrub", "--regions", "intl"],
        "Send to GB29NWBK60161331926819",
    )
    assert result.returncode == 0
    assert "{{IBAN}}" in result.stdout


def test_scrub_with_exclude() -> None:
    result = _run(
        ["scrub", "--detectors", "intl_iban", "--exclude", "intl_iban"],
        "Pay to GB29NWBK60161331926819 now",
    )
    assert result.returncode == 0
    assert "GB29NWBK60161331926819" in result.stdout


def test_scrub_no_validate() -> None:
    result = _run(
        ["scrub", "--detectors", "intl_iban", "--no-validate"],
        "Bad: GB00NWBK60161331926819",
    )
    assert result.returncode == 0
    assert "{{IBAN}}" in result.stdout


def test_scrub_stable_tokens() -> None:
    result = _run(
        ["scrub", "--detectors", "intl_iban", "--stable-tokens"],
        "A=GB29NWBK60161331926819 B=GB29NWBK60161331926819",
    )
    assert result.returncode == 0
    assert result.stdout.count("{{IBAN_1}}") == 2


def test_scrub_token_format() -> None:
    result = _run(
        ["scrub", "--detectors", "intl_iban", "--token-format", "[{name}]"],
        "Pay to GB29NWBK60161331926819",
    )
    assert result.returncode == 0
    assert "[IBAN]" in result.stdout


# ---------------------------------------------------------------------------
# scan subcommand
# ---------------------------------------------------------------------------


def test_scan_happy_path() -> None:
    result = _run(["scan", "--detectors", "intl_iban"], "Pay to GB29NWBK60161331926819 now")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    m = data[0]
    assert m["name"] == "intl_iban"
    assert m["token"] == "IBAN"
    assert m["value"] == "GB29NWBK60161331926819"
    assert m["valid"] is True
    assert "start" in m
    assert "end" in m


def test_scan_with_regions() -> None:
    result = _run(
        ["scan", "--regions", "intl"],
        "IBAN: GB29NWBK60161331926819",
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert any(m["name"] == "intl_iban" for m in data)


def test_scan_no_validate_accepts_invalid() -> None:
    result = _run(
        ["scan", "--detectors", "intl_iban", "--no-validate"],
        "GB00NWBK60161331926819",
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["valid"] is False  # valid reflects actual validity even in no-validate mode


def test_scan_empty_input() -> None:
    result = _run(["scan", "--detectors", "intl_iban"], "")
    assert result.returncode == 0
    assert json.loads(result.stdout) == []


def test_scan_no_matches() -> None:
    result = _run(["scan", "--detectors", "intl_iban"], "no PII here")
    assert result.returncode == 0
    assert json.loads(result.stdout) == []


def test_main_module_invocable() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "piigex", "scan", "--detectors", "intl_iban"],
        input="GB29NWBK60161331926819",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1


def test_scrub_min_feasibility() -> None:
    result = _run(
        ["scrub", "--min-feasibility", "high"],
        "GB29NWBK60161331926819",
    )
    assert result.returncode == 0
    assert "{{IBAN}}" in result.stdout


def test_scrub_json_input() -> None:
    payload = '{"iban": "GB29NWBK60161331926819", "note": "hi"}'
    out = _run_direct(["scrub", "--detectors", "intl_iban", "--json"], payload)
    data = json.loads(out)
    assert data["iban"] == "{{IBAN}}"
    assert data["note"] == "hi"


# ---------------------------------------------------------------------------
# Direct-call tests (cover cli.py for coverage)
# ---------------------------------------------------------------------------


def test_direct_scrub_basic() -> None:
    out = _run_direct(["scrub", "--detectors", "intl_iban"], "Pay to GB29NWBK60161331926819")
    assert "{{IBAN}}" in out


def test_direct_scrub_no_validate() -> None:
    out = _run_direct(
        ["scrub", "--detectors", "intl_iban", "--no-validate"],
        "Bad: GB00NWBK60161331926819",
    )
    assert "{{IBAN}}" in out


def test_direct_scrub_stable_tokens() -> None:
    out = _run_direct(
        ["scrub", "--detectors", "intl_iban", "--stable-tokens"],
        "A=GB29NWBK60161331926819 B=GB29NWBK60161331926819",
    )
    assert out.count("{{IBAN_1}}") == 2


def test_direct_scrub_token_format() -> None:
    out = _run_direct(
        ["scrub", "--detectors", "intl_iban", "--token-format", "[{name}]"],
        "Pay to GB29NWBK60161331926819",
    )
    assert "[IBAN]" in out


def test_direct_scrub_with_regions() -> None:
    out = _run_direct(["scrub", "--regions", "intl"], "GB29NWBK60161331926819")
    assert "{{IBAN}}" in out


def test_direct_scrub_with_exclude() -> None:
    out = _run_direct(
        ["scrub", "--detectors", "intl_iban", "--exclude", "intl_iban"],
        "GB29NWBK60161331926819",
    )
    assert "GB29NWBK60161331926819" in out


def test_direct_scan_basic() -> None:
    out = _run_direct(["scan", "--detectors", "intl_iban"], "GB29NWBK60161331926819")
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["name"] == "intl_iban"
    assert data[0]["valid"] is True


def test_direct_scan_no_validate() -> None:
    out = _run_direct(
        ["scan", "--detectors", "intl_iban", "--no-validate"],
        "GB00NWBK60161331926819",
    )
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["valid"] is False  # valid reflects actual validity even in no-validate mode


def test_direct_scan_empty() -> None:
    out = _run_direct(["scan", "--detectors", "intl_iban"], "")
    assert json.loads(out) == []


def test_direct_scan_with_regions() -> None:
    out = _run_direct(["scan", "--regions", "intl"], "GB29NWBK60161331926819")
    data = json.loads(out)
    assert any(m["name"] == "intl_iban" for m in data)


def test_direct_scrub_min_feasibility() -> None:
    out = _run_direct(["scrub", "--min-feasibility", "high"], "GB29NWBK60161331926819")
    assert "{{IBAN}}" in out
