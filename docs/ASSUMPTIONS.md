# Assumptions

- NASA `default_flag = 1` rows represent the archive's preferred published solution at synchronization time.
- Exact archive `hostname` is the canonical grouping key; no fuzzy entity merging is performed.
- Missing longitude of ascending node and nominal mean anomaly are project priors of zero in the displayed simulation. A separate 32-trial experiment draws independent uniform mean anomalies with a fixed seed; it is not a posterior.
- Missing eccentricity becomes a project prior of zero only in the displayed trajectory and remains disclosed.
- Planet radii are exaggerated visually; orbital coordinates share one linear scale.
- Near period ratio means proximity only, not confirmed resonance.

