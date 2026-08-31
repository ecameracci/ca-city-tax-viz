"""Load 2021 Census neighbourhood population totals.

The source is City of Edmonton Open Data's Socrata export for
"2021 Federal Census: Population" (dataset eg3i-f4bj), which is the same
2021 Federal Census population source surfaced through the City's Tableau
Neighbourhood Profiles workbook. One row is one 2021 Census neighbourhood total.
"""

from pathlib import Path

import pandas as pd


POPULATION_COLUMNS = ["census_population_2021"]

# The current assessment/boundary data uses WÎHKWÊNTÔWIN; the 2021 Census
# population table still uses the former OLIVER name. Treat this as the same
# neighbourhood when joining a Census denominator.
NAME_CORRECTIONS = {
    "OLIVER": "WÎHKWÊNTÔWIN",
}


def load_population(path: str | Path) -> pd.DataFrame:
    """Return 2021 Census population totals keyed by neighbourhood_name."""
    df = pd.read_csv(path)
    required = {"neighbourhood", "total_population"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Population file {path} missing required column(s): {', '.join(sorted(missing))}"
        )

    out = pd.DataFrame({
        "neighbourhood_name": df["neighbourhood"].astype(str).str.strip().str.upper(),
        "census_population_2021": pd.to_numeric(df["total_population"], errors="coerce"),
    })
    out["neighbourhood_name"] = out["neighbourhood_name"].replace(NAME_CORRECTIONS)
    out = out.dropna(subset=["census_population_2021"])
    out["census_population_2021"] = out["census_population_2021"].astype(int)

    dup = out[out["neighbourhood_name"].duplicated(keep=False)]
    if not dup.empty:
        names = ", ".join(sorted(dup["neighbourhood_name"].unique()))
        raise ValueError(f"Population file has duplicate neighbourhood rows after normalization: {names}")

    return out[["neighbourhood_name", *POPULATION_COLUMNS]]
