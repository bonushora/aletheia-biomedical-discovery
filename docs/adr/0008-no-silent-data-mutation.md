# ADR-0008 — No Silent Data Mutation

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Data integrity

## Context
Filtering, normalization, imputation, annotation, integration, and feature transformation can irreversibly change the analytical meaning of a dataset if performed in place.

## Decision
Source and qualified input objects are immutable within Aletheia workflows.

Any scientifically meaningful transformation MUST create a new derived object with explicit parent identity, transformation description, parameters and policy version, transformation software identity, manifest/hash where appropriate, and reversible linkage to the source.

No pipeline may silently overwrite a qualified source artifact.

## Consequences
Storage use increases, but provenance and rollback remain possible and scientific review can distinguish source from derived representations.
