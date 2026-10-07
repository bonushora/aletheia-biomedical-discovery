# ADR-0017 — Adversarial Hardening and Qualification Model

- **Status:** Accepted
- **Date:** 2026-10-07
- **Decision date:** 2026-10-07
- **Authority:** Explicit human approval
- **Scope:** Foundation integrity and qualification boundaries

## Context

The documentation-first foundation already validates its ADR inventory, governance status, federation safeguards, links, hashes, and manifest. A nominal validation result alone does not show how those controls behave when repository paths, governance metadata, package members, or validation fixtures are intentionally malformed.

## Decision

Propose a bounded adversarial qualification model with independent fixtures and canonical validation oracles. The model distinguishes:

- detection of an invalid state;
- prevention of unsafe extraction or acceptance;
- qualification against a declared attack corpus;
- scientific validation, which is outside this foundation hardening;
- clinical validation, which is outside this foundation hardening.

The canonical foundation validator may inspect an explicitly selected physical root, but an attacker-controlled fixture must not replace the canonical validator executable. Accepted ADR continuity is checked against an explicit Git base revision. Evidence ZIP verification establishes container safety only and does not establish scientific meaning.

Cross-platform repository qualification covers case-fold collisions, Windows-reserved components, trailing-dot or trailing-space ambiguity, unexpected symbolic links, and local Markdown links that are absolute or escape the repository. Clear raw biomedical payload extensions remain outside this repository.

`GREEN_ALETHEIA_FOUNDATION_HARDENING_V01` means only that the declared foundation attack corpus and nominal structural gates passed. It is not a claim of therapeutic efficacy, scientific validation, clinical validation, universal security, or protection from unknown attacks.

## Consequences

- ADR-0016 remains the only Accepted ADR and is protected by a history-aware continuity check.
- This ADR remains Proposed until a separate explicit human decision.
- The hardening controls remain standard-library validation and test tooling.
- No executable platform contract, schema, scientific workflow, or clinical workflow is introduced.
- Future attack-corpus changes require review of both expected outcomes and the canonical oracle.

## Alternatives considered

### Treat nominal validation as sufficient

Rejected because it does not exercise bypasses or cross-platform path ambiguity.

### Copy validators into each fixture and execute the copy

Rejected because the fixture could replace the oracle it is meant to test.

### Accept this ADR as part of automated integration

Rejected because acceptance is a separate human architectural decision.
