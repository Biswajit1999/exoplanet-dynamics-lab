# Methods

## Population

The survey retrieves five genuine TAP tables. `ps` is kept at literature-row granularity; confirmed-planet analysis filters `default_flag = 1`. Systems group by the archive canonical `hostname`. Similar strings are never merged. Multiplicity uses the number of distinct default `pl_name` values.

## Evidence tiers

The reconstruction score is an evidence-coverage index, not a probability. It combines completeness across period, mass, radius, eccentricity, transit epoch and inclination (35%), mass coverage (35%), and epoch coverage (30%). Tier A requires periods, ≥80% mass coverage and ≥65% combined completeness. Tier B supports prior ensembles; Tier C is visualisation only; Tier D is excluded.

## Commensurabilities

Adjacent planets are ordered by period and compared with 2:1, 3:2, 4:3, 5:4, 5:3, and 3:1. A fractional offset within 2% is labelled *near commensurability*. This is not a resonance detection: confirming resonance requires a resonant angle to librate in a sufficiently constrained integration.

## N-body

REBOUND uses units of years, AU and solar masses. WHFast timestep is the shortest orbital period divided by 100. The selected system is integrated for 10 years with 700 stored outputs. A result passes the release criterion when both relative energy and angular-momentum drifts are below `1e-7`.

