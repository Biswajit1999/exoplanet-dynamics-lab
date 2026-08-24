"""End-to-end population survey and browser-export pipeline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from exodynamics.archives.nasa_tap import NasaTapClient
from exodynamics.catalog.population import SurveySummary, build_alias_table, build_system_catalog
from exodynamics.dynamics.diagnostics import nearest_commensurability

ROOT = Path(__file__).resolve().parents[2]

PS_COLUMNS = [
    "pl_name", "hostname", "default_flag", "sy_pnum", "discoverymethod", "disc_year",
    "disc_facility", "pl_orbper", "pl_orbpererr1", "pl_orbpererr2", "pl_orbsmax",
    "pl_rade", "pl_radeerr1", "pl_radeerr2", "pl_bmasse", "pl_bmasseerr1",
    "pl_bmasseerr2", "pl_orbeccen", "pl_orbeccenerr1", "pl_orbeccenerr2",
    "pl_orbincl", "pl_tranmid", "pl_tranmiderr1", "pl_tranmiderr2", "tran_flag",
    "rv_flag", "ttv_flag", "st_mass", "st_rad", "st_teff", "ra", "dec", "sy_dist",
    "gaia_dr3_id", "tic_id", "hd_name", "hip_name", "releasedate", "rowupdate",
]


def _available_columns(client: NasaTapClient, table: str, desired: list[str]) -> list[str]:
    available = set(client.table_columns(table))
    selected = [column for column in desired if column in available]
    if len(selected) < 2:
        raise RuntimeError(f"schema discovery found too few usable columns in {table}")
    return selected


def acquire_population(root: Path = ROOT) -> list[dict[str, object]]:
    client = NasaTapClient()
    raw = root / "data" / "raw"
    manifests = root / "data" / "manifests"
    acquisitions = []
    ps_columns = _available_columns(client, "ps", PS_COLUMNS)
    queries = {
        "ps": f"select {','.join(ps_columns)} from ps",
        "pscomppars": "select pl_name,hostname,sy_pnum,pl_orbper,pl_orbsmax,pl_rade,pl_bmasse,pl_orbeccen,st_mass,st_rad,ra,dec,sy_dist from pscomppars",
        "toi": "select tid,toi,toipfx,pl_pnum,tfopwg_disp,pl_orbper,pl_tranmid,pl_trandurh,pl_trandep,pl_rade,ra,dec,st_tmag,st_teff,st_logg,st_rad from toi",
        "CUMULATIVE": "select kepid,kepoi_name,kepler_name,koi_disposition,koi_pdisposition,koi_period,koi_time0bk,koi_depth,koi_duration,koi_prad,koi_steff,koi_srad,koi_kepmag,ra,dec from CUMULATIVE",
        "Q1_Q17_DR25_TCE": "select kepid,tce_plnt_num,tce_period,tce_time0bk,tce_duration,tce_depth,tce_prad,tce_maxmesd,tce_rogue_flag from Q1_Q17_DR25_TCE",
    }
    for table, query in queries.items():
        destination = raw / f"{table.lower()}.csv"
        acquisition = client.acquire(
            table=table,
            adql=query,
            destination=destination,
            manifest_destination=manifests / f"{table.lower()}.json",
        )
        acquisitions.append(acquisition.__dict__)
    return acquisitions


def analyse_population(root: Path = ROOT) -> dict[str, object]:
    raw = root / "data" / "raw"
    results = root / "results"
    results.mkdir(exist_ok=True)
    ps = pd.read_csv(raw / "ps.csv", low_memory=False)
    defaults = ps[ps["default_flag"] == 1].copy()
    systems = build_system_catalog(defaults)
    multis = systems[systems["n_planets"] >= 2].copy()
    aliases = build_alias_table(defaults)

    pairs: list[dict[str, object]] = []
    for host, group in defaults.dropna(subset=["pl_orbper"]).groupby("hostname"):
        ordered = group.sort_values("pl_orbper")
        for (_, inner), (_, outer) in zip(ordered.iloc[:-1].iterrows(), ordered.iloc[1:].iterrows(), strict=False):
            result = nearest_commensurability(float(inner["pl_orbper"]), float(outer["pl_orbper"]))
            pairs.append(
                {
                    "hostname": host,
                    "inner_planet": inner["pl_name"],
                    "outer_planet": outer["pl_name"],
                    "period_ratio": result.observed_ratio,
                    "nearest_ratio": f"{result.numerator}:{result.denominator}",
                    "fractional_offset": result.fractional_offset,
                    "classification": result.classification,
                    "interpretation": "period-ratio diagnostic only; libration not tested",
                }
            )
    resonance = pd.DataFrame(pairs)
    near_count = int((resonance["classification"] == "near_commensurability").sum()) if not resonance.empty else 0

    manifest_files = sorted((root / "data" / "manifests").glob("*.json"))
    acquisitions = [json.loads(path.read_text(encoding="utf-8")) for path in manifest_files]
    survey_counts = SurveySummary(
        archive_rows_surveyed=sum(int(item["row_count"]) for item in acquisitions),
        confirmed_planets=int(defaults["pl_name"].nunique()),
        host_systems=int(defaults["hostname"].nunique()),
        multi_planet_systems=len(multis),
        high_multiplicity_systems=int((multis["n_planets"] >= 6).sum()),
        tier_a_systems=int((multis["tier"] == "A").sum()),
        tier_b_systems=int((multis["tier"] == "B").sum()),
        near_commensurate_pairs=near_count,
    ).as_dict()
    summary: dict[str, object] = {}
    summary.update(survey_counts)
    summary["archives"] = 1
    summary["data_last_synchronised"] = max(item["retrieval_timestamp_utc"] for item in acquisitions)
    summary["method_note"] = "Counts derive from timestamped live TAP responses; archive rows include repeated literature solutions in ps."

    systems.to_parquet(results / "system_completeness.parquet", index=False)
    multis.to_parquet(results / "multi_planet_systems.parquet", index=False)
    aliases.to_parquet(results / "alias_table.parquet", index=False)
    resonance.to_parquet(results / "resonance_results.parquet", index=False)
    pd.DataFrame(columns=["archive", "target", "mission", "product", "data_kind", "status"]).to_parquet(results / "observation_inventory.parquet", index=False)
    selection = multis.sort_values(["tier", "dynamical_reconstruction_confidence"], ascending=[True, False]).head(100)
    selection.to_csv(results / "system_selection.csv", index=False)
    (results / "archive_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (results / "provenance_manifest.json").write_text(json.dumps(acquisitions, indent=2), encoding="utf-8")

    web_data = root / "web" / "public" / "data"
    web_data.mkdir(parents=True, exist_ok=True)
    shutil.copy2(results / "archive_summary.json", web_data / "archive_summary.json")
    atlas_columns = [
        "canonical_system_id", "canonical_host", "n_planets", "multiplicity_class", "tier",
        "is_transiting", "is_rv_detected", "data_completeness", "dynamical_reconstruction_confidence",
    ]
    atlas = multis[atlas_columns].head(1000).replace({np.nan: None}).to_dict(orient="records")
    (web_data / "systems.json").write_text(json.dumps(atlas), encoding="utf-8")
    return summary


def survey(root: Path = ROOT) -> dict[str, object]:
    acquire_population(root)
    return analyse_population(root)
