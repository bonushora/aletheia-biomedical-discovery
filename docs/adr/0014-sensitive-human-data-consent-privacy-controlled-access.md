# ADR-0014 — Sensitive Human Data, Consent, Privacy, and Controlled Access

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Data governance

## Context
Future Aletheia modules may process human genomic, transcriptomic, clinical, or other sensitive data. Technical access does not automatically imply ethical or legal permission to reuse data for every purpose.

## Decision
Aletheia SHALL separate data possession from data authority.

For sensitive human data, workflows must support dataset-specific use restrictions, consent/use-basis metadata where available, least-privilege access, controlled export and packaging, redaction/de-identification boundaries, audit of access and derived disclosures, and prohibition on republishing protected raw data merely because it was computationally processed.

Public, de-identified, controlled-access, and locally restricted data must remain distinguishable.

## Consequences
Some cross-dataset analyses may be blocked or require different execution environments. This is preferable to unauthorized reuse.
