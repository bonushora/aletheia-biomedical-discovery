# Contract versioning

- Published contracts use Semantic Versioning.
- A breaking change requires a major version.
- Every Control Plane records explicit compatible versions; v0.1.0 uses a non-empty unique set of exact Semantic Versions.
- A Control Plane must never consume mutable `main` implicitly.
- Migration is an explicit, separately authorized operation with its own validation.
- Compatibility is recorded in a required matrix and backed by evidence.

The RCP Descriptor contract is established at `0.1.0` with schema `0.1.0`. Consumer compatibility remains `NOT_ESTABLISHED` until a separate exact-revision qualification.
