# json_scrubber.py: scrub PII from JSON payloads (API requests/responses, webhooks).
#
# Walks nested dicts/lists, scrubbing only string values. Keys, numbers,
# booleans, and null are preserved. scan_json also returns each match with a
# dotted path showing exactly where the PII was found.
#
# Usage:
#   echo '{"user": {"iban": "GB29NWBK60161331926819"}}' | python examples/json_scrubber.py

import json
import sys

import piigex

if __name__ == "__main__":
    payload = json.load(sys.stdin)
    scrubbed = piigex.clean_json(payload)
    matches = piigex.scan_json(payload)

    json.dump(scrubbed, sys.stdout, indent=2)
    sys.stdout.write("\n")

    if matches:
        sys.stderr.write("Detected PII:\n")
        for m in matches:
            sys.stderr.write(f"  {m.path or '<root>'}: {m.name} ({m.token})\n")
