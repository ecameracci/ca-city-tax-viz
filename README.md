# Edmonton Revenue Per Acre Analysis

A public fiscal analysis comparing Edmonton's property tax revenue to the cost of servicing it, by area.

[Edmonton Tax Visualization](https://ecameracci.github.io/ca-city-tax-viz/)

## Multi-city status

The live deployment currently ships the Edmonton dataset. A city selector scaffold has been added for future adapters, and source manifests have been researched for **Vancouver**, **Calgary**, **Toronto**, **Hamilton**, and **Montréal** under `data/cities/` and `docs/cities/`. Those cities remain disabled in the public dropdown until their generated neighbourhood-level data files exist and pass validation.

The expansion is intentionally adapter-based: Calgary, Vancouver, and Montréal have plausible public revenue/value paths, but with local tax semantics; Toronto and Hamilton have strong spatial/service open data but no Edmonton-equivalent open assessment roll, so their revenue/value lenses must stay unavailable unless lawful aggregate assessment data is obtained.

## What This Is

Several published studies have examined the fiscal balance of suburban development in Edmonton. A Sustainable Prosperity report found that costs to the city will exceed revenues by **nearly $4 billion over 60 years** across just 17 planned new developments. A 2016 analysis of three new neighbourhoods (Decoteau, Riverview, Horse Hills) found they'll cost **$1.4 billion more** than they'll generate over 50 years.

No comprehensive, public **revenue-per-acre analysis** has been published for Edmonton — the kind of spatial fiscal analysis that presents this data at the neighbourhood level for residents and councillors.

The goal: map Edmonton's property tax revenue and estimated service costs against land area, broken out by area and development pattern — downtown mixed-use and established infill areas alongside suburban greenfield expansion — and present the per-acre figures.

## Why Now

- Edmonton recently raised property taxes by **6.9%**
- Council is actively debating development costs and suburban expansion
- Edmonton has excellent open data infrastructure (~448,000 property assessment records publicly available)
- No comparable public analysis exists for Edmonton, despite Calgary and Ottawa having attempted versions of this work

## Methodology

This project is inspired by the **revenue-per-acre** framework developed by [Urban3](https://www.urbanthree.com/) and popularized by [Strong Towns](https://www.strongtowns.org/), adapted for Edmonton's data environment. (Methodological lineage note: Urban3's denominator is parcel acres — this project's **lot-acre** mode; the **ground-acre** default is this project's own robustness-motivated addition. See `docs/FINDINGS_denominator_cardinality.md`.)

**Core calculation:**
```
Municipal levy (or assessed value) ÷ Neighbourhood area = Revenue (value) per acre
```

with a toggleable denominator: **ground acres** (boundary area — robust to record-to-parcel cardinality issues) or **parcel/lot acres** (deduplicated titled lot area — the Urban3-analogous "developable land" view, with a low-parcel-fraction guard). The revenue numerator is the per-account municipal levy computed from assessed value × the class mill rate.

The **cost side** layers service supply and modeled service cost per acre: road network supply, a bylaw-native stormwater charge model, fire-rescue service demand, and a per-connection water/sanitary model — each validated against published figures where possible (`docs/FINDINGS_utility_validation.md`). A top-level **Cost** metric summarizes the modeled roads + fire cost per acre where that data is available. Modeled figures are labeled *modeled, not billed*.

A separate **Transportation** view compares measured road length density, dedicated bike-route length density, and **City-managed public parking supply** from parkades and surface lots. The mode can be absolute neighbourhood supply, `km / km²` for roads/bike and stalls per `km²` for parking, per-1,000-resident metrics when 2021 Census population ships, or **Operating cost**: modeled annual City operating cost for the selected road, bike, or parking layer. Road/bike length is centreline / route length, not vehicle lane-kilometres; parking is City-managed only, not all parking in Edmonton; and operating-cost figures are not lifecycle/full-city costs.

**Data sources (all open data):**
- [Property Assessment Data](https://data.edmonton.ca/City-Administration/Property-Assessment-Data-Current-Calendar-Year-/q7d6-ambg) (~440,000 records, refreshed weekly, annual roll)
- Neighbourhood boundaries, Zoning Bylaw geometry, road centrelines, dedicated cycling infrastructure, City-managed public parking facilities, fire-rescue events & stations, transit schedule outputs, and property information (lot sizes) — all from the [Edmonton Open Data Portal](https://data.edmonton.ca/)
- [2021 Federal Census: Population](https://data.edmonton.ca/d/eg3i-f4bj) (`eg3i-f4bj`) from the City of Edmonton Neighbourhood Profiles / Federal Census 2021 source, used only as a Transportation per-resident denominator
- Published mill rates and utility tariffs (EPCOR bylaw rates, franchise fee schedules)

**Tooling:** Python only (pandas + geopandas + shapely; deck.gl in the browser) — no GIS desktop software. The full pipeline regenerates from open data in one command and runs weekly in CI.

## The Data Challenge (resolved)

Edmonton transferred parcel-level GIS *boundary* data to AltaLIS in November 2021 — it's no longer freely available. The project resolved this without AltaLIS, GEODE, or FOIP:

1. **Neighbourhood-level aggregation** on the free boundary file is the primary unit — the same resolution as Ottawa's Hemson study and the Halifax cost-of-service research.
2. **Lot areas** (not boundary geometry) turn out to be in the open [Property Information dataset](https://data.edmonton.ca/) (`dkk9-cj3x`), which — with a repeat-aware deduplication heuristic for condo/multi-unit records (`docs/FINDINGS_lot_dedupe.md`) — supports the parcel-acre denominator and a 100 m grid view at near-Urban3 detail.

Work that would genuinely need parcel *geometry* is catalogued in `docs/PARCEL_LEVEL_OPPORTUNITIES.md`.

## Comparable Work

- **Ottawa (2021):** Hemson Consulting analysis found suburban greenfield development runs a **$465/person/year deficit** while high-density infill generates a **$606/person/year surplus**. Councillor Shawn Menard requested and publicized this; it became a major input to Ottawa's growth strategy.
- **Lafayette, LA:** Urban3's parcel-by-parcel analysis found $32 billion in infrastructure obligations against $16 million in annual maintenance revenue. Apparently the most comprehensive fiscal analysis done for a North American city.
- **Halifax:** Academic cost-of-service study across 8 settlement types found road costs of $1,053/household/year at low density vs. $26 at high density — roughly a **40:1 ratio**.
- **Arlington, VA (Rosslyn–Ballston corridor):** Transit-oriented corridor occupying roughly **8% of the county's land** generates about **33% of its tax revenue**, alongside some of the lowest tax rates in Northern Virginia — a revenue-side example at scale.
- **Calgary (2022):** Revenue-only analysis without a cost side.

## Status

**Live:** interactive 3D map at **https://ecameracci.github.io/ca-city-tax-viz/**
— municipal tax revenue, assessed value, and modeled roads + fire cost per acre
by neighbourhood, with land-use set-aside, residential-only, Transportation,
Services, Ratio, Uses, Development, and Glass-grid lenses.

**Data-quality reports:** **https://ecameracci.github.io/ca-city-tax-viz/notebooks/**
— standalone, reproducible findings about defects in Edmonton's published open
data, each recomputing every figure at run time and asserting its own
invariants:

- [The current assessment roll is published under the wrong coverage year](https://ecameracci.github.io/ca-city-tax-viz/notebooks/roll-year-metadata.html)
  — `q7d6-ambg`'s `Period of Coverage` says 2025; the rows are the 2026 roll.
- [Whole buildings are missing from the 2024 slice of the Historical roll](https://ecameracci.github.io/ca-city-tax-viz/notebooks/historical-2024-gap.html)
  — 2,448 accounts across 188 neighbourhoods, 29 addresses losing every account.
- [What public data can and cannot say about tax-exempt property](https://ecameracci.github.io/ca-city-tax-viz/notebooks/exemption-uncertainty.html)
  — sizing a ~$15B gap, and why public data cannot resolve it.

Sources are under `notebooks/standalone/`; the register of known issues and
whether anyone has been told is `docs/DATA_ISSUES.md`.

**Full / specialist build:** **https://ecameracci.github.io/ca-city-tax-viz/full/**
— the same map with additional specialist controls (Infill mode, Industrial
metric, deeper data-detail) exposed. This is the build for anyone visiting the
repo directly; the public root above is the streamlined view.

The **cost side is
built** (`docs/SPEC_services.md`, `docs/SPEC_utilities.md`): a Services view
layers the city-maintained road network (road supply per acre), a **modeled
stormwater charge** per acre, **fire-rescue service demand** per acre, and a
**modeled water/sanitary charge** per acre; the top-level Cost metric shows the
modeled roads + fire cost per acre; and a Ratio view shows **revenue per road
metre** or **revenue as a multiple of modeled roads + fire service cost**. A
Transportation view compares road kilometres, dedicated bike-route kilometres,
and City-managed parking by absolute supply, area, Census-backed per-resident
denominator, or modeled annual **Operating cost** for the selected transportation
asset/program when the needed fields are present. A Uses view maps the zoning bylaw's land-use
categories, and a Glass view renders the metric in **100 m grid cells** (the
Urban3-style detail level). Both the Money and Glass views toggle between
ground acres and **parcel (lot) acres** as the denominator. A weekly GitHub
Action regenerates the data and publishes a clean static artifact branch (see
`docs/SPEC_deployment.md`).

See [`/research`](/research) for background findings and data source inventory.

## Technical Docs

- [`docs/METHODS.md`](docs/METHODS.md) — how the numbers are made: metric definitions, denominators, models, validation, limitations
- [`docs/VERIFICATION.md`](docs/VERIFICATION.md) — how to check the pipeline actually ran correctly, not just read about how it's supposed to work
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — dev pipeline, setup, coding conventions, AI-assisted workflow
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — module contracts and data flow
- [`docs/SPEC_phase1.md`](docs/SPEC_phase1.md) — Phase 1 deliverable and acceptance criteria

## Contributing / Contact

This is an independent civic project. If you work in urban planning, municipal finance, or GIS and want to collaborate — or if you have access to data that could help — get in touch.

For code contributions, see [`CONTRIBUTING.md`](CONTRIBUTING.md).
