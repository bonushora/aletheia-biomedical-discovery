# Aletheia Biomedical Discovery

Local architecture foundation for an evidence-governed biomedical discovery platform.

This repository is intentionally documentation-first. It does **not** modify biomedical data, production code, or the existing kidney research repository. ADR-0016 is `Accepted` by explicit human authority; every other foundation ADR remains `Proposed`.

## Local qualification state

Target: `GREEN_ALETHEIA_ADR_FOUNDATION_INTEGRATED`

This state means the ADR set is structurally complete, internally cross-referenced, locally validated, hashed, committed in its own repository, and governed by the accepted federated topology. It does **not** mean scientific validation, clinical validation, remote publication, release, or compatibility with untested future control planes.

## Structure

- `docs/adr/` — platform-level ADRs.
- `modules/kidney/docs/adr/` — Kidney Regeneration Research Control Plane ADRs.
- `docs/architecture/` — derived architecture summaries.
- `contracts/`, `schemas/`, and `evidence-packages/` — versioned federation scaffolding.
- `control-planes/` — conceptual Research Control Plane boundary.
- `scripts/validate_foundation.py` — local structural and invariant validation.
- `evidence/foundation-v01/` — baseline, decisions, validation, manifest, and snapshot evidence.

## Authority boundary

Architecture may define what evidence and human approval are required. Architecture must not silently encode temporary scientific thresholds as immutable system truth.
