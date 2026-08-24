# Research notes

Research was performed before scientific implementation on 24 August 2026.

- NASA Exoplanet Archive TAP is the primary catalogue interface. The live schema was queried through `TAP_SCHEMA.columns`; no historical column list was assumed. The official TAP documentation lists `ps`, `pscomppars`, and `toi` and recommends TAP+/PyVO for large responses.
- MAST recommends metadata/target crossmatching before bulk TESS acquisition; a single extended-mission sector can approach 1.8 TB. EXODYNAMICS therefore inventories products before selective FITS retrieval.
- REBOUND provides symplectic WHFast for efficient nearly Keplerian integrations, adaptive IAS15 for difficult configurations, and MEGNO through variational equations. This release uses WHFast for the selected compact system and checks both energy and angular momentum.
- Gaia DR3 is the documented astrometric release considered for later host crossmatching. Archive-provided Gaia DR3 identifiers are retained now; no new positional Gaia query is claimed.

Authoritative interfaces: [NASA TAP](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html), [PS/PSCompPars definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html), [MAST TESS-SPOC](https://archive.stsci.edu/hlsp/tess-spoc), [Gaia DR3](https://gea.esac.esa.int/archive/documentation/GDR3/), [REBOUND](https://rebound.hanno-rein.de/).

