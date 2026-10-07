# ADR-KR-0006 — Cross-Dataset Replication Before Candidate Promotion

- **Status:** Proposed
- **Date:** 2026-10-06
- **Parents:** ADR-0004, ADR-0009

## Decision
A regenerative candidate derived from one kidney dataset cannot be promoted as a robust cross-context candidate solely on that dataset.

Promotion SHOULD require replication across an appropriate independent dataset, orthogonal evidence, or a documented reason why replication is not yet possible. Failure to replicate is recorded as evidence, not hidden.
