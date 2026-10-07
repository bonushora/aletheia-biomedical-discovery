# Foundation Hardening Model

## Scope

Foundation hardening uses synthetic, local fixtures to challenge architecture-document integrity, repository path portability, accepted-decision continuity, manifest freshness, federation boundaries, and ZIP container safety.

The model distinguishes five concerns:

1. **DETECTION** identifies a declared invalid state and reports the offending path or invariant.
2. **PREVENTION** refuses to treat an unsafe ZIP or repository state as acceptable.
3. **QUALIFICATION** executes the bounded, versioned attack corpus and compares observed results with declared expectations.
4. **SCIENTIFIC_VALIDATION** assesses scientific methods and evidence; it is not performed here.
5. **CLINICAL_VALIDATION** assesses clinical claims and authority; it is not performed here.

## Oracle boundary

The canonical scripts in the real Aletheia repository are the oracles. Each attack fixture is a fresh copy without Git metadata. A copied validator is data under test and is never trusted as the executable oracle. Explicit fixture roots are physically resolved before inspection.

## Meaning of GREEN

`GREEN_ALETHEIA_FOUNDATION_HARDENING_V01` means only that the declared foundation attack corpus produced every expected outcome and that nominal structural checks remained green at the qualified commit.

It does not claim scientific validation, clinical validation, therapeutic efficacy, universal security, or protection against unknown attacks.

## Boundaries

- No real biomedical or patient data is used.
- A structurally safe ZIP is not necessarily meaningful scientific evidence.
- ADR-0016 remains governed by its prior human acceptance and byte continuity.
- ADR-0017 remains Proposed unless separately decided by a human maintainer.
- No executable contracts or schemas are created by this hardening model.
