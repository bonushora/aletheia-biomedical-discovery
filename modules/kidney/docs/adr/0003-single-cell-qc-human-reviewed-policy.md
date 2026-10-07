# ADR-KR-0003 — Single-Cell QC as a Human-Reviewed Scientific Policy

- **Status:** Proposed
- **Date:** 2026-10-06
- **Parents:** ADR-0003, ADR-0007, ADR-0008

## Context
QC metrics are observations; thresholds and exclusion semantics are scientific policies that depend on tissue, protocol, dataset, and research question.

## Decision
KRRCP will compute and qualify descriptive single-cell QC separately from the policy that acts on it.

- No universal mitochondrial, gene-count, or UMI threshold is hard-coded as scientific truth.
- Threshold proposals must cite dataset-specific and/or appropriate kidney/organoid evidence.
- Simulation may flag hypothetical impacts without removing cells.
- A human scientific decision is required before a QC policy becomes executable.
- Applying an approved policy creates a derived dataset and does not mutate the qualified source.

Current org4 work is treated as evidence for this architecture, not as automatic acceptance of any threshold.
