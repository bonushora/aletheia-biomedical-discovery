# ADR-0003 — Human Scientific Authority Boundary

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Scientific governance

## Context
Automated pipelines can calculate metrics, simulate thresholds, rank hypotheses, and summarize literature, but these operations can be mistaken for scientific approval if authority is not explicit.

## Decision
Aletheia establishes a hard boundary between automated recommendation and human scientific authority.

Only an authorized human reviewer may approve or reject decisions that materially change scientific interpretation or promote a result across a validation boundary, including adoption of a scientific QC policy, exclusion of real biological observations based on a scientific criterion, promotion of a cell annotation, promotion of a mechanistic or regenerative candidate, assertion of experimental validation, and assertion of clinical validity or therapeutic efficacy.

Automation may produce evidence, simulations, candidate rules, uncertainty estimates, and proposed decisions, but must label them as pending human review.

## Invariants
- Absence of human approval cannot be interpreted as approval.
- A model cannot approve its own scientific output.
- Human approval does not erase uncertainty or provenance.
