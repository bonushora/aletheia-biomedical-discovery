# Compatibility model

No executable contract, schema, or compatibility range is established by this documentation-only foundation.

```yaml
contract_version: NOT_ESTABLISHED
schema_version: NOT_ESTABLISHED
contract_versioning: semver
control_plane_dependency:
  explicit: true
  mutable_main_dependency: forbidden
breaking_change:
  requires_major_version: true
  requires_migration_mission: true
compatibility_matrix:
  required: true
  current: NOT_ESTABLISHED
```

A compatibility matrix must bind a Control Plane revision to an explicit contract and schema range. A breaking Core change cannot silently migrate or mutate a federated Control Plane; migration requires its own authorized mission and validation to GREEN.
