# Python API

All public names are re-exported from the top-level `piigex` package.

```python
from piigex import Scrubber, clean, scan, clean_json, scan_json, Match
```

The package includes a `py.typed` marker, so all signatures below are visible
to `mypy --strict` consumers with no extra configuration.

## Module-level convenience

For one-shot redaction with the default detector set:

```python
piigex.scan(text: str) -> list[Match]
piigex.clean(text: str) -> str
piigex.scan_json(obj: Any) -> list[Match]
piigex.clean_json(obj: Any) -> Any
```

These use a shared `Scrubber()` that is initialised lazily. The construction is
thread-safe: the first call takes the lock, and every other call hits the
cached instance.

## `Scrubber`

```python
Scrubber(
    detectors: list[str] | None = None,
    *,
    exclude: list[str] | None = None,
    regions: list[str] | None = None,
    min_feasibility: str = "medium",
    validate: bool = True,
    stable_tokens: bool = False,
    token_format: str = "{{{name}}}",
    token_map: TokenMap | None = None,
)
```

### Filtering which detectors run

| Parameter | Behaviour |
|---|---|
| `detectors=None` (default) | use the default set (every detector with `default_enabled=True`, further filtered by `regions` and `min_feasibility`) |
| `detectors=["es_dni", "intl_iban"]` | use only these detectors, regardless of their `default_enabled` flag |
| `exclude=["intl_email", "intl_ipv4"]` | remove names from whichever set is selected |
| `regions=["es", "intl"]` | restrict the default set to these ISO-2 region codes (no effect when `detectors=` is explicit) |
| `min_feasibility="high"` | drop any default detector with feasibility weaker than `high` (no effect when `detectors=` is explicit) |

### Validation

- `validate=True` (default): the regex finds candidates, the validator confirms
  the checksum, and `clean()` only redacts when both pass. The scanner still
  returns invalid matches with `valid=False` so callers can inspect them.
- `validate=False`: every candidate is treated as valid for redaction purposes
  by `clean()`. `Match.valid` still reflects the real checksum result, so
  callers can tell shape-only matches apart from checksum-valid ones.

### Tokens

`token_format` controls the placeholder string. The token name is substituted
for `{name}`:

```python
Scrubber(token_format="{{{name}}}")  # default -> {{ES_DNI}}, {{IBAN}}
Scrubber(token_format="[{name}]")    # -> [ES_DNI], [IBAN]
Scrubber(token_format="<<{name}>>")  # -> <<ES_DNI>>, <<IBAN>>
```

With `stable_tokens=True`, repeated occurrences of the same normalised value
share the same numeric suffix within one `clean()` call:

```python
s = Scrubber(stable_tokens=True)
s.clean("NIE X1234567L appears again as X1234567L")
# -> "NIE {{ES_NIE_1}} appears again as {{ES_NIE_1}}"
```

Normalisation strips separators (spaces, dots, dashes) and lowercases the
value, so the spaced and compact IBAN forms share a token index:

```python
s.clean("Compare ES91 2100 0418 4502 0005 1332 with ES9121000418450200051332")
# -> "Compare {{IBAN_1}} with {{IBAN_1}}"
```

For state that persists across `clean()` calls, pass a `TokenMap`:

```python
from piigex.tokens import TokenMap

tm = TokenMap()
s = Scrubber(stable_tokens=True, token_map=tm)
s.clean(doc1)  # values get tokens 1, 2, 3...
s.clean(doc2)  # same values across docs reuse those indices
```

## `Match`

```python
@dataclass(frozen=True)
class Match:
    name: str    # detector name, e.g. "es_dni"
    token: str   # placeholder token, e.g. "ES_DNI"
    start: int   # offset in the input string
    end: int
    value: str   # the matched substring
    valid: bool  # checksum result (always populated)
    path: str    # JSON path, populated by scan_json only
```

## `Scrubber.scan` / `Scrubber.clean`

```python
Scrubber.scan(text: str) -> list[Match]
Scrubber.clean(text: str, *, token_map: TokenMap | None = None) -> str
```

`scan()` returns every candidate, validated or not, in left-to-right order
without overlap. `clean()` only redacts the validated ones, unless the scrubber
was created with `validate=False`.

The per-call `token_map=` on `clean()` overrides the scrubber's persistent
token map for that call only. Use it when you want a stable-token document
boundary without rebuilding the scrubber.

## `Scrubber.scan_json` / `Scrubber.clean_json`

```python
Scrubber.scan_json(obj: Any) -> list[Match]
Scrubber.clean_json(obj: Any) -> Any
```

Both walk nested dicts, lists, and tuples. They only touch string values.
Keys, numbers, booleans, `None`, and the surrounding structure are preserved.
Unknown types pass through unchanged.

`scan_json` populates `Match.path` with a dotted path showing where the PII
was found:

```python
payload = {"user": {"email": "alice@example.com"}, "amounts": [100, 200]}
for m in piigex.scan_json(payload):
    print(m.path, m.name)
# user.email intl_email
```

Keys that contain `.`, `[`, or `]` are bracket-quoted in the path
(`segment["weird.key"]`) so the segments stay unambiguous.

## `TokenMap`

```python
from piigex.tokens import TokenMap

tm = TokenMap()
tm.get("intl_iban", "es9121000418450200051332")  # -> 1 (first time)
tm.get("intl_iban", "es9121000418450200051332")  # -> 1 (same input)
tm.get("intl_iban", "de89370400440532013000")    # -> 2 (new input)
tm.reset()  # counters and seen-set cleared
```

## Registry helpers

```python
from piigex.detectors import get_registry, get_detectors

registry = get_registry()              # dict[str, Detector] of all loaded detectors
default_set = get_detectors()          # the same filtering Scrubber() would apply
es_only = get_detectors(regions=["es"])
```

`get_detectors` accepts the same `names`, `regions`, `min_feasibility`, and
`exclude` arguments as `Scrubber.__init__`.
