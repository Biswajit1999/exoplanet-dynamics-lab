# Validation

The test suite covers Kepler's third law, Earth period/semimajor axis regression, mutual Hill spacing, controlled 3:2 and non-commensurate cases, AMD, Earth RV semi-amplitude, flux normalisation, transit probability, O−C timing, multi-planet RV construction, instrument offsets, exact host grouping, uncertainty bounds and a five-year REBOUND two-body conservation test.

The selected K2-138 WHFast run spans 10 years with timestep `P_min/100`. Its release metrics are generated in `results/simulation_summary.json`; passing means the maximum sampled `|ΔE/E₀| < 10⁻⁷` and `|ΔL/L₀| < 10⁻⁷`. The nominal maxima are `2.49×10⁻⁸` and `1.33×10⁻¹⁴` respectively. Actual symplectic step times are stored, and their maximum offset from requested output times is bounded by one timestep.

`results/timestep_convergence.csv` independently repeats the 10-year run at 50, 100 and 200 steps per shortest orbit; maximum energy drift falls from `9.98×10⁻⁸` to `2.49×10⁻⁸` to `6.23×10⁻⁹`, consistent with second-order timestep convergence. `results/phase_prior_sensitivity.csv` contains all 32 deterministic unknown-phase trials. All pass the numerical tolerance; the largest eccentricity excursion is 0.0133. These are numerical and prior-sensitivity checks, not evidence of gigayear physical stability.

