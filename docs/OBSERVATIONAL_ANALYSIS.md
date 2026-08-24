# Observational analysis

The package implements flux normalisation, linear ephemerides, O−C residuals, transit probability, circular multi-planet RV forward models and explicit instrument offsets. These functions are tested on synthetic controls only.

The intended observed-data flow is: MAST metadata inventory → target/product ranking → selective FITS download → quality filtering → normalisation/detrending → transit fitting → residuals. RV data require a public DACE or DOI-backed source, instrument labels and independent zero points. No observed time series is bundled or displayed in v0.1; this avoids confusing synthetic forward models with telescope measurements.

