# Foundation Hardening Attack Matrix

The canonical case definitions and machine-readable outcomes are maintained by the independent harness and its JSON evidence.

| IDs | Boundary | Expected control |
|---|---|---|
| H01 | Nominal fixture | Validator passes |
| H02–H06 | ADR status, accepted history, and register hashes | Invalid governance is rejected |
| H07 | Manifest freshness | Drift is rejected |
| H08–H10 | Symlinks and local Markdown paths | Unsafe paths are rejected |
| H11–H12 | Raw payload and federated module boundary | Payload is rejected |
| H13–H14 | Text integrity | Conflict residue and invalid UTF-8 are rejected |
| H15 | Accepted federation safeguards | Safeguard removal is rejected |
| H16–H18 | Cross-platform filesystem semantics | Ambiguous paths are rejected |
| H19–H23 | Malicious ZIP structures | Unsafe containers are rejected |
| H24 | Safe ZIP control | Container-safety verifier passes with limited claim |
| H25 | Fixture oracle substitution | Canonical oracle still rejects the independent defect |
| H26 | ADR identity uniqueness | Duplicate identity is rejected |

All payloads are synthetic. Expected rejection is a test result, not scientific or clinical validation.
