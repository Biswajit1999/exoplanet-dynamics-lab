"""Produce seeded, synthetic dynamics sensitivity JSON (no new observations)."""
import json
from pathlib import Path

from exodynamics.dynamics.robustness import (
    hill_logmass_sensitivity, synthetic_ephemeris_sensitivity,
    synthetic_resonance_sampling,
)


def main() -> None:
    payload = {
        "schema": "exodynamics-robustness/1", "is_observation": False,
        "resonance_sampling": synthetic_resonance_sampling(),
        "hill_mass_prior": [hill_logmass_sensitivity(mass_correlation=r)
                            for r in (-0.8, 0.0, 0.8)],
        "ephemeris": synthetic_ephemeris_sensitivity(),
    }
    out = Path("results/dynamics_robustness.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "ephemeris": payload["ephemeris"],
                      "hill_mass_prior": payload["hill_mass_prior"]}, indent=2))


if __name__ == "__main__":
    main()
