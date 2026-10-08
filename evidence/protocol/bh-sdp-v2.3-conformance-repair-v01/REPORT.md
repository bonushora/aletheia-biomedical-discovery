# BH-SDP v2.3 exact conformance repair report

This repair corrects serialization and schema conformance only for every tracked Aletheia snapshot claiming `BH-SDP v2.3`. It does not fabricate, upgrade, or reinterpret any prior technical GREEN result.

The exact top-level and nested key sets, enum spellings, UTF-8 parsing, duplicate-key rejection, scalar types, arrays, nonnegative counters, and recursive claim discovery are now enforced by a standard-library validator and 31 unit tests. Scientific and clinical validation were not executed.

No contract, schema, registry, or compatibility-matrix semantics changed. ADR-0016 and ADR-0017 remain byte-identical. No Kidney file, worktree, scientific state, or biomedical datum was changed.

Fields absent from older snapshots were reconstructed only from existing mission evidence with conservative semantics. `contagem_de_gates` equals the number of named entries in each snapshot's `componentes_validados`; this is the deterministic gate-group counting rule for the repair. A `tentativas_equivalentes` value of `0` means “no equivalent retry count was historically recorded”, not proof that no retries occurred.

The three historical qualified commits remain `c08d5740149ea00f9e8f0915ef4aacc74c95ce97`, `01b275e5cc8d96f1c03540b24b581a2ae820f264`, and `1383df3c5cf738a2ef4da1c650ef14a2f788b0c9`. The exact repair commit is recorded externally after the single local commit because a commit cannot contain its own identity.
