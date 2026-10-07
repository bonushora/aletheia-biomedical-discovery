# ADR-0000 — ADR Governance and Lifecycle

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Aletheia Biomedical Discovery

## Context
A biomedical discovery platform can accumulate architectural and scientific-policy choices that later become difficult to distinguish. The project needs a durable process for recording architecture without turning transient scientific judgments into immutable software doctrine.

## Decision
1. Architectural decisions are recorded as ADRs.
2. Every ADR has an explicit lifecycle state: `Proposed`, `Accepted`, `Superseded`, `Deprecated`, or `Rejected`.
3. Only a human maintainer may move an ADR from `Proposed` to `Accepted` or `Rejected`.
4. Scientific thresholds, cell-level decisions, candidate rankings, and disease-specific operating rules belong in versioned scientific policies or decision records unless the architectural issue is who may decide and how evidence is governed.
5. Accepted ADRs are never silently rewritten. Material changes require a superseding ADR or an explicit amendment with rationale and history.
6. ADR identifiers are stable and never reused.

## Invariants
- Architecture cannot impersonate scientific approval.
- Historical decisions remain auditable.
- Supersession is explicit.
- Machine-generated ADR text remains `Proposed` until human acceptance.

## Consequences
The project gains a durable architectural record while preserving scientific flexibility. Review overhead increases slightly, but ambiguity over what is architectural versus scientific is reduced.
