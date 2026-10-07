# ADR-0015 — AI Model and Agent Non-Authority with Reproducible Inference

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** AI-assisted research

## Context
Aletheia may use language models, agents, embedding models, classifiers, or other learned systems. Their outputs may vary across model versions, prompts, providers, stochastic settings, and tool contexts.

## Decision
AI components are non-authoritative analytical instruments.

A governed AI-assisted result SHOULD record, where technically available and relevant: model/provider identity and version, prompt/instruction identity or hash, tool/data context, generation parameters, structured output/schema validation, citations/evidence used, deterministic post-processing and checks, and human review state.

No AI component may promote its own output across a human scientific authority boundary. Non-reproducible generative output must be treated as a proposal, not a stable scientific fact.

## Consequences
Models can be swapped or improved without transferring scientific authority to the model layer.
