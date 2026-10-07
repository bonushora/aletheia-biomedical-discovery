# ADR-0007 — Separation of Observation, Interpretation, and Intervention

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Analytical semantics

## Context
A metric such as mitochondrial fraction is an observation. Calling a cell damaged is an interpretation. Filtering that cell is an intervention. Combining these steps obscures assumptions and makes review difficult.

## Decision
Aletheia SHALL model three separate layers:
1. **Observation** — computed or directly measured facts.
2. **Interpretation** — scientific meaning proposed for observations.
3. **Intervention** — mutation, exclusion, promotion, or experimental action based on an interpretation.

Each layer must be independently traceable. An intervention must reference the approved policy or decision that authorized it.

## Consequences
Pipelines become more verbose but scientifically reviewable. Alternative interpretations can coexist without rewriting source observations.
