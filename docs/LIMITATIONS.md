# Limitations

Version 0.1 is a substantial, verified foundation rather than completion of every research programme in the master brief.

- One live archive is surveyed. MAST light-curve files, DACE RVs and new Gaia DR3 queries were not retrieved.
- The archive survey covers 98,192 source rows at the recorded timestamp; `ps` includes multiple literature solutions and is not a unique-planet count.
- The web laboratory contains one deterministically selected 10-year nominal reconstruction plus 32 mean-anomaly prior draws. This tests numerical and phase-prior sensitivity only; it does not demonstrate gigayear stability or sample the observational posterior.
- Parameter correlations and published posterior chains are not yet ingested; the uncertainty module supports split-normal draws.
- Resonance output is proximity-only. Libration, resonant chains and secular frequency analysis are not reported.
- MEGNO is implemented but not run population-wide.
- Transit and RV helpers are validated on controlled inputs, not real observations in this release.
- DACE may require access arrangements; no unavailable measurement is fabricated.
- Deployment, GitHub push and release creation depend on repository authentication and were not assumed.

