# Schemas

This directory reserves explicitly versioned schemas for:

- evidence packages;
- provenance;
- scientific state;
- dataset identity;
- human decision records;
- Research Control Plane descriptors.

Only the Research Control Plane descriptor schema is established, at [`0.1.0`](research-control-plane-descriptor/0.1.0/schema.json). Evidence-package, provenance, scientific-state, dataset-identity, and human-decision schemas remain `NOT_ESTABLISHED`.

The descriptor schema is a normative structural representation. Its standard-library validator enforces additional duplicate-key, dependency-identity, and repository-URL semantics without claiming generic JSON Schema-engine equivalence.
