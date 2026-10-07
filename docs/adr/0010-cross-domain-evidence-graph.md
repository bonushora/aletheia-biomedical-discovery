# ADR-0010 — Cross-Domain Evidence Graph

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Knowledge representation

## Context
Potential discoveries may connect genes, cell states, pathways, phenotypes, organ systems, disease mechanisms, interventions, and publications across modules.

## Decision
Aletheia will maintain a versioned evidence graph whose edges represent typed, provenance-bearing assertions rather than unqualified associations.

The graph must distinguish at least observation, derived association, literature assertion, mechanistic hypothesis, replication, contradiction, intervention candidate, and validation event.

Graph edges must retain origin and evidence strength. Cross-domain edges do not inherit validation merely because one endpoint is validated in another context.

## Consequences
The graph can reveal cross-disease hypotheses while reducing the risk of context transfer being treated as proof.
