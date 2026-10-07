# ADR-0012 — Reproducible Scientific Packaging and Review Artifacts

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Evidence packaging

## Context
A result that exists only in a transient notebook or terminal log is hard to review, reproduce, or preserve.

## Decision
Material scientific missions SHALL produce a review package containing, as applicable: human-readable report, machine-readable result/state, source inventory, commands/workflow record, environment identity, policy/decision references, limitations and unresolved questions, manifest with sizes and cryptographic hashes, and package integrity verification.

Aletheia SHOULD support RO-Crate 1.3 compatible export for research-object metadata while retaining its own stricter domain invariants where necessary.

Packages must not include sensitive or large raw data by default when references/hashes are sufficient.

## Consequences
Review and exchange become more reliable. Packaging is a governed output, not an afterthought.
