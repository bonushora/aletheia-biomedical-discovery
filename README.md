# Aletheia Biomedical Discovery

Local architecture and first executable federation contract for an evidence-governed biomedical discovery platform.

This repository is intentionally documentation-first. It does **not** modify biomedical data or the existing kidney research repository. ADR-0016 and ADR-0017 are `Accepted` by explicit human authority; every other foundation ADR remains `Proposed`.

## Local qualification state

Target: `GREEN_ALETHEIA_FIRST_QUALIFIED_CONSUMER_REGISTERED`

This state means the ADR and contract foundation remains qualified and Kidney is registered as the first exact-SHA, local qualified consumer of the RCP Descriptor v0.1.0 contract. It does **not** mean the Kidney qualification branch was merged, scientific or clinical validation occurred, therapeutic efficacy was established, or any repository was remotely published.

## Structure

- `docs/adr/` — platform-level ADRs.
- `modules/kidney/docs/adr/` — Kidney Regeneration Research Control Plane ADRs.
- `docs/architecture/` — derived architecture summaries.
- `contracts/research-control-plane-descriptor/0.1.0/` — first executable federation contract.
- `schemas/research-control-plane-descriptor/0.1.0/` — its normative structural schema and illustrative example.
- `evidence-packages/` — future versioned evidence-package boundary; no executable evidence-package schema is established.
- `control-planes/` — conceptual Research Control Plane boundary.
- `scripts/validate_foundation.py` — local structural and invariant validation.
- `scripts/validate_accepted_adr_history.py` — accepted-decision continuity against an explicit Git base.
- `scripts/verify_evidence_zip.py` — generic ZIP container-safety verification.
- `scripts/validate_rcp_descriptor.py` — stdlib-only RCP Descriptor validation.
- `scripts/validate_consumer_registry.py` — stdlib-only exact-SHA registry/matrix validation.
- `tests/contracts/` — unit and adversarial contract qualification.
- `tests/foundation-hardening/` — independent synthetic adversarial qualification corpus.
- `docs/security/` — scope and attack-model documentation.
- `evidence/foundation-v01/` — baseline, decisions, validation, manifest, and snapshot evidence.

## Authority boundary

Architecture may define what evidence and human approval are required. Architecture must not silently encode temporary scientific thresholds as immutable system truth.
