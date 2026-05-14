# Adding a new detector

Detectors live under `src/piigex/detectors/<iso2>/` (or `intl/` for
cross-border identifiers). Each detector is a single Python module that
defines a class and registers an instance of it.

This page walks through adding `xx_example`. The same checklist applies to a
new country or to a new identifier inside one that already exists.

## 1. Pick a directory

ISO 3166-1 alpha-2 lowercase. If the country doesn't exist yet, create the
directory and an empty `__init__.py`:

```sh
mkdir -p src/piigex/detectors/xx
touch src/piigex/detectors/xx/__init__.py
```

`intl/` is reserved for identifiers that aren't tied to one country (IBAN,
BIC, credit card, email, IP addresses, MAC, EU VAT).

## 2. Write the detector module

```python
# src/piigex/detectors/xx/example.py
from __future__ import annotations

import re

from stdnum.xx import example as _stdnum  # if stdnum covers it

from piigex.detectors import register
from piigex.detectors.base import Detector


class ExampleDetector(Detector):
    # stdnum.xx.example - https://arthurdejong.org/python-stdnum/doc/.../stdnum.xx.example
    # Format: <describe shape>
    # Checksum: <describe algorithm or link the spec>
    name = "xx_example"
    token = "XX_EXAMPLE"
    region = "xx"
    feasibility = "high"        # see docs/coverage.md
    default_enabled = True      # opt-in detectors set this False

    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{2}\d{6}"
        r"(?![A-Za-z0-9])",
        re.ASCII,
    )

    def validate(self, candidate: str) -> bool:
        return bool(_stdnum.is_valid(candidate))

    def normalize(self, candidate: str) -> str:
        return str(_stdnum.compact(candidate))


register(ExampleDetector())
```

### Pattern guidelines

- Always pre-compile. Call `re.compile(...)` at module import time.
- Use `re.ASCII` unless you genuinely need Unicode semantics. The combined
  engine rejects detectors that use unsupported flags like `IGNORECASE`,
  `DOTALL`, or `MULTILINE`. Spell the alternatives out explicitly instead.
- Anchor with lookarounds, not whitespace. Use `(?<!\d)` / `(?!\d)` for numeric
  IDs and `(?<![A-Za-z0-9])` / `(?![A-Za-z0-9])` for mixed alphanumeric.
  Consuming a leading space would shift the reported span.
- Use bounded quantifiers only. Avoid `+` and `*` on alternations so worst-case
  scan time stays linear.

### Validator guidelines

- Delegate to `python-stdnum` when it covers the spec. Use `is_valid()`, not
  `validate()` (which raises on invalid input).
- For hand-rolled checksums, link the spec in a comment header so reviewers
  can audit the algorithm against the source.
- Validators must never raise on shape-conforming input. Catch `ValueError`
  inside `int()` calls and return `False` instead.

### `feasibility` and `default_enabled`

| Feasibility | Default | Examples |
|---|---|---|
| `high` | usually `True` | IBAN, DNI, NIR, CNP. Distinctive shape plus a strong checksum |
| `medium` | usually `False` | passports (shape-only), phone numbers, French CNI |
| `low` | `False` | reserved for future detectors with high false-positive risk |

The default Scrubber uses `min_feasibility="medium"`, which includes both
`high` and `medium` detectors. The flag that actually keeps a detector off by
default is `default_enabled=False`. The feasibility tier is informational and
lets the user opt out broadly with `min_feasibility="high"`.

## 3. Write tests

Create `tests/test_xx.py` with the five test types every other detector
includes:

1. Positive: 5+ valid examples taken from a public spec or Wikipedia test
   vectors. Never real PII.

   ```python
   VALID_EXAMPLES = ["AB123456", "CD789012", ...]
   ```

2. Negative: 5+ strings that match the shape but fail the checksum. Verify
   they are rejected with `validate=True` and accepted with `validate=False`.

3. Embedded: the identifier surrounded by punctuation and natural language.
   Check the `match.start` and `match.end` spans.

4. Cross-region isolation: a similar-shaped identifier from another region
   must not match this detector when called in isolation
   (`Scrubber(detectors=["xx_example"])`).

5. Stable token: the same value twice produces the same suffix, and
   normalised equivalents (spaced vs compact, mixed case) produce the same
   suffix.

Use the existing test files as templates. `tests/test_iban.py` is the most
complete reference. `tests/test_es.py` shows the multi-detector country
layout.

## 4. Add a default-scrubber regression entry

Append one row to the `DEFAULT_VECTORS` list in
[tests/test_default_scrubber_integration.py](../tests/test_default_scrubber_integration.py).
This is the test that would have caught the shadowing bug fixed before 0.2.0.
Every new detector must include an entry so future contributors cannot break
existing detectors by adding overlapping patterns.

```python
DEFAULT_VECTORS = [
    ...,
    ("xx_example", "AB123456"),  # valid per stdnum.xx.example test data
]
```

If your detector legitimately validates a value that another existing
detector also validates (same algorithm, or your detector is a special case
of an EU VAT), add the entry to `AMBIGUOUS_VECTORS` instead of
`DEFAULT_VECTORS`.

## 5. Run the suite

```sh
python -m pytest -q
python -m mypy --strict src
python -m ruff check src tests
```

All three must pass. CI runs the same on push.

## 6. Regenerate the coverage page

```sh
python scripts/gen_coverage.py > docs/coverage.md
```

Commit the regenerated file alongside the detector. Reviewers diff this to
confirm the new detector landed in the right region with the right
default/feasibility flags.

## 7. CHANGELOG

Add a one-line entry under `## [Unreleased]` in
[CHANGELOG.md](../CHANGELOG.md):

```markdown
### Added
**XX (Example Country)**
- `xx_example` - Brief description (format, checksum, via python-stdnum.xx.example)
```
