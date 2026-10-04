# Methods

## Population

The survey retrieves five genuine TAP tables. `ps` is kept at literature-row granularity; confirmed-planet analysis filters `default_flag = 1`. Systems group by the archive canonical `hostname`. Similar strings are never merged. Multiplicity uses the number of distinct default `pl_name` values.

## Evidence tiers

The reconstruction score is an evidence-coverage index, not a probability. It combines completeness across period, mass, radius, eccentricity, transit epoch and inclination (35%), mass coverage (35%), and epoch coverage (30%). Tier A requires periods, ≥80% mass coverage and ≥65% combined completeness. Tier B supports prior ensembles; Tier C is visualisation only; Tier D is excluded. Candidate ordering is deterministic: tier, descending coverage index, descending planet count, then archive hostname. The final hostname tie-breaker carries no scientific meaning, and the ordering is not a target-value ranking.

## Commensurabilities

Adjacent planets are ordered by period and compared with 2:1, 3:2, 4:3, 5:4, 5:3, and 3:1. A fractional offset within 2% is labelled *near commensurability*. This is not a resonance detection: confirming resonance requires a resonant angle to librate in a sufficiently constrained integration.

## N-body

REBOUND uses units of years, AU and solar masses. WHFast timestep is the shortest orbital period divided by 100. The selected system is integrated for 10 years with 700 stored outputs. Because `exact_finish_time=0` preserves symplectic stepping, products record actual integrator times alongside requested sample times. A result passes only when the maximum sampled relative energy and angular-momentum drifts—not merely their final values—are both below `1e-7`.

Numerical convergence is evaluated at 50, 100 and 200 steps per shortest orbit. Dependence on unknown orbital phase is assessed with 32 deterministic independent-uniform mean-anomaly draws (`seed=20261004`) over the same 10-year interval. This ensemble samples a declared project prior, not an observational posterior; bounded behaviour over this interval is not a general stability result.

