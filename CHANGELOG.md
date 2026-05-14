# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **US region** with nine Tier-1 detectors, all default-on with
  `feasibility="high"`:
  - `us_ssn`: Social Security Number. stdnum-backed. Rejects reserved
    areas (000, 666, 9xx), group 00, serial 0000, and the known
    promotional numbers. Accepts hyphenated and compact forms.
  - `us_ein`: Employer Identification Number. stdnum-backed; enforces
    the IRS prefix table. Hyphenated form only; the compact 9-digit
    form would collide with `us_rtn` and `us_ssn`.
  - `us_itin`: Individual Taxpayer Identification Number. stdnum-backed.
    Requires the 9xx area and an IRS-published middle group (70-99
    excluding 89 and 93).
  - `us_atin`: Adoption Taxpayer Identification Number. Hand-rolled to
    enforce the IRS-reserved middle group 93; `stdnum.us.atin` is
    shape-only and would otherwise tag any 9-digit value failing
    SSN/EIN/ITIN.
  - `us_ptin`: Preparer Tax Identification Number. stdnum-backed.
    Literal `P` + 8 digits.
  - `us_rtn`: ABA Routing Transit Number. stdnum-backed; ABA weighted
    checksum.
  - `us_npi`: National Provider Identifier. Hand-rolled. Runs Luhn over
    the ISO 7812 issuer prefix `80840` followed by the 9 leading digits.
  - `us_dea`: DEA registration number. Hand-rolled checksum: last digit
    of `d1+d3+d5 + 2*(d2+d4+d6)` equals d7.
  - `us_mbi`: Medicare Beneficiary Identifier. Hand-rolled shape
    validator. Digits and letters sit at fixed positions; the letter
    alphabet drops S, L, O, I, B, and Z per CMS.
- `scripts/gen_coverage.py` now recognizes `us` as United States.

## [0.1.0] - 2026-05-14

Initial public release.

### Added

#### Engine and public API

- Single-pass scan engine with longest-validated-match resolution: builds one
  combined alternation regex over all enabled detectors, runs `re.search` per
  candidate position, picks the longest detector match whose validator passes.
  Resolves the shadowing problem that arises when multiple detectors share an
  identical/subset pattern (e.g. `\d{11}` is shared by `be_bis`, `be_nn`,
  `gr_amka`, `hr_oib`, `it_partita_iva`, `pl_pesel`).
- `Scrubber`, `clean`, `scan`, `clean_json`, `scan_json`: public entry points.
- `Match` frozen dataclass: `name`, `token`, `start`, `end`, `value`, `valid`,
  `path` (populated by `scan_json`).
- `TokenMap` for stable token numbering: per-call by default, persistable
  across calls when passed via `token_map=`.
- Thread-safe lazy default scrubber for module-level `clean()` / `scan()`.
- Detector registry with sorted auto-discovery under
  `src/piigex/detectors/<iso2>/`.

#### Detectors: 72 across 24 regions (58 default-on, 14 opt-in)

Full per-detector list with feasibility and default-on/opt-in status in
[docs/coverage.md](docs/coverage.md).

- **International (intl):** `intl_iban`, `intl_bic`, `intl_eu_vat`,
  `intl_credit_card`, `intl_email`, `intl_ipv4`, `intl_ipv6`, `intl_mac`;
  plus `intl_phone_e164` (opt-in).
- **Spain (es):** `es_dni`, `es_nie`, `es_cif`, `es_nss`, `es_ccc`,
  `es_referencia_catastral`; plus `es_passport`, `es_matricula`, `es_phone`
  (opt-in).
- **Italy (it):** `it_codice_fiscale`, `it_partita_iva`; plus `it_phone`
  (opt-in).
- **France (fr):** `fr_nir`, `fr_nif`, `fr_siren`, `fr_siret`, `fr_tva`;
  plus `fr_cni`, `fr_phone` (opt-in).
- **Germany (de):** `de_idnr`, `de_vat`, `de_svnr`; plus `de_phone` (opt-in).
- **Portugal (pt):** `pt_nif`, `pt_cc`, `pt_niss`; plus `pt_passport`,
  `pt_phone` (opt-in).
- **Netherlands (nl):** `nl_bsn`, `nl_btw`; plus `nl_passport`, `nl_phone`
  (opt-in).
- **Belgium (be):** `be_nn`, `be_bis`, `be_vat`, `be_eid`; plus
  `be_ogm_vcs_delimited`, `be_phone` (opt-in).
- **Austria (at), Bulgaria (bg), Croatia (hr), Czech Republic (cz),
  Denmark (dk), Estonia (ee), Finland (fi), Greece (gr), Hungary (hu),
  Ireland (ie), Lithuania (lt), Poland (pl), Romania (ro), Sweden (se),
  Slovenia (si), Slovakia (sk):** structured tax IDs, social-security
  numbers, company registration codes, and similar, all stdnum-backed.

#### JSON / dict-aware scanning

- `Scrubber.clean_json(obj)` and `Scrubber.scan_json(obj)` walk nested dicts,
  lists, and tuples; scrub only string values; preserve keys, numbers,
  booleans, and structure.
- Top-level convenience functions `piigex.clean_json` and `piigex.scan_json`.
- `Match.path` is a dotted JSON path; dict keys containing `.`, `[`, or `]`
  are bracket-quoted.

#### Command-line interface

- `piigex scrub`: read stdin, write redacted output to stdout.
- `piigex scan`: read stdin, write a JSON array of matches to stdout.
- Common flags: `--regions`, `--detectors`, `--exclude`, `--min-feasibility`,
  `--no-validate`, `--json`.
- `scrub`-only flags: `--stable-tokens`, `--token-format`.
- Runnable as `piigex` (entry point) or `python -m piigex`.

#### Project hygiene

- `py.typed` marker shipped in the wheel; the package is `mypy --strict`
  clean.
- pre-commit configuration: ruff (lint + format), mypy --strict.
- GitHub Actions CI: lint, typecheck, test matrix on Python 3.10-3.13.
- Coverage gate at 90% (current: ~96%).
- Documentation: API reference, CLI reference, extending guide, auto-generated
  coverage matrix.
- Examples: chatbot input filter, log scrubber, CSV column scrubber, JSON
  payload scrubber.
