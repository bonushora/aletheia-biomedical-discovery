# ADR-0004 — Evidence Before Scientific Claim

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Claims and evidence

## Context
Biomedical statements differ in strength: raw observations, associations, mechanistic interpretations, replicated findings, and clinical claims are not equivalent.

## Decision
Every promotable scientific claim MUST carry an evidence record containing, at minimum: claim identifier and version; claim class; source datasets and immutable identities where available; analytical procedure and software/environment identity; supporting evidence; contradictory or limiting evidence; uncertainty and unresolved assumptions; replication state; human review state; and links to external literature used in the rationale.

Claims without sufficient evidence remain explicitly provisional or blocked. The system must support `INSUFFICIENT_EVIDENCE` as a valid outcome.

## Consequences
Aletheia optimizes for auditable claims rather than persuasive prose. Evidence can be strengthened, challenged, or superseded without losing the historical chain.
