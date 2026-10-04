# Reproducibility

Use Python 3.12+ and Node 22.12+. Then run `make setup`, `make data`, `make survey`, `make simulate`, `make figures`, `make web`, and `make test`.

Each acquisition manifest stores the ADQL, UTC timestamp, row count, URL, NASA dataset DOI, processing version and SHA-256. Raw CSV responses are ignored by Git; copy them to release assets for immutable releases. Derived Parquet, JSON, CSV, figures, simulations and manifests are kept in the repository.

`make simulate` regenerates the nominal trajectory, maximum-sampled conservation metrics, three-level timestep convergence, and 32-trial phase-prior ensemble. The phase seed (`20261004`), every draw, actual integrator times, and requested output times are preserved in machine-readable results.
