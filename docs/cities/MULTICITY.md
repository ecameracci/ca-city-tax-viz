# Multi-city expansion audit

This project started as an Edmonton-specific pipeline and UI. Adding Vancouver, Calgary, Toronto, and Hamilton should use city adapters rather than pushing every municipality through Edmonton field names and tax semantics.

## Shared browser data contract

The current browser expects a neighbourhood-level GeoJSON plus optional sidecar files:

- `neighbourhood_value_per_acre.geojson` — required; neighbourhood features and canonical metric columns.
- `status.json` — optional; vintages, banners, mill-rate pod, budget context.
- `temporal.json` — optional; assessment-history panel.
- `roads.geojson`, `bike_routes.json`, `transit_stations.json`, `lrt_lines.json`, `fire_stations.json`, `parking_facilities.json`, `zoning.geojson`, `reference.geojson`, `value_grid.json`, `dev_grid.json`, `budget_ranked.json` — optional view/context layers.

`web/data/cities.json` now records available city metadata. A city must not be marked `available: true` until its required browser-facing outputs exist and have passed validation. Missing optional files should hide or degrade the relevant controls, not fail the whole app.

## Current hard Edmonton assumptions

- `scripts/download_data.py` is Edmonton Socrata-specific: domain, dataset IDs, filenames, row-count checks, and source comments are all Edmonton.
- `main.py` and many `src/load_*.py` modules expect Edmonton file names and columns such as `neighbourhood_name`, Edmonton mill-class fields, Edmonton zoning codes, and Edmonton GTFS table layout.
- Cost rates in `data/city_unit_costs.json` are Edmonton operating/service-cost estimates and must not be reused for other cities.
- UI copy, tooltips, caveats, title strings, and the Data & Methods pod mention Edmonton throughout. A multi-city production pass should move those strings behind city metadata or city-specific view copy.
- Browser default camera, reference geography, and optional sidecar data URLs were hardcoded to Edmonton. The selector scaffold introduces a city manifest indirection for these assets.

## City feasibility summary

| City | First defensible geography | Revenue/value feasibility | Key caveat |
|---|---|---|---|
| Edmonton | Neighbourhoods | Live baseline | Uses modeled municipal levy from open assessment roll and pinned mill rates. |
| Vancouver | Local Areas | Feasible, but not Edmonton-equivalent | `property-tax-report.tax_levy` is actual total notice amount, not municipal-only reconstructed levy. |
| Calgary | Community Districts | Strong | Open parcel assessment has values/classes/community/geometry; tax rates need official page/bylaw pinning. |
| Toronto | 158 neighbourhoods | Blocked from open data | No open parcel/account assessment roll with assessed values/classes; services/spatial branch first. |
| Hamilton | Planning neighbourhoods | Blocked from open data | Parcel polygons are open-ish but lack value/class/roll fields; services/spatial branch first. |

## Recommended implementation sequence

1. Keep Edmonton as the reference implementation and contract test.
2. Add a city-source config/adapters layer with explicit domain, source IDs, raw filenames, CRS, join keys, and canonical output columns.
3. Implement Calgary first for the closest Edmonton-like revenue/value workflow.
4. Implement Vancouver second with a clear revenue semantic label: actual property-tax levy / total notice amount unless municipal-only rates are reconstructed.
5. Implement Toronto and Hamilton as services/spatial/data-availability branches unless lawful aggregate assessment inputs are secured.
6. Make city-specific UI copy part of the manifest or generated status file before marking any non-Edmonton city live.

## Privacy rule

Parcel/account-level values, addresses, folios/roll numbers, applicants, contractors, or owner/tenant fields should never be shipped as raw web artifacts. City branches should aggregate to neighbourhood/community/local-area or privacy-safe grids before publishing.
