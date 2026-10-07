# ADR-0013 — Research-Only Boundary and Clinical Non-Authority

- **Status:** Proposed
- **Date:** 2026-10-06
- **Scope:** Safety and intended use

## Context
Biomedical discovery outputs can resemble clinical recommendations even when they have not undergone clinical validation, regulatory review, or patient-specific assessment.

## Decision
Aletheia is a research platform unless and until a separately governed clinical product is created and validated.

The research platform MUST NOT diagnose or treat a patient, provide patient-specific clinical recommendations as authoritative outputs, present computational or experimental candidates as established therapies, or infer clinical validation from scientific plausibility or preclinical evidence.

Clinical claims require an explicitly separate validation and governance path.

## Consequences
The research system can remain ambitious without silently crossing into clinical decision support.
