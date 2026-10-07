# Scientific state model — draft derived view

This is a convenience view derived from proposed ADRs and is non-normative until those ADRs are accepted.

```text
SOURCE DISCOVERED
      |
      v
DATASET QUALIFICATION -----> BLOCKED / INSUFFICIENT_EVIDENCE
      |
      v
QUALIFIED_COMPUTATIONALLY
      |
      v
OBSERVATION
      |
      v
INTERPRETATION / HYPOTHESIS -----> CONTRADICTED / SUPERSEDED
      |
      v
PENDING_HUMAN_REVIEW
      |
      v
SUPPORTED / POLICY-APPROVED
      |
      v
DERIVED ANALYSIS OR EXPERIMENTAL HANDOFF
      |
      +----> VALIDATED_EXPERIMENTALLY
                     |
                     +----> VALIDATED_CLINICALLY
```

A `GREEN_*` mission state is contract-scoped and never automatically promotes an item in this scientific state model.
