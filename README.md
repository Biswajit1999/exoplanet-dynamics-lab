# EXODYNAMICS — Multi-Planet Systems in Motion

**Reconstructing, simulating, and observing real exoplanetary systems from public astronomical data.**

EXODYNAMICS is an open computational astrophysics platform that begins with a population survey, identifies genuine multi-planet systems, ranks their reconstruction evidence, and evolves archive-selected architectures with REBOUND. Observed, processed, simulated and model-predicted quantities are never conflated.

## Archive snapshot

<!-- BEGIN GENERATED STATS -->
| Quantity | Generated value |
|---|---:|
| Genuine source rows surveyed | **98,192** |
| Confirmed planets | **6,354** |
| Host systems | **4,764** |
| Multi-planet systems | **1,058** |
| High-multiplicity systems (≥6) | **14** |
| Tier A systems | **271** |
| Tier B systems | **760** |
| Near-commensurate adjacent pairs | **261** |
<!-- END GENERATED STATS -->

These values were generated from the timestamped response in [`results/archive_summary.json`](results/archive_summary.json), not typed from memory. The `ps` contribution includes multiple literature solutions; confirmed-planet counts use only `default_flag = 1`.

## Scientific flow

```text
NASA TAP snapshots → schema validation → exact host identity → evidence tiers
                   → uncertainty-aware parameters → REBOUND trajectory
                   → transit / TTV / RV forward models → observation residuals
```

The current release completes the live population foundation and a validated nominal K2-138 reconstruction. K2-138 emerged as the highest-ranked system under the transparent selection score; it was not preselected. The WHFast integration spans 10 years, uses `P_min/100`, and passes release tolerances with `ΔE/E = 2.28×10⁻⁸` and `ΔL/L = 1.17×10⁻¹⁴`. It does **not** establish long-term stability.

## Repository map

- `src/exodynamics/`: archive client, population catalogue, dynamics, uncertainty and observation models
- `data/manifests/`: timestamped ADQL acquisition provenance and checksums
- `results/`: derived Parquet/CSV/JSON data, figures and simulation metrics
- `web/`: React/Three.js archive atlas and orbital laboratory
- `docs/`: research provenance, methods, assumptions, limitations and validation
- `paper/`: research manuscript source
- `notebooks/`: thin workflows backed by package functions
- `tests/`: numerical and data-model regressions

## Reproduce

```bash
make setup
make data
make survey
make simulate
make figures
make web
make test
```

Equivalent commands are available through `exodynamics data|survey|analyse`. Python 3.12+ and Node 22.12+ are required. The exact acquisition query, row count, timestamp, DOI and checksum are stored in every manifest.

## Scientific boundaries

- A near period ratio is not called a confirmed resonance without libration evidence.
- Missing nodes and orbital phases in the first trajectory use disclosed zero-valued project priors.
- Planet sizes are visually exaggerated; orbital coordinates use one linear distance scale.
- No MAST light curve, DACE RV series, or new Gaia match is claimed in v0.1.
- Transit/TTV/RV modules are presently validated on controlled inputs, not presented as telescope analyses.
- Tier scores measure evidence coverage, not the probability that a model is correct.

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) for the complete boundary and [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for snapshot policy.

## Citation and licence

Please cite using [`CITATION.cff`](CITATION.cff). Code is released under the MIT License. Archive data retain their source terms and should cite the NASA Exoplanet Archive dataset DOI `10.26133/NEA12`.
