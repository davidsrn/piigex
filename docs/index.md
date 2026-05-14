# piigex documentation

A small PII detection and redaction library for structured identifiers. It uses
regex plus checksum validation. No ML, no NLP, no large dependencies.

- [Quickstart](#quickstart): three-line examples for the common cases.
- [Coverage](coverage.md): every detector grouped by region, with default and opt-in status.
- [Python API](api.md): `Scrubber`, `clean`, `scan`, `clean_json`, `scan_json`, `Match`.
- [Command-line interface](cli.md): `piigex scrub` and `piigex scan` with stdin and JSON modes.
- [Extending](extending.md): how to add a detector for a new identifier or region.

## When to use piigex

Reach for piigex when you need to detect or redact structured personal
identifiers in free text or JSON payloads:

- Sanitising chatbot input before it goes to an LLM.
- Scrubbing application logs.
- Redacting customer-support transcripts.
- Quick GDPR-aware data masking in pipelines.

piigex detects values whose shape is fully specified: tax IDs, social security
numbers, IBANs, BICs, credit cards, email addresses, IP addresses, MAC addresses.
It does not detect names, organisations, addresses, or other free-form sensitive
content. For that, use a NER-based tool such as
[Microsoft Presidio](https://microsoft.github.io/presidio/).

## Quickstart

```python
from piigex import clean, scan

clean("Send payment to ES91 2100 0418 4502 0005 1332 by Friday")
# -> "Send payment to {{IBAN}} by Friday"

scan("IBAN: DE89370400440532013000")
# -> [Match(name='intl_iban', token='IBAN', start=6, end=28,
#           value='DE89370400440532013000', valid=True)]
```

JSON payloads:

```python
import piigex

piigex.clean_json({
    "user": {"email": "alice@example.com", "iban": "GB29NWBK60161331926819"},
    "amount": 100,
})
# -> {"user": {"email": "{{EMAIL}}", "iban": "{{IBAN}}"}, "amount": 100}
```

Command line:

```sh
echo "DNI 12345678Z and IBAN GB29NWBK60161331926819" | piigex scrub
# -> "DNI {{ES_DNI}} and IBAN {{IBAN}}"
```

For region-scoped scrubbing, stable tokens, persistent token maps, and
non-validating shape-only mode, see [the Python API reference](api.md).

## Design

- Pure regex for detection. Patterns are pre-compiled at module import. The scan
  engine builds one combined alternation, runs `re.search` per candidate
  position, then picks the longest validated match.
- Checksum validation by default. Validators delegate to `python-stdnum` where it
  covers the spec, and are hand-rolled otherwise (with the algorithm spec linked
  from the detector module).
- Country-agnostic layout. Detectors live under `src/piigex/detectors/<iso2>/`.
  Adding a region means adding modules in the right folder. See [extending](extending.md).
- One runtime dependency: `python-stdnum`.
