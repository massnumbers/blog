# Proposal

## Why

The November 6 legislative-results post needs a reproducible visual foundation that follows up on the October 29 forecast. Building its structure and data displays now will let the author add narrative later against a consistent snapshot of unofficial results.

## What Changes

- Create `posts/2026-11-06-legislative-results/index.qmd` with metadata based on `_README.md`, section headings, executable R chunks, and no drafted narrative. Keep it a draft until the author completes it.
- Lead with a results overview table and municipality result maps for the four closest forecast races: 9th Norfolk, 8th Bristol, 9th Essex, and 3rd Barnstable.
- Add an other-notable-results section featuring 22nd Middlesex and Marc Lombardo's defeat, supported by a results table.
- Add a full table of the same 57 contested races as the pre-election post, showing unofficial results against the pinned forecast, reporting/call status, and outcome characterizations for party holds/flips and incumbent/open-seat outcomes.
- Pin local copies of the existing `ma-election-db` AP general-election results and forecast comparison, record provenance, and render working tables and interactive maps with the repository's current Quarto/R conventions.

## Capabilities

### New Capabilities

- `legislative-results-post`: An author-editable legislative-results post with reproducible results displays, municipality maps, forecast comparisons, and explicit unofficial/uncalled status.

### Modified Capabilities

None. The existing Blogger archive capability is unaffected.

## Impact

Implementation adds the post source and supporting data/provenance files under `posts/2026-11-06-legislative-results/`, plus generated Quarto output and freeze assets as required by repository conventions. It reads existing AP outputs from the sibling `ma-election-db` repository and reuses the October 29 forecast and local GIS assets; it does not modify that repository or refresh its feed. No new R package is expected. Narrative drafting, model retraining, certified-results replacement, and additional statewide charts/maps are outside scope.
