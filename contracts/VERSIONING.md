# Contract versioning

- Published contracts use Semantic Versioning.
- A breaking change requires a major version.
- Every Control Plane records an explicit compatible version or range.
- A Control Plane must never consume mutable `main` implicitly.
- Migration is an explicit, separately authorized operation with its own validation.
- Compatibility is recorded in a required matrix and backed by evidence.

No contract version or compatibility range is established in this foundation; both remain `NOT_ESTABLISHED`.
