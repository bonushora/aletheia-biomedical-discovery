# ADR-0002 — Platform Core and Disease-Specific Research Control Planes

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Platform topology

## Context
Evidence, provenance, reproducibility, state transitions, review gates, and packaging are reusable across disease areas. Cell ontologies, biological references, QC policies, and experimental interpretations are domain-specific.

## Decision
Aletheia is split into:
1. **Core Biomedical Discovery Engine** — shared evidence, provenance, state, packaging, policy execution, and review infrastructure.
2. **Research Control Planes** — disease/organ-specific modules that define domain evidence requirements and scientific policies.

The **Kidney Regeneration Research Control Plane (KRRCP)** is the first specialized module.

Control planes may specialize platform contracts but may not weaken core invariants such as provenance, explicit uncertainty, human authority, or no-silent-mutation.

## Consequences
Kidney work can evolve rapidly without hard-coding kidney-specific assumptions into the platform core. Future modules for diabetes, neurodegeneration, cancer, or other domains can reuse the same governance substrate.
