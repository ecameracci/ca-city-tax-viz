# Toronto implementation note

Branch: `city/toronto`

## Recommendation

Implement Toronto as a services/spatial branch first. Do **not** enable revenue/value lenses until a lawful assessment-value source is secured.

## Core path

1. Use Toronto’s 158-neighbourhood model consistently.
2. Implement boundaries, Toronto Centreline, cycling network, TTC GTFS, Green P parking, zoning, and Neighbourhood Profiles population adapters.
3. Hide or disable money/revenue/value/temporal lenses in Toronto until assessed value and tax-class inputs are available.
4. If assessment data is obtained from MPAC/City/public roll access, strip personal fields and aggregate to neighbourhood × property class before export.

## Required caveats before marking live

- No Edmonton-equivalent open assessment roll was found.
- The official assessment roll is public-inspection/in-person and may contain owner/tenant data; do not scrape or republish it.
- 2021 Neighbourhood Profiles are wide XLSX workbooks and need an unpivoting loader.
- CKAN licence metadata may say `notspecified`; verify Toronto Open Government Licence before release.

## Primary source manifest

See `data/cities/toronto.json`.
