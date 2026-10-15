# Proposal

## Why

The `port-blogspot-archive` investigation (archived 2026-09-13) concluded that the
Blogger archive *can* be ported: Fusion Tables' shutdown cost far less than feared,
because 20 of the 40 Fusion Tables references were static screenshots that are already
recovered, and the converter grades all 95 posts clean or minor. Its recommendation
in `_sources/blogspot/FEASIBILITY.md` is to port the archive in two stages, at an
estimated 20-46 hours for the remaining 92 posts. Three pilot posts are live; the
other 92 still exist only on `massnumbers.blogspot.com`, outside the site's search
and history, and their images still depend on imgur except for the local copies
taken during the investigation.

## What Changes

- **Stage one: port the 81 remaining posts that need no map reconstruction** — 3
  prose-only, 64 image-only, and 14 whose maps survive as their own static
  screenshots (tier 2). Ported in three year batches, each rendered and verified
  before the next.
- **Stage two: port the 11 remaining map-judgment posts one at a time** — 4
  declared-missing, 4 tier-1 candidates with local data, 3 tier-1 candidates needing
  `electionstats.state.ma.us` downloads. Every tier-1 candidate is checked against
  the figures its own prose states before it is rebuilt; a failed check demotes it to
  declared-missing, as happened with the 2012-11-18 pilot.
- **Separate archive listing.** Ported posts carry a `blogger-archive` category and
  are listed on a new `archive.qmd` page linked from the navbar. The front page and
  its RSS feed stay limited to native posts, so 92 ported posts do not bury current
  work or flood feed subscribers. The three pilot posts move to the archive listing.
- **Intra-archive links point at the ported copies.** The 33 links (in 30 posts) from
  one Blogger post to another are rewritten to the ported post on this site. Link
  text and surrounding prose are unchanged; every other outbound link stays as
  written.
- **Editorial notes are marked as such.** Captions promising an interactive map that
  no longer exists (15 posts) and dead-embed placeholders (7 posts) are resolved with
  a visually distinct note, never by rewording the original prose.
- **Porting tooling is made repeatable.** `stage_pilot.py` hard-codes an expired
  scratchpad path and `verify_fidelity.py` hard-codes the three pilots; both become
  manifest-driven, and the manifest gains a per-post port status and site slug.
- **Completeness check.** The change ends with all 95 manifest posts ported, each
  verified for prose fidelity, local assets, no dead embeds, and a provenance link.

Non-goals: retiring or redirecting `massnumbers.blogspot.com` (provenance links
depend on it staying up, and Blogger cannot issue external per-post redirects);
restyling ported posts beyond the site theme; reconstructing maps whose data no
source covers (Suffolk poll crosstabs, Boston municipal results, the NOAA tornado
table).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `blogspot-archive-port`: adds requirements for the separate archive listing,
  intra-archive link rewriting, distinguishable editorial notes, a prose-agreement
  gate on reconstruction, site slugs and the archive category for ported posts, and
  archive completeness; modifies the post-convention and content-fidelity
  requirements accordingly; removes the investigation-only feasibility-recommendation
  requirement, which the archived change satisfied.

## Impact

- **Content**: 92 new `posts/YYYY-MM-DD-slug/` directories, each with `index.qmd`,
  an `images/` directory where the post has images, and `_sources/original.html`.
  The three pilot posts gain the archive category.
- **Repo size**: about 30 MB of images, from the 31.0 MB already downloaded to
  `_sources/blogspot/images/`.
- **Site**: new `archive.qmd` page and navbar entry; `index.qmd` listing excludes
  archive posts; search index and sitemap grow by 92 entries. Rendered output in
  `docs/` grows accordingly.
- **Build**: the 4-7 posts that end up with a reconstructed map add R code chunks and
  `_freeze/` entries under the existing Quarto / `renv` / `tmap` conventions. All
  other ported posts are plain markdown with no executable code.
- **Tooling**: `_sources/blogspot/` scripts (`convert_post.py`, `stage_pilot.py`,
  `verify_fidelity.py`) and `manifest.csv` / `fusion_tables.csv` gain port-status
  columns. Nothing under `_sources/` is published.
- **External**: `electionstats.state.ma.us` downloads for up to 3 stage-two posts.
  No new runtime dependency.
