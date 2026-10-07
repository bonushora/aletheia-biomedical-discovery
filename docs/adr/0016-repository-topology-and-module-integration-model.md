# ADR-0016 — Repository Topology and Module Integration Model

- **Status:** Accepted
- **Date:** 2026-10-06
- **Decision date:** 2026-10-07
- **Authority:** Explicit human approval of the federated recommendation and safeguards
- **Scope:** Source and module topology

## Context
The Kidney Regeneration Research work already exists as an independent research codebase. Converting it implicitly into the platform root would mix a mature vertical with a new platform architecture and could force risky history, path, CI, and release changes.

## Decision
The accepted topology is **federated repositories**:

- `aletheia-biomedical-discovery` is the platform/core repository;
- `kidney-regeneration-research` remains an independently versioned research repository and first KRRCP implementation;
- integration occurs through versioned contracts, evidence packages, schemas, and adapters rather than by moving historical kidney artifacts into the platform repository;
- future Control Planes remain independently governed repositories and must satisfy explicitly versioned Core contracts.

The following safeguards are mandatory:

1. `aletheia-biomedical-discovery` has its own repository.
2. Research Control Planes remain in independent repositories.
3. Integration uses explicitly versioned contracts.
4. Integration uses explicitly versioned schemas.
5. Evidence packages are versioned and identify the consumed contract version.
6. No Control Plane may depend implicitly on mutable `main` state.
7. Core changes may not mutate a federated repository automatically.
8. A compatibility matrix is required for qualified integrations.
9. Incompatible migration requires an explicit migration mission and independent validation to GREEN.
10. Git submodules are not the primary integration mechanism.

No existing repository is to be repurposed or migrated solely by inference.

## Alternatives considered

### Convert the kidney repository into the Aletheia monorepo
Rejected as the default because it unnecessarily couples historical kidney research, platform governance, and future disease modules.

### Copy kidney history into a new monorepo
Rejected as the default because duplicated history and provenance complicate auditability.

## Consequences
Repository integration of the ADR foundation occurs in the dedicated Aletheia platform repository. Each repository retains its own URL, branch, commit identity, CI, and release lifecycle. Contract and schema versions are `NOT_ESTABLISHED` in this foundation mission.
