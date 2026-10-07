# Aletheia Biomedical Discovery

Local architecture foundation for an evidence-governed biomedical discovery platform.

This repository is intentionally documentation-first. It does **not** modify biomedical data, production code, or the existing kidney research repository. ADR-0016 is `Accepted` by explicit human authority; every other foundation ADR remains `Proposed`.

## Local qualification state

Target: `GREEN_ALETHEIA_FOUNDATION_HARDENING_V01`

This state means the ADR set is structurally complete, internally cross-referenced, locally validated, hashed, committed in its own repository, and governed by the accepted federated topology. It does **not** mean scientific validation, clinical validation, remote publication, release, or compatibility with untested future control planes.

## Structure

- `docs/adr/` — platform-level ADRs.
- `modules/kidney/docs/adr/` — Kidney Regeneration Research Control Plane ADRs.
- `docs/architecture/` — derived architecture summaries.
- `contracts/`, `schemas/`, and `evidence-packages/` — versioned federation scaffolding.
- `control-planes/` — conceptual Research Control Plane boundary.
- `scripts/validate_foundation.py` — local structural and invariant validation.
- `scripts/validate_accepted_adr_history.py` — accepted-decision continuity against an explicit Git base.
- `scripts/verify_evidence_zip.py` — generic ZIP container-safety verification.
- `tests/foundation-hardening/` — independent synthetic adversarial qualification corpus.
- `docs/security/` — scope and attack-model documentation.
- `evidence/foundation-v01/` — baseline, decisions, validation, manifest, and snapshot evidence.

## Authority boundary

Architecture may define what evidence and human approval are required. Architecture must not silently encode temporary scientific thresholds as immutable system truth.
