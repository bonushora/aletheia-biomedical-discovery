# ADR-KR-0007 — Regenerative Candidate Evidence Ladder

- **Status:** Proposed
- **Date:** 2026-10-06
- **Parents:** ADR-0004, ADR-0006, ADR-0009

## Decision
KRRCP will use an explicit evidence ladder for regenerative candidates. Indicative levels are:

1. `OBSERVED_SIGNAL`
2. `ASSOCIATION_SUPPORTED`
3. `MECHANISTIC_HYPOTHESIS`
4. `CROSS_DATASET_SUPPORTED`
5. `ORTHOGONAL_PRECLINICAL_SUPPORT`
6. `EXPERIMENTALLY_VALIDATED`
7. `CLINICALLY_VALIDATED`

Transitions require evidence appropriate to the target level and human review where mandated by the platform. Higher ranking within a level does not equal promotion to the next level.
