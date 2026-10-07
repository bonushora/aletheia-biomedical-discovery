# ADR-0011 — External Literature and Dataset Trust Model

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** External evidence

## Context
External sources vary in authority, stability, completeness, and reproducibility. A DOI, repository accession, webpage, preprint, supplement, author communication, or local copy provides different kinds of evidence.

## Decision
Aletheia SHALL record external evidence using a trust model based on source class and verification, not prestige alone.

For each external object, record where possible: canonical identifier, source class, retrieval time, local identity/hash when copied, publication/repository version, peer-review status where relevant, whether the source was directly inspected, whether a claim is primary evidence/secondary interpretation/metadata, and unresolved provenance conflicts.

Author correspondence may resolve documentary questions but does not by itself substitute for experimental validation.

## Consequences
The platform can reason about evidence quality without flattening all citations into equivalent authority.
