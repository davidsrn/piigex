from __future__ import annotations

import json
import subprocess
import sys

import pytest

import piigex
from piigex import Scrubber

VALID_IBAN = "GB29NWBK60161331926819"
VALID_IBAN_2 = "DE89370400440532013000"


@pytest.fixture()
def s() -> Scrubber:
    return Scrubber(detectors=["intl_iban", "intl_email"])


def test_clean_json_string_passthrough(s: Scrubber) -> None:
    assert s.clean_json(f"pay to {VALID_IBAN}") == "pay to {{IBAN}}"


def test_clean_json_flat_dict(s: Scrubber) -> None:
    payload = {"account": VALID_IBAN, "memo": "hello"}
    result = s.clean_json(payload)
    assert result == {"account": "{{IBAN}}", "memo": "hello"}


def test_clean_json_preserves_non_string_primitives(s: Scrubber) -> None:
    payload = {"amount": 100, "active": True, "fee": 1.5, "ref": None}
    assert s.clean_json(payload) == payload


def test_clean_json_nested(s: Scrubber) -> None:
    payload = {
        "user": {"iban": VALID_IBAN, "name": "Alice"},
        "meta": {"src": "web"},
    }
    expected = {
        "user": {"iban": "{{IBAN}}", "name": "Alice"},
        "meta": {"src": "web"},
    }
    assert s.clean_json(payload) == expected


def test_clean_json_list(s: Scrubber) -> None:
    payload = [VALID_IBAN, "nothing here", VALID_IBAN_2]
    assert s.clean_json(payload) == ["{{IBAN}}", "nothing here", "{{IBAN}}"]


def test_clean_json_list_of_dicts(s: Scrubber) -> None:
    payload = [{"iban": VALID_IBAN}, {"iban": VALID_IBAN_2}]
    assert s.clean_json(payload) == [{"iban": "{{IBAN}}"}, {"iban": "{{IBAN}}"}]


def test_clean_json_tuple_returns_tuple(s: Scrubber) -> None:
    result = s.clean_json((VALID_IBAN, "hi"))
    assert result == ("{{IBAN}}", "hi")
    assert isinstance(result, tuple)


def test_clean_json_unknown_type_passthrough(s: Scrubber) -> None:
    obj = {1, 2, 3}
    assert s.clean_json(obj) is obj


def test_clean_json_idempotent(s: Scrubber) -> None:
    payload = {"a": {"b": [VALID_IBAN]}}
    once = s.clean_json(payload)
    twice = s.clean_json(once)
    assert once == twice


def test_scan_json_path_for_dict_value(s: Scrubber) -> None:
    matches = s.scan_json({"account": VALID_IBAN})
    assert len(matches) == 1
    assert matches[0].path == "account"
    assert matches[0].value == VALID_IBAN


def test_scan_json_path_for_nested_dict(s: Scrubber) -> None:
    matches = s.scan_json({"user": {"profile": {"iban": VALID_IBAN}}})
    assert len(matches) == 1
    assert matches[0].path == "user.profile.iban"


def test_scan_json_path_for_list_index(s: Scrubber) -> None:
    matches = s.scan_json([VALID_IBAN, VALID_IBAN_2])
    paths = sorted(m.path for m in matches)
    assert paths == ["[0]", "[1]"]


def test_scan_json_path_for_list_of_dicts(s: Scrubber) -> None:
    matches = s.scan_json([{"iban": VALID_IBAN}])
    assert len(matches) == 1
    assert matches[0].path == "[0].iban"


def test_scan_json_path_for_dict_with_list(s: Scrubber) -> None:
    matches = s.scan_json({"accounts": [VALID_IBAN, VALID_IBAN_2]})
    paths = sorted(m.path for m in matches)
    assert paths == ["accounts[0]", "accounts[1]"]


def test_scan_json_path_empty_for_bare_string(s: Scrubber) -> None:
    matches = s.scan_json(f"pay {VALID_IBAN}")
    assert len(matches) == 1
    assert matches[0].path == ""


def test_scan_json_skips_non_string_primitives(s: Scrubber) -> None:
    assert s.scan_json({"n": 12345, "ok": True, "x": None}) == []


def test_scan_json_match_preserves_metadata(s: Scrubber) -> None:
    matches = s.scan_json({"iban": VALID_IBAN})
    m = matches[0]
    assert m.name == "intl_iban"
    assert m.token == "IBAN"
    assert m.valid is True
    assert m.value == VALID_IBAN


def test_scan_json_finds_email_too() -> None:
    sc = Scrubber(detectors=["intl_email"])
    matches = sc.scan_json({"contact": "ping me at alice@example.com please"})
    assert len(matches) == 1
    assert matches[0].path == "contact"


def test_top_level_clean_json() -> None:
    payload = {"iban": VALID_IBAN}
    result = piigex.clean_json(payload)
    assert result["iban"] == "{{IBAN}}"


def test_top_level_scan_json() -> None:
    matches = piigex.scan_json({"iban": VALID_IBAN})
    assert len(matches) == 1
    assert matches[0].path == "iban"


def test_match_path_default_empty() -> None:
    sc = Scrubber(detectors=["intl_iban"])
    matches = sc.scan(VALID_IBAN)
    assert matches[0].path == ""


def test_cli_scrub_json() -> None:
    payload = json.dumps({"iban": VALID_IBAN, "memo": "hi"})
    result = subprocess.run(
        [sys.executable, "-m", "piigex.cli", "scrub", "--json", "--detectors", "intl_iban"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed == {"iban": "{{IBAN}}", "memo": "hi"}


def test_cli_scan_json_includes_path() -> None:
    payload = json.dumps({"user": {"iban": VALID_IBAN}})
    result = subprocess.run(
        [sys.executable, "-m", "piigex.cli", "scan", "--json", "--detectors", "intl_iban"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["path"] == "user.iban"
