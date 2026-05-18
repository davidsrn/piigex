# Security Policy

piigex processes and redacts personal data. Responsible disclosure of security
issues is appreciated.

## Reporting a vulnerability

Please report security issues through
[GitHub Security Advisories](https://github.com/davidsrn/piigex/security/advisories/new)
rather than a public issue. This keeps the report private until a fix is available.
Do not include real personal data (names, ID numbers, account details) in any report.

## Scope

Bypass vectors that cause silent under-redaction — inputs that should be
detected and redacted but are not — are in scope. False positives (values
flagged incorrectly) and false negatives on edge-case inputs that the library
does not claim to cover are not security issues; open a regular issue for those.
