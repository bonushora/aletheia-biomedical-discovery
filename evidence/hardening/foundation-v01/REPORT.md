# Foundation Hardening v01 Report

The bounded adversarial campaign covers 26 synthetic cases. The initial pass found one verifier defect: a safe ZIP member with permission bits but no explicit Unix type bits was rejected. The verifier now inspects the file-type mask separately. Evidence materialization then exposed a false positive in which H13 delimiters preserved in JSON were treated as a live Markdown conflict; that rule is now scoped to governed Markdown. Targeted controls and the complete corpus subsequently passed.

ADR-0016 remains Accepted and byte-identical to baseline. ADR-0017 is integrated only as Proposed. No executable contract or schema was introduced. Scientific and clinical validation were not executed.

The protected kidney repository retained its preexisting working-tree modification and was not written by this mission. Remote creation, push, tag, release, publication, and dependency installation were not performed.

The exact local commit and external package identities are recorded in the external post-condition created after commit.
