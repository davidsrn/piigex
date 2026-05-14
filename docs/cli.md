# Command-line interface

The package installs a `piigex` console script and is also runnable as
`python -m piigex`. Both forms expose two subcommands:

```text
piigex scrub   # read stdin, write the redacted output to stdout
piigex scan    # read stdin, write JSON matches to stdout
```

## `piigex scrub`

Replaces every validated PII match with its placeholder token.

```sh
echo "DNI 12345678Z and IBAN GB29NWBK60161331926819" | piigex scrub
# DNI {{ES_DNI}} and IBAN {{IBAN}}
```

### Options

| Flag | Description |
|---|---|
| `--detectors NAME[,NAME...]` | run only the named detectors (overrides defaults) |
| `--exclude NAME[,NAME...]` | drop named detectors from the active set |
| `--regions CODE[,CODE...]` | restrict the default set to these ISO-2 region codes (e.g. `es,intl`) |
| `--min-feasibility {high,medium,low}` | drop default detectors weaker than this tier (default: `medium`) |
| `--no-validate` | skip checksum validation; redact every shape-level match |
| `--stable-tokens` | replace repeated values with `{{TOKEN_1}}`, `{{TOKEN_2}}`, ... (per stdin) |
| `--token-format FORMAT` | placeholder template. `{name}` is replaced by the token (default `{{{name}}}`) |
| `--json` | parse stdin as JSON; scrub string values, preserve structure |

### Examples

Region-scoped scrub:

```sh
cat customer-notes.txt | piigex scrub --regions es,intl
```

Stable tokens for log correlation:

```sh
cat app.log | piigex scrub --stable-tokens > scrubbed.log
```

Custom token shape:

```sh
echo "Card 4111111111111111" | piigex scrub --token-format '[REDACTED:{name}]'
# Card [REDACTED:CREDIT_CARD]
```

JSON in, JSON out:

```sh
cat payload.json | piigex scrub --json
```

## `piigex scan`

Reports each match as a JSON object on stdout. Does not modify the input.

```sh
echo "Email: alice@example.com" | piigex scan
# [{"name": "intl_email", "token": "EMAIL", "start": 7, "end": 24,
#   "value": "alice@example.com", "valid": true, "path": ""}]
```

### Options

`scan` accepts the same filtering flags as `scrub`: `--detectors`,
`--exclude`, `--regions`, `--min-feasibility`, `--no-validate`, `--json`. The
output is a JSON array of matches.

With `--json`, the input is parsed as JSON, the structure is walked, and the
`path` field on each match indicates where the value was found:

```sh
echo '{"user": {"iban": "GB29NWBK60161331926819"}}' | piigex scan --json
# [{"name": "intl_iban", ..., "path": "user.iban"}]
```

## Exit codes

`0` on success. Argparse-driven argument errors return `2`. Validation
failures inside a payload do not affect the exit code. They just produce
matches with `valid: false`.

## Piping patterns

Scrub a directory of logs in place (Unix):

```sh
for f in logs/*.log; do
  piigex scrub < "$f" > "$f.scrubbed" && mv "$f.scrubbed" "$f"
done
```

Pre-process before sending to an LLM:

```sh
read -r prompt
echo "$prompt" | piigex scrub | curl -d @- https://api.example.com/chat
```
