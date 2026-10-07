# Architecture

```text
Aletheia Biomedical Discovery
        |
        +-- Core
        +-- Contracts
        +-- Schemas
        +-- Evidence Package Specification
        +-- Research Control Plane Interface
                    |
        +-----------+--------------------+
        |                                |
        v                                v
Kidney Regeneration                Future Control Planes
Research Control Plane
(external repository)
```

The Aletheia repository owns platform governance and integration boundaries. It does not embed or mutate the Kidney implementation. Federation occurs only through explicit, versioned contracts, schemas, and evidence packages. Current executable versions are `NOT_ESTABLISHED`.

See [ADR-0016](docs/adr/0016-repository-topology-and-module-integration-model.md), the [federation model](docs/architecture/FEDERATION-MODEL.md), and the [compatibility model](docs/architecture/COMPATIBILITY-MODEL.md).
