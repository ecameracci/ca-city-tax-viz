# Hamilton implementation note

Branch: `city/hamilton`

## Recommendation

Implement Hamilton as a services/spatial branch first. Do **not** enable revenue/value lenses until a lawful aggregate assessment source is secured.

## Core path

1. Use Hamilton planning neighbourhoods as the analysis geography.
2. Implement ArcGIS FeatureServer paging for neighbourhoods, street centrelines, bikeways, HSR stops/service, zoning, and parking/context layers.
3. Treat former municipality/community boundaries and fire/transit area-rating geographies as tax-area support if revenue becomes possible.
4. Hide or disable money/revenue/value/temporal lenses until assessment values and property classes are available.

## Required caveats before marking live

- The Hamilton assessment parcel layer found in research has geometry/shape fields only, not assessed value, class, address, roll/account, or neighbourhood fields.
- Tax rates vary by former municipality/community plus area-rated fire/transit classes; a simple Edmonton-like mill-rate table will be wrong.
- Do not scrape individual tax calculators or address/roll lookup flows.
- Verify exact zoning and population FeatureServer items before implementation; research found stronger ward-level than neighbourhood-level population coverage.

## Primary source manifest

See `data/cities/hamilton.json`.
