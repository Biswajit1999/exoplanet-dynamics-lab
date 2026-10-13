# Independent dynamical and radial-velocity diagnostics

These functions extend the existing exodynamics numerical and observational modules without changing archive-derived classifications. They are screening tools, not detections or dynamical stability proofs.

## First-order commensurability and superperiod

For an inner and outer orbital period near the first-order `j:(j-1)` commensurability, define `Delta = ((j-1)/j)*(P_outer/P_inner)-1` and the beat superperiod `P_sup = 1/|j/P_outer-(j-1)/P_inner|`. An exactly commensurate pair has infinite beat period in this approximation. Small `|Delta|` **does not demonstrate resonant-angle libration**, and the beat period does not predict a TTV amplitude without additional parameters.

## Independent-prior Hill-spacing sensitivity

For two planets, compute Keplerian semimajor axes from sampled positive masses and periods and mutual Hill spacing `Delta_H = (a_outer-a_inner)/(((a_inner+a_outer)/2)*((m_inner+m_outer)/(3*M_star))^(1/3))`. Independent lognormal input priors are moment-matched to supplied means and standard deviations; draws where the periods reverse order are discarded and counted. Report 5th/50th/95th percentiles and the fraction above `2*sqrt(3)`. The threshold is an approximate *sufficient* analytic criterion only for nearly circular, coplanar, low-mass two-planet systems. It is not an N-body integration, proof of gigayear stability, or general criterion for resonant systems.

## Weighted circular-RV scan with instrument offsets

For each trial period fit instrument-specific intercepts plus cosine and sine by weighted least squares. Compare `chi2(P)` with the offset-only null via `1 - chi2(P)/chi2_null`. Also compute the cadence spectral window `|mean(exp(2*pi*i*t/P))|^2`. The scan allows heteroscedastic measurement errors and multiple instruments. It does **not** estimate detection significance or a false-alarm probability, model stellar jitter/correlated noise, or account for the look-elsewhere effect. Peaks must not be presented as confirmed planets.

The tests cover analytical limits, input validation, deterministic Monte Carlo behavior, mass sensitivity, orbital-order crossing, and a synthetic RV injection with two different instrument zero points. Run `pytest tests/test_robustness.py` from an editable installation; CI's existing `ruff`, `mypy`, and `pytest` checks should be retained.
