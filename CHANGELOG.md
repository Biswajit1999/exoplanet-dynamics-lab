# Changelog

## [0.2.0] - 2026-10-04

### Scientific validation

- Conservation criteria now use the maximum sampled drift across a trajectory,
  while retaining final drift as a separate diagnostic.
- Actual WHFast step times are stored beside requested output times; the maximum
  mismatch is reported and tested to remain within one timestep.
- Added 50/100/200-step convergence experiments and 32 deterministic unknown-
  mean-anomaly sensitivity trials, with every draw and metric published as CSV.
- Added fail-closed physical input and integration-control validation.
- Made system ordering deterministic and documented its multiplicity and
  hostname tie-breakers as reconstruction-practicality choices, not scientific value.

### Communication and infrastructure

- Added a generated three-panel numerical-validation figure and a dedicated
  website section with machine-readable downloads and adjacent claim boundaries.
- Renamed the public table display to “parameter coverage index” and labels it
  as a heuristic rather than probability or physical confidence.
- Pinned all CI and Pages actions to immutable commit SHAs.

## [0.1.0] - 2026-08-24

- Initial provenance-first population survey, catalogue evidence tiers,
  K2-138 nominal model, forward-observable helpers, tests and web laboratory.
