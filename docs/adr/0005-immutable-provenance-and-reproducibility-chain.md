# ADR-0005 — Immutable Provenance and Reproducibility Chain

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Provenance

## Context
Biomedical results are difficult to interpret if source identity, transformations, software versions, parameters, or operator actions cannot be reconstructed.

## Decision
Aletheia will treat provenance as a first-class graph rather than a narrative afterthought. Every governed transformation SHOULD record immutable or content-addressed identifiers for inputs and important outputs; source location and acquisition metadata; transformation identity and version; parameters/configuration; software and environment identity; actor/agent identity and authority context; timestamps where relevant; predecessor/successor relationships; and verification state.

The internal model SHOULD be compatible with W3C PROV concepts (`Entity`, `Activity`, `Agent`) and SHOULD permit export into a research-object package such as RO-Crate.

Hashes demonstrate byte identity, not biological equivalence or semantic validity.

## Consequences
Reconstruction and auditing become possible, while storage and metadata overhead increase.
