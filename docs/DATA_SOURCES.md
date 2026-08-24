# Data sources

| Archive | Table | Role | Snapshot policy |
|---|---|---|---|
| NASA Exoplanet Archive | `ps` | literature-level planetary-system rows and default solution | selected columns, raw CSV excluded, query/checksum committed |
| NASA Exoplanet Archive | `pscomppars` | one composite row per confirmed planet | selected columns |
| NASA Exoplanet Archive | `toi` | TESS candidate population | selected columns |
| NASA Exoplanet Archive | `CUMULATIVE` | Kepler cumulative KOI population | selected columns |
| NASA Exoplanet Archive | `Q1_Q17_DR25_TCE` | final Kepler threshold-crossing events | selected columns |

Raw responses are reproducible only while upstream data remain available. Each response has a timestamp, ADQL query and SHA-256 in `data/manifests/`. This is strong provenance but not a permanent archive; release assets should include compressed responses where licensing and hosting limits permit.

MAST, DACE, and Gaia remain documented adapters/next-stage sources. Version 0.1 does not claim observed light-curve, RV, or fresh Gaia crossmatch results.

