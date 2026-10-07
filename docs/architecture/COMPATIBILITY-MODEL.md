# Compatibility model

The first executable federation boundary is the experimental RCP Descriptor contract and schema v0.1.0. No consumer compatibility is established.

```yaml
contract: aletheia.research-control-plane-descriptor
contract_version: 0.1.0
schema_version: 0.1.0
contract_versioning: semver
control_plane_dependency:
  explicit: true
  mutable_main_dependency: forbidden
breaking_change:
  requires_major_version: true
  requires_migration_mission: true
compatibility_matrix:
  required: true
  qualified_consumers: 0
  consumer_compatibility: NOT_ESTABLISHED
```

A compatibility matrix must bind a Control Plane revision to exact contract and schema identities. A breaking Core change cannot silently migrate or mutate a federated Control Plane; migration requires its own authorized mission and validation to GREEN.
