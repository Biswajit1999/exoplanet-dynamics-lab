# Validation

The test suite covers Kepler's third law, Earth period/semimajor axis regression, mutual Hill spacing, controlled 3:2 and non-commensurate cases, AMD, Earth RV semi-amplitude, flux normalisation, transit probability, O−C timing, multi-planet RV construction, instrument offsets, exact host grouping, uncertainty bounds and a five-year REBOUND two-body conservation test.

The selected K2-138 WHFast run spans 10 years with timestep `P_min/100`. Its release metrics are generated in `results/simulation_summary.json`; passing means `|ΔE/E| < 10⁻⁷` and `|ΔL/L| < 10⁻⁷`.

