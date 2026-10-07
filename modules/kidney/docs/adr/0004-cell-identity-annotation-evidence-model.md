# ADR-KR-0004 — Cell Identity and Annotation Evidence Model

- **Status:** Proposed
- **Date:** 2026-10-06
- **Parents:** ADR-0004, ADR-0009, ADR-0010

## Decision
Cell annotations are evidence-bearing claims. Candidate annotations SHOULD record marker evidence, reference mapping evidence, conflicting markers, ontology identifiers where appropriate, method/version, confidence semantics, and human review state.

Automated labels remain candidate annotations until the configured promotion gate is satisfied. Ambiguous, transitional, or off-target states may remain unresolved rather than being forced into a known label.
