# Research Control Plane Descriptor Contract v0.1.0

## Identity

- Contract: `aletheia.research-control-plane-descriptor`
- Contract version: `0.1.0`
- Schema version: `0.1.0`
- Schema ID: `urn:aletheia:schema:research-control-plane-descriptor:0.1.0`
- Registry status: `EXPERIMENTAL`

## Purpose

This contract describes the identity, immutable source revision, authority boundary, and exact contract dependencies of a federated Research Control Plane. It is the first executable Aletheia federation contract and implements no scientific workflow, dataset schema, evidence-package schema, provenance schema, or human-decision schema.

## Normative shape

The root contains exactly `descriptor_contract`, `control_plane`, `repository`, `authority`, and `consumes`. Every object is closed to unknown fields.

`repository.branch` is observational metadata and may be `main`; the immutable qualification identity is `repository.commit_sha`. In contrast, every value in `consumes[].compatible_versions` is an exact SemVer and may not be a mutable label such as `main`, `latest`, or `*`.

The authority constants are mandatory:

- `research_only` is `true`;
- `clinical_authority` is `false`;
- `human_scientific_authority_required` is `true`.

The JSON Schema is the normative structural representation. The standard-library validator additionally rejects duplicate JSON keys, duplicate dependency names, unsafe repository URL forms, and duplicate compatible versions. A validator PASS establishes conformance to this contract only; it does not qualify a consumer or establish scientific or clinical validity.

## Compatibility

Version 0.1.0 has zero qualified consumers. Compatibility must be established by a separate cross-repository qualification mission bound to exact repository and contract identities.
