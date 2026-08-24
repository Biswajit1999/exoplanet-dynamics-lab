"""Generate thin notebooks that exercise the reusable package rather than duplicating it."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = [
    ("01_archive_population.ipynb", "Archive population", "from exodynamics.pipeline import analyse_population\nanalyse_population()"),
    ("02_multi_planet_identification.ipynb", "Multi-planet identification", "import pandas as pd\npd.read_parquet('../results/multi_planet_systems.parquet').head()"),
    ("03_system_reconstruction.ipynb", "System reconstruction", "import pandas as pd\npd.read_csv('../results/system_selection.csv').head()"),
    ("04_rebound_nbody.ipynb", "REBOUND N-body", "from exodynamics.dynamics.nbody import PlanetInitialCondition, integrate_system"),
    ("05_stability_analysis.ipynb", "Stability diagnostics", "import json\njson.load(open('../results/simulation_summary.json'))"),
    ("06_resonance_analysis.ipynb", "Resonance proximity", "import pandas as pd\npd.read_parquet('../results/resonance_results.parquet').query(\"classification == 'near_commensurability'\").head()"),
    ("07_kepler_lightcurve.ipynb", "Kepler light-curve workflow", "from exodynamics.observations.transit import normalize_flux\n# Retrieval is selective; no observed data are bundled in this release."),
    ("08_ttv_analysis.ipynb", "Transit timing variations", "from exodynamics.observations.transit import observed_minus_calculated"),
    ("09_radial_velocity.ipynb", "Radial velocity", "from exodynamics.observations.rv import circular_multi_planet_rv"),
    ("10_observation_vs_simulation.ipynb", "Observation vs simulation", "# Requires an observed dataset with data_kind='observed'; none is claimed in v0.1."),
]


def main() -> None:
    for filename, title, code in NOTEBOOKS:
        notebook = {
            "cells": [
                {"cell_type": "markdown", "metadata": {}, "source": [f"# {title}\n", "Thin reproducible interface to the tested `exodynamics` package.\n"]},
                {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in code.splitlines()]},
            ],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11"}},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        (ROOT / "notebooks" / filename).write_text(json.dumps(notebook, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

