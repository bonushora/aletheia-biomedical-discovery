# ADR-KR-0002 — Qualified Kidney Dataset Intake

- **Status:** Proposed
- **Date:** 2026-10-06
- **Parents:** ADR-0004, ADR-0005, ADR-0008

## Decision
Kidney datasets enter downstream analysis only through a qualification record that separates byte/data integrity, provenance, metadata completeness, and scientific suitability.

Computational qualification MUST NOT be reported as scientific validation. Unresolved provenance may be preserved explicitly when it does not invalidate the permitted computation; otherwise intake is `BLOCKED`.
