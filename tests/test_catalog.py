import pandas as pd

from exodynamics.catalog.population import build_system_catalog, multiplicity_class


def test_multiplicity_classes() -> None:
    assert multiplicity_class(1) == "single_planet"
    assert multiplicity_class(5) == "five_plus_planet"
    assert multiplicity_class(6) == "high_multiplicity"


def test_grouping_uses_exact_archive_hostname() -> None:
    frame = pd.DataFrame(
        {
            "hostname": ["Star A", "Star A", "Star-A"],
            "pl_name": ["Star A b", "Star A c", "Star-A b"],
            "default_flag": [1, 1, 1],
            "pl_orbper": [1.0, 2.0, 3.0],
        }
    )
    result = build_system_catalog(frame)
    assert len(result) == 2
    assert result.iloc[0]["n_planets"] == 2

