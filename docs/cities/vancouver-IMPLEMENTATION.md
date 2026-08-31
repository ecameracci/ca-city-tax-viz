# Vancouver implementation note

Branch: `city/vancouver`

## Recommendation

Implement Vancouver through a city adapter, using **Local Areas** as the neighbourhood analogue. Vancouver can support a revenue/value MVP, but the tax semantics are not Edmonton-equivalent.

## Core path

1. Download Local Area boundaries from City of Vancouver Open Data (`local-area-boundary`).
2. Download property parcel polygons (`property-parcel-polygons`) and property tax report rows (`property-tax-report`).
3. Join `property-tax-report.land_coordinate` to parcel `tax_coord`; spatially assign parcels to Local Areas.
4. Aggregate values and tax amounts to Local Area before any web export.
5. Label revenue carefully: `tax_levy` is the actual total notice amount, not a reconstructed municipal-only levy from City mill rates.
6. Use TransLink GTFS for transit service; City rapid-transit station/line layers are context only.

## Required caveats before marking live

- Local Areas are only 22 polygons, much coarser than Edmonton neighbourhoods.
- `tax_levy` includes non-City charges and should not be presented as Edmonton-style municipal levy.
- No clean city-managed off-street lot/parkade stall inventory was found; parking meters are a curbside fallback, not an Edmonton parking equivalent.
- Strip/avoid parcel-level folio, PID, address, legal-description, applicant, contractor, and postal-code fields in web artifacts.

## Primary source manifest

See `data/cities/vancouver.json`.
