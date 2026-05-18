# piigex

A small PII detection and redaction library for structured identifiers. It uses regex
plus checksum validation. There is no ML model, no NLP pipeline, and no large dependency tree.

Use it to sanitize chatbot input before it hits an LLM, scrub logs, or redact customer
support transcripts. Coverage includes the 7 major EU countries, the United States, and
international identifiers like IBAN, BIC, credit cards, email, IP addresses, and MAC
addresses.

---

## Quickstart

```python
from piigex import clean, scan

clean("Send payment to ES91 2100 0418 4502 0005 1332 by Friday")
# → "Send payment to {{IBAN}} by Friday"

scan("IBAN: DE89370400440532013000")
# → [Match(name='intl_iban', token='IBAN', start=6, end=28,
#          value='DE89370400440532013000', valid=True)]

# Fine-grained control
from piigex import Scrubber
s = Scrubber(regions=["es", "intl"], stable_tokens=True)
s.clean("DNI 12345678Z and card 4111 1111 1111 1111")
# → "DNI {{ES_DNI_1}} and card {{CREDIT_CARD_1}}"
```

---

## JSON / dict payloads

`clean_json` and `scan_json` walk nested dicts, lists, and tuples. They only touch
string values; keys, numbers, booleans, and the overall structure are left untouched.
`scan_json` returns each `Match` with a dotted `path` showing where the PII was found.

```python
import piigex

payload = {
    "user": {"email": "alice@example.com", "iban": "GB29NWBK60161331926819"},
    "amount": 100,
}

piigex.clean_json(payload)
# → {"user": {"email": "{{EMAIL}}", "iban": "{{IBAN}}"}, "amount": 100}

for m in piigex.scan_json(payload):
    print(f"{m.path}: {m.name}")
# user.email: intl_email
# user.iban:  intl_iban
```

The CLI exposes the same behaviour with `--json`:

```sh
cat payload.json | piigex scrub --json
cat payload.json | piigex scan  --json    # match list with "path" field
```

---

## Coverage

81 detectors across 28 regions. 67 Tier-1 identifiers are on by default. The other 14
(phone numbers and low-risk shape-only IDs) are off, since they produce more false
positives. Turn them on explicitly with `detectors=[...]` or `regions=[...]`.

| Region | Default-on detectors |
|--------|---------------------|
| ES | `es_dni`, `es_nie`, `es_cif`, `es_nss`, `es_ccc`, `es_referencia_catastral` |
| IT | `it_codice_fiscale`, `it_partita_iva` |
| FR | `fr_nir`, `fr_nif`, `fr_siren`, `fr_siret`, `fr_tva` |
| DE | `de_idnr`, `de_vat`, `de_svnr` |
| PT | `pt_nif`, `pt_cc`, `pt_niss` |
| NL | `nl_bsn`, `nl_btw` |
| BE | `be_nn`, `be_bis`, `be_vat`, `be_eid` |
| AT | `at_vnr` |
| BG | `bg_egn`, `bg_pnf` |
| HR | `hr_oib` |
| CZ | `cz_rc`, `cz_dic` |
| DK | `dk_cpr`, `dk_cvr` |
| EE | `ee_ik` |
| FI | `fi_hetu`, `fi_ytunnus` |
| GR | `gr_amka` |
| HU | `hu_anum` |
| IE | `ie_pps` |
| LT | `lt_asmens` |
| PL | `pl_pesel`, `pl_nip`, `pl_regon` |
| RO | `ro_cnp`, `ro_cf` |
| SK | `sk_rc` |
| SI | `si_emso`, `si_maticna` |
| SE | `se_personnummer`, `se_orgnr` |
| US | `us_ssn`, `us_ein`, `us_itin`, `us_atin`, `us_ptin`, `us_rtn`, `us_npi`, `us_dea`, `us_mbi` |
| intl | `intl_iban`, `intl_eu_vat`, `intl_bic`, `intl_credit_card`, `intl_email`, `intl_ipv4`, `intl_ipv6`, `intl_mac` |

Countries with VAT coverage only (via `intl_eu_vat`): CY, LV, LU, MT.

Opt-in detectors (default disabled, `feasibility="medium"`):
- Phone: `intl_phone_e164`, `es_phone`, `it_phone`, `fr_phone`, `de_phone`, `pt_phone`, `nl_phone`, `be_phone`
- Shape-only IDs: `es_passport`, `es_matricula`, `fr_cni`, `pt_passport`, `nl_passport`, `be_ogm_vcs_delimited`

Enable them by name (`detectors=["es_passport", ...]`) or by region. They stay off by
default because phone numbers and shape-only IDs are noisier.

The internals are country-agnostic, so adding a new region means dropping detector
modules under `src/piigex/detectors/<iso2>/`. UK coverage is on the v0.3.0 roadmap.

---

## Comparison

Install sizes measured with `du -sh` against a clean venv (baseline pip/setuptools
excluded), Python 3.13. Presidio spaCy model (`en_core_web_lg`, downloaded separately)
adds a further 560 MB.

| Library | Approach | Net install size | Structured IDs | Requires ML |
|---------|----------|------------------|----------------|-------------|
| **piigex** | regex + checksum | **~6 MB** | 81 (67 default + 14 opt-in) | No |
| commonregex | regex only | ~6 KB | None | No |
| piiregex | regex only | ~4 KB | None | No |
| scrubadub | regex + optional NLP | ~335 MB | Limited (IBAN only) | Optional |
| Microsoft Presidio | NLP + ML | ~200 MB + model | Via custom recognizers | Yes (default) |

Size breakdown for piigex: `python-stdnum` is 5.7 MB and the piigex source itself is
about 150 KB. scrubadub 2.x pulls in scipy, numpy, scikit-learn, phonenumbers, faker,
nltk, regex, and dateparser as transitive dependencies. Most of its install weight is
that ML/data stack, not the detection code.

---

## API reference

```python
from piigex import Scrubber, clean, scan, Match

# Module-level convenience (uses the default Scrubber: all high/medium detectors)
scan(text: str) -> list[Match]
clean(text: str) -> str

# Configurable scrubber
s = Scrubber(
    detectors=None,            # None = default set; or ["es_dni", "intl_iban"]
    exclude=None,              # detector names to exclude from the default set
    regions=None,              # ["es", "intl"]: None = all regions
    min_feasibility="medium",  # "high" | "medium" | "low"
    validate=True,             # False = shape-only, skip checksum
    stable_tokens=False,       # True → same value → same numbered token per call
    token_format="{{{name}}}", # produces {{TOKEN}} by default
    token_map=None,            # pass a persistent TokenMap to share state across calls
)

# Match fields (frozen dataclass)
Match(name, token, start, end, value, valid, path)
#     str   str    int   int  str   bool   str   # path populated by scan_json only
```

### Validation behaviour

`validate=True` (default): regex locates, checksum confirms. Matches with invalid checksums
are returned with `valid=False` and are **not** replaced by `clean()`.

`validate=False`: shape-match only. This is useful for catching likely PII even when
the value is truncated or encoded.

### Stable tokens

```python
s = Scrubber(stable_tokens=True)
s.clean("NIE X1234567L appears again as X1234567L")
# → "NIE {{ES_NIE_1}} appears again as {{ES_NIE_1}}"
```

Normalized equivalents (e.g. spaced vs. compact IBAN) map to the same token index.
The counter resets each `clean()` call unless you pass a persistent `TokenMap`:

```python
from piigex.tokens import TokenMap
tm = TokenMap()
s.clean(doc1, token_map=tm)
s.clean(doc2, token_map=tm)  # same values → same indices across both docs
```

---

## When NOT to use this library

piigex only detects structured identifiers: tax codes, account numbers, social security
numbers, and other formats that have a defined shape and a checksum algorithm.

It will not detect:
- Names, organizations, or postal addresses (no NER)
- Dates of birth written in natural language
- Free-form sensitive content

If you need any of that, look at [Microsoft Presidio](https://microsoft.github.io/presidio/)
or a spaCy-based NER pipeline. Those tools require ML models. piigex deliberately does not.

---

## Documentation

- [docs/index.md](docs/index.md): landing page and design overview
- [docs/coverage.md](docs/coverage.md): every detector grouped by region
- [docs/api.md](docs/api.md): Python API reference
- [docs/cli.md](docs/cli.md): command-line usage
- [docs/extending.md](docs/extending.md): how to add a new detector

---

## Scope

Structured identifiers only. No NER, no ML. EU and US country coverage; UK on the
roadmap. The only runtime dependency is `python-stdnum`.
