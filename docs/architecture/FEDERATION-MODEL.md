# Federation model

- Aletheia Core does not depend on the Kidney implementation.
- Kidney consumes only published or otherwise explicitly qualified Aletheia contracts; the current contract version is `NOT_ESTABLISHED`.
- Each repository has its own URL, branch, commit SHA, CI, and release lifecycle.
- Cross-repository mutation is prohibited without an explicit mission authorizing it.
- Every integration evidence package records the exact contract and schema versions consumed.
- Mutable `main` is not an integration version or dependency target.
- Git submodules are not the primary integration mechanism.

Kidney is the first federated Research Control Plane. Its source repository remains external to this repository.
