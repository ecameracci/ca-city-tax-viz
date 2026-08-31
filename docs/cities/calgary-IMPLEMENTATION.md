# Calgary implementation note

Branch: `city/calgary`

## Recommendation

Implement Calgary first among the new cities. It is the closest match to Edmonton for a revenue/value pipeline because open parcel assessment data includes assessed values, assessment classes, community codes/names, land size, and geometry.

## Core path

1. Use Community District Boundaries (`surr-xmvs`) as the neighbourhood analogue.
2. Use Current Year Property Assessments (Parcel) (`4bsw-nn7w`) for assessed value/class/community/land-size inputs.
3. Map Calgary assessment classes (`Residential`, `Non-Residential`, `Farm Land`) to canonical revenue cuts.
4. Pin or scrape official Calgary tax-rate/bylaw values with tests; no clean open-data tax-rate API was found.
5. Aggregate to community before publishing any web artifact.
6. Add Calgary-specific zoning classification from Land Use Districts (`qe6k-p9nh`) instead of reusing Edmonton zone-code rules.
7. Parse Calgary Transit GTFS ZIP (`npk7-z3bj`) rather than Edmonton’s separate Socrata GTFS tables.

## Required caveats before marking live

- Open assessment excludes titled parking stalls/storage, machinery/equipment, and linear property, so totals may not reconcile exactly to statutory tax denominators.
- Historical assessment (`4ur7-wsgc`) is 10M+ rows; use server-side Socrata aggregation.
- Off-street parking zones have lot polygons/names but no obvious stall capacity; do not invent capacity.
- Avoid publishing parcel-level roll numbers, addresses, or geometries.

## Primary source manifest

See `data/cities/calgary.json`.
