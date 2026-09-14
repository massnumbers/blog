## Why

The Mass. Numbers blog ran on Blogger from November 2012 until August 2022, when it
moved to this Quarto site. Those 95 posts — covering the 2013 Markey/Gomez Senate
special, the 2014 governor's race, and a decade of MA legislative analysis — are the
blog's entire early history and are still only available on `massnumbers.blogspot.com`,
outside the site's search, listings, and social metadata.

Porting them is not obviously feasible. Most of the maps were Google Fusion Tables
embeds, and Fusion Tables was shut down on 3 December 2019: those embeds now redirect
to a Google help FAQ and render nothing. Before committing to a 95-post migration, we
need to establish what can actually be recovered and at what cost per post.

## What Changes

This change is an investigation with a small proof-of-concept port, not the full
migration. It will:

- **Inventory the archive** — extract all 95 posts from the Blogger Atom feed into a
  machine-readable manifest (date, title, labels, permalink, body HTML) and classify
  each by what it depends on: static images, Fusion Tables embeds, Google Sheets links,
  or prose only.
- **Audit external dependencies for liveness**, so the manifest records what is
  recoverable versus permanently lost. Baseline already measured while drafting this
  proposal:
  - 256 unique `i.imgur.com` images referenced across 91 posts; all 256 return HTTP 200
    today, but they are a single-host dependency with no local copy.
  - 40 unique Fusion Tables embed URLs across 27 posts; all dead. The URLs do preserve
    the table ID, the selected geometry column, and the map center/zoom.
  - 17 Google Sheets links across 11 posts; sampled sheets still resolve publicly.
- **Determine whether the Fusion Tables data is recoverable** — check for a Fusion
  Tables archive in the author's Google Drive (Google's 2019 export), for the source
  CSVs in `_data/`, and for equivalent data in the `mapoli` repo (`results/`, `pvi/`,
  `districts/`, `gis/`).
- **Define and evaluate fidelity tiers** for handling dead embeds, from full
  reconstruction as a `tmap`/Leaflet map down to a static note that the original
  interactive map is unavailable.
- **Port 3 representative posts** end to end as a proof of concept — one prose-only,
  one image-heavy, one Fusion Tables map post — and measure the actual effort per post.
- **Produce a recommendation** on whether to port all 95, a subset, or none, with a
  per-post cost estimate grounded in the pilot.

Non-goals: porting the remaining 92 posts, retiring the Blogger site, and setting up
redirects from `blogspot.com` permalinks. Those depend on the recommendation and belong
in a follow-up change.

## Capabilities

### New Capabilities
- `blogspot-archive-port`: How legacy Blogger posts are represented on the Quarto site —
  the archive manifest, source fidelity and dating rules, asset localization, the
  fidelity tiers for embeds whose backing service is gone, and provenance/attribution
  on every ported post.

### Modified Capabilities

None. `openspec/specs/` is currently empty; this is the project's first capability.

## Impact

- **New**: `posts/YYYY-MM-DD-slug/` directories for the 3 pilot posts, following the
  existing post convention; `_sources/blogspot/` at the repo root for the cross-post
  archive manifest and the fetched feed, with each pilot post's original HTML under its
  own `posts/<slug>/_sources/` per the project's convention. Quarto ignores
  `_`-prefixed directories, so none of it is published.
- **Assets**: localized copies of referenced imgur images under each ported post's
  directory, adding roughly 30–40 MB to the repo if all 256 are eventually pulled in
  (the pilot will measure the real per-post figure).
- **Site**: ported posts appear in the `index.qmd` listing interleaved with current
  posts by date; the listing grows from 21 posts to 24 in the pilot, and would reach
  116 under a full port. Whether that is desirable for the front page is one of the
  questions this investigation answers.
- **Build**: any reconstructed map re-executes under the existing Quarto 1.9 / `renv`
  toolchain and the `tmap` conventions in `CLAUDE.md`; adds `_freeze/` entries.
- **External dependencies**: Blogger Atom feed (read-once), imgur (read-once during
  localization), Google Drive (manual check for a Fusion Tables archive). No new runtime
  dependency on any of them.
