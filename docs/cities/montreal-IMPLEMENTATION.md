# Montréal implementation note

Branch: `city/montreal`

## Recommendation

Implement Montréal through a separate city adapter. Montréal is a plausible revenue/value candidate, but it should **not** be presented as Edmonton-equivalent. The strongest path is to join published municipal tax-account line data to evaluation-unit geometry, then aggregate to a chosen neighbourhood geography before any browser export.

## Core path

1. Choose and freeze one neighbourhood analogue:
   - `quartiers-sociologiques`, or
   - `quartiers` / quartiers de référence en habitation.
2. Use `taxes-municipales` (`Imposition annuelle de taxes municipales`) as the first-pass revenue source.
3. Use `unites-evaluation-fonciere` to locate evaluation units and join tax rows by `ID_CUM` / evaluation-unit identifiers.
4. Explicitly filter/label tax lines. Montréal tax accounts include multiple components: general property tax, water, road/voirie, ARTM contribution, borough taxes, sector/property-type exceptions, and other charges.
5. Aggregate to quartiers before publishing. Do not ship raw `ID_CUM`, account numbers, matricules, civic addresses, or unit-level geometry.
6. Use `geobase` for road centreline equivalents, `pistes-cyclables` for cycling infrastructure, STM GTFS for transit, and municipal paid parking datasets only after separating on-street/off-street scope.

## Required caveats before marking live

- Montréal’s public tax data is a first-issuance tax-account-line dataset, not a simple Edmonton-style assessment-roll + mill-rate reconstruction.
- The catalogue notes that `taxes-municipales` is not exhaustive City revenue data and may omit later adjustments/exceptions.
- Québec role-foncier rules limit public consultation patterns; raw account/address/matricule data is sensitive even when open-data resources exist.
- Evaluation-unit geometries include condominium overlap and temporary 2m × 2m geometries for some modified matricules.
- Neighbourhood population for the selected quartiers may require Statistics Canada dissemination-area/block apportionment; older 2011 Montréal neighbourhood resources are not acceptable as current denominators.
- Municipal parking data includes paid on-street and off-street places/rules; do not describe it as city-managed parkade/surface-lot capacity unless that split and capacity can be defended.

## Primary source manifest

See `data/cities/montreal.json`.
