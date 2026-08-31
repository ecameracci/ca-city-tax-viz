# Multi-city source manifests

This directory records researched source candidates for city adapters. Edmonton is the live baseline. Vancouver, Calgary, Toronto, Hamilton, and Montréal have research-backed manifests, but their generated datasets are not shipped in the public deployment until a city-specific pipeline adapter is implemented and verified.

The web app reads `web/data/cities.json` for city-selector metadata. A city should not be marked `available: true` until its browser-facing data files are generated, validated, and documented.

## Implementation rule

Do not coerce other municipalities into Edmonton-specific semantics. Each city needs a source adapter that maps local field names, geography, tax rules, licensing, and privacy caveats into the app's canonical neighbourhood-level outputs.
