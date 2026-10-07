# ADR-0006 — Scientific State Machine

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** State semantics

## Context
Binary “pass/fail” labels are too coarse for biomedical workflows. Computational qualification, scientific review, experimental validation, and clinical validation are distinct.

## Decision
Aletheia will use explicit orthogonal state dimensions rather than a single universal green flag. Common states include `NOT_EXECUTED`, `PENDING_HUMAN_REVIEW`, `IN_PROGRESS`, `QUALIFIED_COMPUTATIONALLY`, `SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE`, `BLOCKED`, `VALIDATED_EXPERIMENTALLY`, `VALIDATED_CLINICALLY`, and `SUPERSEDED`.

A workflow-level `GREEN_*` state means only that the contract named by the suffix was satisfied. It MUST NOT be generalized to scientific or clinical validation unless that is explicitly the contract.

## Consequences
Status reporting becomes more precise and prevents “green” infrastructure from being mistaken for biological validation.
