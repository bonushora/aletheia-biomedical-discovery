# ADR-KR-0008 — Experimental Hypothesis Handoff Boundary

- **Status:** Proposed
- **Date:** 2026-10-06
- **Parents:** ADR-0003, ADR-0009, ADR-KR-0007

## Decision
When KRRCP produces a hypothesis suitable for wet-lab investigation, the handoff package must state the hypothesis and falsifiable prediction, evidence and counterevidence, candidate mechanism, proposed experimental observations without claiming successful execution, known confounders and limitations, source datasets and analysis provenance, current evidence-ladder level, and human reviewer decision.

The computational platform cannot record `EXPERIMENTALLY_VALIDATED` until external experimental evidence is ingested and reviewed.
