# ADR-0009 — Hypothesis Generation Is Not Validation

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Discovery semantics

## Context
Models can synthesize literature and multi-omics signals into compelling hypotheses. Plausibility is not experimental evidence.

## Decision
All machine- or software-generated hypotheses begin in a non-validated state and must carry origin and generation method, evidence used, counterevidence/known caveats, falsifiable prediction where possible, proposed validation path, confidence or ranking semantics if used, and an explicit statement that ranking is not validation.

Promotion to experimentally validated status requires independent evidence produced by an authorized experimental process and human review.

## Consequences
Aletheia can generate ambitious hypotheses without conflating creativity with proof.
