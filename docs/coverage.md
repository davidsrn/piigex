# Coverage

piigex has 83 detectors across 25 regions. 67 of them are on by default. The other 16 are opt-in: phone numbers and shape-only identifiers, kept off because they produce more false positives.

Each detector pairs a pre-compiled regex with a checksum validator. Validators delegate to `python-stdnum` where possible and are hand-rolled otherwise. With `validate=True` (the default), only checksum-valid matches are redacted.

## Feasibility tiers

- high: distinctive shape and a strong checksum. Very low false-positive risk.
- medium: distinctive shape but weak or absent checksum, or a strong checksum with an ambiguous shape. Phone numbers and shape-only IDs fall here and are off by default.
- low: reserved for future detectors with high false-positive risk.

## Summary by region

| Region | Detectors | Default-on | Opt-in |
|---|---|---|---|
| Austria (`at`) | 1 | 1 | 0 |
| Belgium (`be`) | 6 | 4 | 2 |
| Bulgaria (`bg`) | 2 | 2 | 0 |
| Czech Republic (`cz`) | 2 | 2 | 0 |
| Germany (`de`) | 4 | 3 | 1 |
| Denmark (`dk`) | 2 | 2 | 0 |
| Estonia (`ee`) | 1 | 1 | 0 |
| Spain (`es`) | 9 | 6 | 3 |
| Finland (`fi`) | 2 | 2 | 0 |
| France (`fr`) | 7 | 5 | 2 |
| Greece (`gr`) | 1 | 1 | 0 |
| Croatia (`hr`) | 1 | 1 | 0 |
| Hungary (`hu`) | 1 | 1 | 0 |
| Ireland (`ie`) | 1 | 1 | 0 |
| International (`intl`) | 9 | 8 | 1 |
| Italy (`it`) | 3 | 2 | 1 |
| Lithuania (`lt`) | 1 | 1 | 0 |
| Netherlands (`nl`) | 4 | 2 | 2 |
| Poland (`pl`) | 3 | 3 | 0 |
| Portugal (`pt`) | 5 | 3 | 2 |
| Romania (`ro`) | 2 | 2 | 0 |
| Sweden (`se`) | 2 | 2 | 0 |
| Slovenia (`si`) | 2 | 2 | 0 |
| Slovakia (`sk`) | 1 | 1 | 0 |
| United States (`us`) | 11 | 9 | 2 |

## Detectors by region

### International (`intl`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `intl_bic` | `{{BIC}}` | high | on |
| `intl_credit_card` | `{{CREDIT_CARD}}` | high | on |
| `intl_email` | `{{EMAIL}}` | high | on |
| `intl_eu_vat` | `{{EU_VAT}}` | high | on |
| `intl_iban` | `{{IBAN}}` | high | on |
| `intl_ipv4` | `{{IPV4}}` | high | on |
| `intl_ipv6` | `{{IPV6}}` | high | on |
| `intl_mac` | `{{MAC}}` | high | on |
| `intl_phone_e164` | `{{INTL_PHONE_E164}}` | medium | off |

### Austria (`at`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `at_vnr` | `{{AT_VNR}}` | high | on |

### Belgium (`be`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `be_bis` | `{{BE_BIS}}` | high | on |
| `be_eid` | `{{BE_EID}}` | high | on |
| `be_nn` | `{{BE_NN}}` | high | on |
| `be_ogm_vcs_delimited` | `{{BE_OGM_VCS}}` | medium | off |
| `be_phone` | `{{BE_PHONE}}` | medium | off |
| `be_vat` | `{{BE_VAT}}` | high | on |

### Bulgaria (`bg`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `bg_egn` | `{{BG_EGN}}` | high | on |
| `bg_pnf` | `{{BG_PNF}}` | high | on |

### Czech Republic (`cz`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `cz_dic` | `{{CZ_DIC}}` | high | on |
| `cz_rc` | `{{CZ_RC}}` | high | on |

### Germany (`de`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `de_idnr` | `{{DE_IDNR}}` | high | on |
| `de_phone` | `{{DE_PHONE}}` | medium | off |
| `de_svnr` | `{{DE_SVNR}}` | high | on |
| `de_vat` | `{{DE_VAT}}` | high | on |

### Denmark (`dk`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `dk_cpr` | `{{DK_CPR}}` | high | on |
| `dk_cvr` | `{{DK_CVR}}` | high | on |

### Estonia (`ee`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `ee_ik` | `{{EE_IK}}` | high | on |

### Spain (`es`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `es_ccc` | `{{ES_CCC}}` | high | on |
| `es_cif` | `{{ES_CIF}}` | high | on |
| `es_dni` | `{{ES_DNI}}` | high | on |
| `es_matricula` | `{{ES_MATRICULA}}` | medium | off |
| `es_nie` | `{{ES_NIE}}` | high | on |
| `es_nss` | `{{ES_NSS}}` | high | on |
| `es_passport` | `{{ES_PASSPORT}}` | medium | off |
| `es_phone` | `{{ES_PHONE}}` | medium | off |
| `es_referencia_catastral` | `{{ES_CATASTRO}}` | high | on |

### Finland (`fi`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `fi_hetu` | `{{FI_HETU}}` | high | on |
| `fi_ytunnus` | `{{FI_YTUNNUS}}` | high | on |

### France (`fr`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `fr_cni` | `{{FR_CNI}}` | medium | off |
| `fr_nif` | `{{FR_NIF}}` | high | on |
| `fr_nir` | `{{FR_NIR}}` | high | on |
| `fr_phone` | `{{FR_PHONE}}` | medium | off |
| `fr_siren` | `{{FR_SIREN}}` | high | on |
| `fr_siret` | `{{FR_SIRET}}` | high | on |
| `fr_tva` | `{{FR_TVA}}` | high | on |

### Greece (`gr`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `gr_amka` | `{{GR_AMKA}}` | high | on |

### Croatia (`hr`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `hr_oib` | `{{HR_OIB}}` | high | on |

### Hungary (`hu`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `hu_anum` | `{{HU_ANUM}}` | high | on |

### Ireland (`ie`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `ie_pps` | `{{IE_PPS}}` | high | on |

### Italy (`it`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `it_codice_fiscale` | `{{IT_CF}}` | high | on |
| `it_partita_iva` | `{{IT_IVA}}` | high | on |
| `it_phone` | `{{IT_PHONE}}` | medium | off |

### Lithuania (`lt`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `lt_asmens` | `{{LT_ASMENS}}` | high | on |

### Netherlands (`nl`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `nl_bsn` | `{{NL_BSN}}` | high | on |
| `nl_btw` | `{{NL_BTW}}` | high | on |
| `nl_passport` | `{{NL_PASSPORT}}` | medium | off |
| `nl_phone` | `{{NL_PHONE}}` | medium | off |

### Poland (`pl`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `pl_nip` | `{{PL_NIP}}` | high | on |
| `pl_pesel` | `{{PL_PESEL}}` | high | on |
| `pl_regon` | `{{PL_REGON}}` | high | on |

### Portugal (`pt`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `pt_cc` | `{{PT_CC}}` | high | on |
| `pt_nif` | `{{PT_NIF}}` | high | on |
| `pt_niss` | `{{PT_NISS}}` | high | on |
| `pt_passport` | `{{PT_PASSPORT}}` | medium | off |
| `pt_phone` | `{{PT_PHONE}}` | medium | off |

### Romania (`ro`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `ro_cf` | `{{RO_CF}}` | high | on |
| `ro_cnp` | `{{RO_CNP}}` | high | on |

### Sweden (`se`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `se_orgnr` | `{{SE_ORGNR}}` | high | on |
| `se_personnummer` | `{{SE_PERSONNUMMER}}` | high | on |

### Slovenia (`si`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `si_emso` | `{{SI_EMSO}}` | high | on |
| `si_maticna` | `{{SI_MATICNA}}` | high | on |

### Slovakia (`sk`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `sk_rc` | `{{SK_RC}}` | high | on |

### United States (`us`)

| Detector name | Token | Feasibility | Default |
|---|---|---|---|
| `us_atin` | `{{US_ATIN}}` | high | on |
| `us_dea` | `{{US_DEA}}` | high | on |
| `us_ein` | `{{US_EIN}}` | high | on |
| `us_itin` | `{{US_ITIN}}` | high | on |
| `us_mbi` | `{{US_MBI}}` | high | on |
| `us_npi` | `{{US_NPI}}` | high | on |
| `us_passport` | `{{US_PASSPORT}}` | medium | off |
| `us_phone` | `{{US_PHONE}}` | medium | off |
| `us_ptin` | `{{US_PTIN}}` | high | on |
| `us_rtn` | `{{US_RTN}}` | high | on |
| `us_ssn` | `{{US_SSN}}` | high | on |

## Notes on opt-in detectors

Phone numbers and shape-only identifiers (passports, vehicle plates, French CNI, Belgian payment references) are off by default. They either lack a strong checksum or share a shape with plenty of non-PII strings. Enable them by name:

```python
from piigex import Scrubber

s = Scrubber(detectors=["us_phone", "us_passport", "intl_phone_e164"])
```

`min_feasibility` and `regions` only narrow the default set; they do not promote a `default_enabled=False` detector into the active set. Always pass opt-in detectors by name.

## Regenerating this page

This file is generated from the live detector registry. After you add or modify a detector, regenerate it with:

```sh
python scripts/gen_coverage.py > docs/coverage.md
```
