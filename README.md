# Canadian City Revenue Per Acre Analysis

A public fiscal-analysis toolkit for comparing Canadian municipal property tax revenue, assessed value, and selected service-cost indicators by neighbourhood or local area. Edmonton is the current live reference implementation.

[Live visualization](https://ecameracci.github.io/ca-city-tax-viz/)

## Multi-city status

The live deployment currently ships the Edmonton dataset. A city selector scaffold has been added for future adapters, and source manifests have been researched for **Vancouver**, **Calgary**, **Toronto**, **Hamilton**, and **Montréal** under `data/cities/` and `docs/cities/`. Those cities remain disabled in the public dropdown until their generated neighbourhood-level data files exist and pass validation.

The expansion is intentionally adapter-based: Calgary and Vancouver have plausible public revenue/value paths, but with local tax semantics. Montréal has strong spatial/service open data and a possible but privacy-sensitive tax-bill-line path; it is not ready for full Edmonton-style value/revenue lenses until that method is validated and aggregated safely. Toronto and Hamilton have strong spatial/service open data but no Edmonton-equivalent open assessment roll, so their revenue/value lenses must stay unavailable unless lawful aggregate assessment data is obtained.

### City-by-city data gaps

These gaps are why only Edmonton is live today. A non-Edmonton city should not be marked `available: true` until its adapter has generated the required browser-facing GeoJSON/JSON outputs and the relevant caveats are represented in the UI.

#### Edmonton — live baseline

- **Available:** neighbourhood boundaries, current assessment roll, pinned municipal mill rates, property-information lot areas, zoning, roads, bike routes, transit stops, City-managed public parking facilities, fire/service layers, 2021 population denominator, and Edmonton-specific operating/service-cost assumptions.
- **Known gaps:** parcel boundary geometry is no longer freely available from the City, so parcel-shape analysis remains out of scope; optional feeds can be absent locally during regeneration; public data cannot fully resolve tax-exempt-property status or private parking supply.
- **Implication:** Edmonton remains the reference implementation, but its cost rates and field assumptions must not be reused for other cities without a city-specific adapter.

#### Calgary — strongest next revenue/value candidate

- **Available:** open parcel assessment records with assessed values, assessment class, community code/name, land size, and geometry; community boundaries; roads, bikeways/pathways, GTFS transit, parking-zone context, land-use districts, and 2021 census-by-community data candidates.
- **Gaps before live:** official/current tax-rate values need to be pinned from a defensible City source or bylaw and tested; loaders must map Calgary assessment classes, community geography, CRS/geometry, and land-use semantics into the shared contract; parcel-level roll/address artifacts must be stripped from web outputs.
- **Implication:** good first implementation target, but not just a dataset swap.

#### Vancouver — feasible with different tax semantics

- **Available:** Local Area boundaries, property tax report with values and `tax_levy`, parcel polygons, public streets, bikeways, parking meters, zoning districts, local-area census profiles, and TransLink GTFS.
- **Gaps before live:** `tax_levy` is an actual total property-tax notice amount, not a clean municipal-only Edmonton-style levy reconstructed from mill rates; municipal-only tax-rate reconstruction would need separate validation; Local Areas are coarser than Edmonton neighbourhoods; parcel/folio/address/legal-description fields must not be shipped raw.
- **Implication:** viable if the UI labels Vancouver revenue as actual/total notice levy or another Vancouver-specific metric, not Edmonton-equivalent modeled municipal levy.

#### Toronto — services/spatial first

- **Available:** neighbourhood boundaries/profiles, centreline, cycling network, TTC/GTFS candidates, Green P/parking facilities, zoning, permits, fire stations/incidents, and population data.
- **Gaps before live:** no open Edmonton-equivalent parcel/account assessment roll with assessed value, property class, and neighbourhood/coordinate fields was found; official assessment roll access is public-inspection/in-person and can include owner/tenant information, so scraping or republishing is not acceptable.
- **Implication:** Toronto should start with services/spatial overlays and keep revenue/value lenses disabled unless lawful aggregate assessment/value data is obtained.

#### Hamilton — services/spatial first

- **Available:** planning neighbourhoods/community boundaries, street-centreline/road-segment layers, bikeways, HSR stops/service candidates, zoning/context layers, parking/context candidates, and census/population geography inputs.
- **Gaps before live:** no open assessment roll with assessed value, class, and neighbourhood/account fields was found; available parcel/spatial layers do not provide the Edmonton-style value/revenue numerator; MPAC/Hamilton aggregate assessment inputs would need to be obtained lawfully and documented.
- **Implication:** Hamilton should keep revenue/value lenses disabled and focus first on spatial/service layers.

#### Montréal — spatial/service first; value/revenue experimental

- **Available:** quartiers sociologiques or housing-reference quartiers, borough/agglomeration boundaries, evaluation-unit geometry, Géobase road centreline, cycling network, STM GTFS, municipal paid parking places/rules, CUBF land-use/use-code proxy, and census/population candidates.
- **Gaps before live:** inspected `Unités d’évaluation foncière` fields do not include assessed/current property value; annual municipal tax-bill lines include `VAL_IMPOSABLE` and `MONTANT_DETAIL`, but they are granular account/address-level records with first-issuance and non-exhaustive-revenue caveats; current tax-rate coverage/semantics need verification; chosen neighbourhood geography and population apportionment need to be settled.
- **Privacy rule:** do not ship raw `ID_CUM`, account numbers, civic addresses, matricules, or unit-level geometry. Aggregate early, filter tax-line categories explicitly, and suppress small cells if needed.
- **Implication:** Montréal can be a strong spatial/service branch, but value/revenue should remain experimental until the tax-bill-line method is reviewed and safely aggregated.

## What This Is

Canadian municipalities make major land-use, infrastructure, and tax decisions with uneven public visibility into how revenue and service obligations vary across the city. This project turns open municipal datasets into a neighbourhood-scale fiscal map: property tax revenue or assessed value per acre, selected service-supply and service-cost indicators, and caveats about what each city’s public data can and cannot support.

The goal is a reusable, city-adapter-based toolkit for Canadian cities. Edmonton is the first complete implementation because its open assessment roll, neighbourhood boundaries, service layers, and published rates are strong enough to support a defensible live map today. Other cities are being researched and scaffolded without pretending their data is complete.

For the Edmonton baseline, several published studies have already examined the fiscal balance of suburban development. A Sustainable Prosperity report found that costs to the city will exceed revenues by **nearly $4 billion over 60 years** across just 17 planned new developments. A 2016 analysis of three new neighbourhoods (Decoteau, Riverview, Horse Hills) found they'll cost **$1.4 billion more** than they'll generate over 50 years.

## Why Now

- Canadian cities are raising property taxes while debating infrastructure backlogs, growth costs, infill, and suburban expansion.
- Open-data portals now publish enough boundary, assessment, transportation, zoning, and service information to make reproducible local fiscal analysis possible in some cities.
- The data is uneven: some cities can support revenue/value analysis, while others are currently limited to spatial/service overlays unless lawful aggregate assessment data is obtained.
- Edmonton has excellent open data infrastructure (~448,000 property assessment records publicly available), making it a practical first reference city for a broader Canadian tool.

## Methodology

This project is inspired by the **revenue-per-acre** framework developed by [Urban3](https://www.urbanthree.com/) and popularized by [Strong Towns](https://www.strongtowns.org/), adapted to Canadian municipal open-data environments. (Methodological lineage note: Urban3's denominator is parcel acres — this project's **lot-acre** mode; the **ground-acre** default is this project's own robustness-motivated addition. See `docs/FINDINGS_denominator_cardinality.md`.)

**Core calculation:**
```
Municipal levy (or assessed value) ÷ Neighbourhood area = Revenue (value) per acre
```

with a toggleable denominator: **ground acres** (boundary area — robust to record-to-parcel cardinality issues) or **parcel/lot acres** (deduplicated titled lot area — the Urban3-analogous "developable land" view, with a low-parcel-fraction guard). In the Edmonton implementation, the revenue numerator is the per-account municipal levy computed from assessed value × the class mill rate; other cities must use city-specific tax semantics.

The **cost side** layers service supply and modeled service cost per acre: road network supply, a bylaw-native stormwater charge model, fire-rescue service demand, and a per-connection water/sanitary model — each validated against published figures where possible (`docs/FINDINGS_utility_validation.md`). A top-level **Cost** metric summarizes the modeled roads + fire cost per acre where that data is available. Modeled figures are labeled *modeled, not billed*.

In the Edmonton implementation, a separate **Transportation** view compares measured road length density, dedicated bike-route length density, and **City-managed public parking supply** from parkades and surface lots. The mode can be absolute neighbourhood supply, `km / km²` for roads/bike and stalls per `km²` for parking, per-1,000-resident metrics when 2021 Census population ships, or **Operating cost**: modeled annual City operating cost for the selected road, bike, or parking layer. Road/bike length is centreline / route length, not vehicle lane-kilometres; parking is City-managed only, not all parking in Edmonton; and operating-cost figures are not lifecycle/full-city costs.

**Data sources:**
- The live Edmonton build uses open data from the [Edmonton Open Data Portal](https://data.edmonton.ca/), including [Property Assessment Data](https://data.edmonton.ca/City-Administration/Property-Assessment-Data-Current-Calendar-Year-/q7d6-ambg) (~440,000 records, refreshed weekly, annual roll), neighbourhood boundaries, Zoning Bylaw geometry, road centrelines, dedicated cycling infrastructure, City-managed public parking facilities, fire-rescue events & stations, transit schedule outputs, and property information/lot sizes.
- The Edmonton build also uses [2021 Federal Census: Population](https://data.edmonton.ca/d/eg3i-f4bj) (`eg3i-f4bj`) from the City of Edmonton Neighbourhood Profiles / Federal Census 2021 source as a Transportation per-resident denominator, plus published mill rates and utility tariffs.
- Future city builds use researched source manifests under `data/cities/`; each city needs an adapter that respects local assessment, tax, privacy, geography, and licensing rules.

**Tooling:** Python only (pandas + geopandas + shapely; deck.gl in the browser) — no GIS desktop software. The full pipeline regenerates from open data in one command and runs weekly in CI.

## The Data Challenge

Every Canadian city exposes a different slice of the fiscal picture: some publish parcel assessment values, some publish only spatial/service layers, and some publish tax-bill details with privacy-sensitive account/address fields. The project treats those differences as first-class adapter constraints rather than forcing every city into Edmonton's schema.

For Edmonton, one major challenge was parcel geometry. Edmonton transferred parcel-level GIS *boundary* data to AltaLIS in November 2021 — it's no longer freely available. The project resolved this without AltaLIS, GEODE, or FOIP:

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

**Live:** interactive 3D Edmonton map at **https://ecameracci.github.io/ca-city-tax-viz/**
— municipal tax revenue, assessed value, and modeled roads + fire cost per acre
by neighbourhood, with land-use set-aside, residential-only, Transportation,
Services, Ratio, Uses, Development, and Glass-grid lenses.

**Researched/scaffolded:** Vancouver, Calgary, Toronto, Hamilton, and Montréal are documented for future Canadian city adapters but remain disabled until real generated outputs exist and pass validation.

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

This is an independent civic project. If you work in urban planning, municipal finance, open data, or GIS in any Canadian city and want to collaborate — or if you have access to data that could help — get in touch.

For code contributions, see [`CONTRIBUTING.md`](CONTRIBUTING.md).
