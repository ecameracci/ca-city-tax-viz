"""City-managed public parking supply per neighbourhood.

Loads the City of Edmonton SODA2 feed ``tsq5-xp73`` (Parkades and Surface Lots)
and produces two outputs:

* a neighbourhood aggregate for the Transportation lens; and
* a tiny web JSON of facility dots with their rate/use rows.

Important scope guard: this is **City-managed public parking supply**, not all
parking in Edmonton. The feed has rate/use rows, not one row per physical asset:
Century Place Parkade and City Hall Parkade appear more than once for different
use/rate products. The loader therefore preserves all rate rows in the point
popup but deduplicates capacity by physical facility before summing stalls.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

logger = logging.getLogger(__name__)

PROJECTED_CRS = "EPSG:3400"
FACILITY_TYPES = ("Parkade", "Surface Lot")
TYPE_TO_PREFIX = {"Parkade": "parkade", "Surface Lot": "surface_lot"}
WEB_PRECISION = 5

_LOCATION_RE = re.compile(r"\(?\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)\s*\)?")


def _parse_location(value: object) -> tuple[float | None, float | None]:
    """Parse Socrata CSV location_1 values like ``(53.54, -113.49)``.

    The JSON endpoint carries a nested ``{latitude, longitude}``, but the CSV
    export used by ``download_data.py`` flattens that into one string. Return
    ``(lat, lon)`` and let the caller report/drop nulls.
    """
    if pd.isna(value):
        return None, None
    m = _LOCATION_RE.search(str(value))
    if not m:
        return None, None
    return float(m.group(1)), float(m.group(2))


def _money(value: object) -> float | None:
    v = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return None if pd.isna(v) else float(v)


def _clean_type(value: object) -> str:
    t = str(value).strip() if not pd.isna(value) else ""
    if t not in FACILITY_TYPES:
        logger.warning("Parking facility type %r is not in %s — kept as written", t, FACILITY_TYPES)
    return t


def _facility_key(row: pd.Series) -> str:
    # Name is the stable human key; coordinates disambiguate defensively if a
    # future feed reuses a name at two places.
    return (
        str(row["parking_facilities"]).strip().casefold(),
        round(float(row["lat"]), 6),
        round(float(row["lon"]), 6),
    ).__repr__()


def _load_rows(parking_csv: str | Path) -> pd.DataFrame:
    df = pd.read_csv(parking_csv)
    needed = {
        "parking_facilities", "owned_leased", "type", "total_stalls", "use",
        "billing_type", "regular_rate", "_5_gst", "monthly_rate",
        "effective_year", "location_1",
    }
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(
            f"expected parking columns missing from {parking_csv}: {sorted(missing)}; "
            f"headers: {list(df.columns)}"
        )

    loc = df["location_1"].map(_parse_location)
    df["lat"] = [x[0] for x in loc]
    df["lon"] = [x[1] for x in loc]
    bad_coord = df["lat"].isna() | df["lon"].isna()
    if bad_coord.any():
        logger.warning("%d parking row(s) have null/unparseable coordinates — dropped", int(bad_coord.sum()))
    df = df.loc[~bad_coord].copy()
    if df.empty:
        raise ValueError(f"no parking rows with coordinates in {parking_csv}")

    df["parking_facilities"] = df["parking_facilities"].astype("string").str.strip()
    df["owned_leased"] = df["owned_leased"].astype("string").str.strip()
    df["type"] = df["type"].map(_clean_type)
    df["total_stalls"] = pd.to_numeric(df["total_stalls"], errors="coerce")
    missing_stalls = df["total_stalls"].isna()
    if missing_stalls.any():
        logger.warning("%d parking row(s) have null/non-numeric total_stalls — treated as 0", int(missing_stalls.sum()))
        df["total_stalls"] = df["total_stalls"].fillna(0)
    df["total_stalls"] = df["total_stalls"].astype(int)
    df["facility_key"] = df.apply(_facility_key, axis=1)
    return df


def _facilities_with_neighbourhoods(
    rows: pd.DataFrame,
    boundaries: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """Deduplicate rate rows to physical facilities and spatially assign hoods."""
    if boundaries.crs is None or boundaries.crs.to_string() != PROJECTED_CRS:
        raise ValueError(f"boundaries must be in {PROJECTED_CRS} (got {boundaries.crs})")

    # One physical facility per key. Inconsistency across duplicate rate rows is
    # upstream drift: warn, then take first/max conservatively.
    for key, g in rows.groupby("facility_key"):
        for col in ("parking_facilities", "owned_leased", "type"):
            vals = sorted(set(g[col].dropna().astype(str)))
            if len(vals) > 1:
                logger.warning("Parking facility %s has inconsistent %s values: %s", key, col, vals)
        stalls = sorted(set(g["total_stalls"].dropna().astype(int)))
        if len(stalls) > 1:
            logger.warning("Parking facility %s has inconsistent total_stalls values: %s; using max", key, stalls)

    facilities = (
        rows.sort_values(["parking_facilities", "facility_key"])
        .groupby("facility_key", as_index=False)
        .agg(
            parking_facilities=("parking_facilities", "first"),
            owned_leased=("owned_leased", "first"),
            type=("type", "first"),
            total_stalls=("total_stalls", "max"),
            lat=("lat", "first"),
            lon=("lon", "first"),
            rate_rows=("facility_key", "size"),
        )
    )

    pts = gpd.GeoDataFrame(
        facilities,
        geometry=[Point(xy) for xy in zip(facilities["lon"], facilities["lat"])],
        crs="EPSG:4326",
    ).to_crs(PROJECTED_CRS)
    assigned = gpd.sjoin(
        pts,
        boundaries[["neighbourhood_name", "geometry"]],
        how="left",
        predicate="within",
    ).drop(columns=["index_right"])
    outside = assigned["neighbourhood_name"].isna()
    if outside.any():
        logger.warning(
            "%d parking facilit%s outside all neighbourhood boundaries: %s",
            int(outside.sum()), "y" if int(outside.sum()) == 1 else "ies",
            sorted(assigned.loc[outside, "parking_facilities"]),
        )
    return rows, assigned.drop(columns="geometry")


def load_parking(parking_csv: str | Path, boundaries: gpd.GeoDataFrame) -> pd.DataFrame:
    """Aggregate city-managed parking facilities by neighbourhood.

    Returns a DataFrame keyed by ``neighbourhood_name`` with deduplicated
    facility counts and stall capacity. A neighbourhood absent from the result
    has zero City-managed public parking facilities in this feed.
    """
    rows = _load_rows(parking_csv)
    _, facilities = _facilities_with_neighbourhoods(rows, boundaries)
    facilities = facilities[facilities["neighbourhood_name"].notna()].copy()

    if facilities.empty:
        logger.warning("No parking facilities assigned to neighbourhoods")
        return pd.DataFrame(columns=[
            "neighbourhood_name", "parking_facilities_total",
            "parking_parkade_facilities", "parking_surface_lot_facilities",
            "parking_stalls_total", "parking_parkade_stalls", "parking_surface_lot_stalls",
        ])

    base = facilities.groupby("neighbourhood_name").agg(
        parking_facilities_total=("facility_key", "nunique"),
        parking_stalls_total=("total_stalls", "sum"),
    )
    for facility_type, prefix in TYPE_TO_PREFIX.items():
        sub = facilities[facilities["type"] == facility_type].groupby("neighbourhood_name").agg(
            **{
                f"parking_{prefix}_facilities": ("facility_key", "nunique"),
                f"parking_{prefix}_stalls": ("total_stalls", "sum"),
            }
        )
        base = base.join(sub, how="left")

    out = base.fillna(0).reset_index()
    count_cols = [c for c in out.columns if c != "neighbourhood_name"]
    out[count_cols] = out[count_cols].astype(int)
    logger.info(
        "Parking supply: %d physical facilities from %d rate/use rows; %d stalls "
        "(%d parkade, %d surface lot) assigned to %d neighbourhood(s)",
        facilities["facility_key"].nunique(), len(rows),
        int(out["parking_stalls_total"].sum()),
        int(out["parking_parkade_stalls"].sum()),
        int(out["parking_surface_lot_stalls"].sum()),
        len(out),
    )
    return out


def export_parking_web(
    parking_csv: str | Path,
    boundaries: gpd.GeoDataFrame,
    out_path: str | Path,
    precision: int = WEB_PRECISION,
) -> int:
    """Write facility dots + rate/use rows for the web map.

    Output shape: ``{"facilities": [{lon, lat, name, type, stalls, ...}]}``.
    Physical facilities are deduplicated for capacity, but their source rows are
    retained under ``options`` so the popup can show transient/monthly/night-rate
    distinctions without pretending they are separate parkades.
    """
    rows = _load_rows(parking_csv)
    rows, facilities = _facilities_with_neighbourhoods(rows, boundaries)
    by_key = {k: g for k, g in rows.groupby("facility_key", sort=False)}

    records = []
    for f in facilities.sort_values(["type", "parking_facilities"]).itertuples(index=False):
        options = []
        for _, r in by_key[f.facility_key].iterrows():
            options.append({
                "use": "" if pd.isna(r["use"]) else str(r["use"]),
                "billing": "" if pd.isna(r["billing_type"]) else str(r["billing_type"]),
                "regular": _money(r["regular_rate"]),
                "gst": _money(r["_5_gst"]),
                "monthly": _money(r["monthly_rate"]),
                "year": None if pd.isna(r["effective_year"]) else str(r["effective_year"]),
            })
        records.append({
            "lon": round(float(f.lon), precision),
            "lat": round(float(f.lat), precision),
            "name": str(f.parking_facilities),
            "owned": str(f.owned_leased),
            "type": str(f.type),
            "stalls": int(f.total_stalls),
            "neighbourhood": "" if pd.isna(f.neighbourhood_name) else str(f.neighbourhood_name),
            "rateRows": int(f.rate_rows),
            "options": options,
        })

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fp:
        json.dump({"facilities": records}, fp, separators=(",", ":"), ensure_ascii=False)
    logger.info("Wrote %d parking facility dots to %s", len(records), out)
    return len(records)
