# Design

## Context

See `proposal.md` for motivation. The destination currently contains only `_README.md` and its editor backup. The October 29 post already implements `gt` tables, `tmap` 4 interactive maps, district links, and the four-race selection. Its model inputs are pinned as `forecast_14d_r2_*` files.

The sibling `ma-election-db/data/ap_results/general_2026/` contains three ready-to-use compressed CSVs: 200 race summaries, 544 municipality-candidate rows, and a 57-row forecast comparison. The observed snapshot is 2026-11-04 20:01 UTC. Its comparison file already uses the October 29 forecast, including 75% intervals and the candidate-pair margin definition. AP's municipality rows are district-specific; they are not precinct observations. The snapshot leaves 9th Norfolk uncalled and calls 8th Bristol despite incomplete reporting, so call status and reporting completeness must remain independent.

## Goals / Non-Goals

**Goals:** Keep computation local and auditable; share one prepared race dataset among all tables; make observed margins comparable to the published model; leave a clean source document for the author's narrative.

**Non-Goals:** Rebuild the forecast pipeline, add a generic election dashboard, import data into SQLite, refresh AP, decide publication timing, or generate additional editorial analysis. Only headings, factual data-display text, and metadata are authored.

## Decisions

### 1. Pin existing AP outputs inside the post

Copy `ma_general_2026_races.csv.gz`, `ma_general_2026_results.csv.gz`, and `ma_general_2026_forecast_comparison.csv.gz` into the new post directory without transforming the originals. Record upstream revision, file checksums, snapshot time, source paths, and the 14d-r2 model/2026-10-20 finance cutoff in an underscore-prefixed provenance file. Record that totals exclude blanks/write-ins and that results are unofficial. Read these local files with `readr` at render time.

Join the comparison cohort to race summaries on stable `(office, district_id)` keys, checking one-to-one coverage. Use `target_id` for forecast identity and AP race/candidate IDs for municipality selection. Compare the comparison-file forecast fields to the October 29 pinned files before relying on them. Keep source candidate IDs in their own namespaces; AP IDs and forecast IDs are not interchangeable. A refresh script is unnecessary for this one snapshot. Reading sibling paths during every render or fetching live data would make a clean checkout non-reproducible.

### 2. Create a draft with this visible structure

- `## Results of the four closest forecast races`: overview table, then `### 9th Norfolk`, `### 8th Bristol`, `### 9th Essex`, and `### 3rd Barnstable`, each containing a result map.
- `## Other notable results`: `### 22nd Middlesex`, followed by a compact race-results table using the same fields as the overview.
- `## Results for all contested seats`: one complete table containing the forecast cohort's 47 House and 10 Senate races.

Use the proposed metadata from `_README.md`, correcting "suprises" to "surprises", author Brent Benson, date 2026-11-06, and `draft: true`. Use hidden source comments if useful to mark narrative insertion points; do not add visible placeholder paragraphs. Captions, table notes, legends, status labels, and provenance labels are permitted because readers need them to interpret the displays. No new thumbnail generation is necessary during this scaffold change; a preview image can be chosen when the author prepares publication. Publishing now would expose an intentionally unfinished article.

### 3. Prepare results once and reuse them

Derive a validated display dataset from the 57 comparison rows plus prior-winner/incumbency fields from race summaries. Preserve all raw fields needed for checks. Compute candidate-pair margin as `100 * (dem_votes - comparison_votes) / (dem_votes + comparison_votes)` only for a positive denominator, and check it and its error against the upstream comparison fields. Display other-candidate votes separately when present. Positive margin/error means Democratic advantage/more Democratic than forecast; label all differences as percentage points. Do not substitute all-candidate shares for the pair margin. Keep full numeric precision until formatting.

Reuse `gt`, `gtExtras`, and formatting conventions from the earlier post. The four-race/notable tables show candidates with incumbency indicators, votes, observed margin, model margin, AP call/leader, and reporting completeness. The full table additionally shows chamber, district link, 75% model range, signed error, and outcome. Use grouped columns and wide layout to make comparison readable; the 75% interval can remain a compact text range to avoid an unnecessary custom plotting dependency. Sort the full table by increasing absolute forecast margin, with stable chamber/district tie breakers. The featured table and maps retain the October 29 order, not the result ranking.

### 4. Characterize outcome on two independent axes

Derive these fields from AP calls, prior seat winner, and whether the incumbent ran; do not infer the prior party solely from `incumbent_status`, which cannot distinguish open-seat holds from flips.

| Case | Party result | Candidate result |
| --- | --- | --- |
| Called; winner is incumbent | `<party> hold` | `Incumbent re-elected` |
| Called; incumbent loses | `<party> hold` or `<prior> to <winner> flip` | `Incumbent defeated` |
| Called; no incumbent running | `<party> hold` or `<prior> to <winner> flip` | `Open-seat win` |
| Uncalled | `Pending` | `Pending` |

Display the two fields together under a grouped outcome heading or as a combined label. Normalize Democratic/Republican abbreviations and equivalent Independent/Unenrolled labels for the same person before party comparisons; preserve named minor-party distinctions and use unknown rather than guessing when the upstream party is ambiguous. Missing prior party yields an explicit unknown party result, without losing a known incumbent/open-seat outcome. For called races with a running incumbent, compare candidate identity using available source IDs with an explicit verified-name fallback for unmatched candidates. The current snapshot must classify 22nd Middlesex as an R-to-D flip/incumbent defeat, 8th Bristol as D-to-R/incumbent defeat, and 9th Essex as an R hold/incumbent re-election. The classifier must also handle open-seat holds and flips among the cohort. Uncalled rows use "Leading" and "Provisional" labels and never acquire a winner or scored correctness merely from a vote lead.

### 5. Build municipality result maps from AP votes and district-clipped geometry

Reuse `_gis/ma_wards_precincts_w_subs.geojson`: filter `State_Rep` to the district, dissolve precinct polygons by `city_town`, and simplify after validating geometry. Normalize district/municipality join keys explicitly, check coverage in both directions, and retain unmatched geometry with unavailable styling rather than losing it through an inner join. Do not use whole-town geometry for split municipalities. The predecessor's presidential/PVI CSV is not the results source.

Aggregate AP candidate rows within each race-municipality, selecting the Democrat and comparison candidate by verified identity; assert totals agree with the race-level candidate votes. Compute pair margins with the same denominator as the tables. Attach municipality reporting fields once per municipality, not summed across candidate rows. Use red-white-blue fill, zero midpoint, a common symmetric scale across all four maps (for example -100 to +100 points), and explicit unavailable styling. Labels/popups identify the margin's party direction, candidates/votes, other votes if any, and municipality reporting status. District-level AP call status belongs in the map caption and must not appear as a municipality winner declaration: upstream `is_race_winner` is district-wide.

Set `tmap_mode("view")`, print each `tmap` object directly, and use existing map/layout conventions. This reuses installed dependencies and preserves functioning widgets under tmap 4.2; `tmap_leaflet()` is incompatible with the repository's documented workflow.

### 6. Verify data assertions and actual rendered widgets

Use focused assertions in data preparation for cohort membership/uniqueness, forecast agreement, featured IDs, join coverage, candidate vote reconciliation, margin/error arithmetic, and called-versus-uncalled outcomes. Verify representative hold, flip, incumbent defeat, and open-seat cases plus zero/missing denominators. Check percentage units explicitly: `precincts_reporting_pct` is on a 0-100 scale while candidate shares are fractions. These checks guard substantive data errors; a separate broad testing framework is unnecessary.

Execute a single-post render under Quarto 1.9+ and the restored R environment, then inspect tables at desktop and narrow viewport widths and exercise each map's popups/zoom. If project rendering excludes drafts, use a local preview that renders drafts without changing source publication status. Check that headings appear with empty narrative space and no generated analytical paragraphs. Follow with a normal site render to verify integration and assets; inspect generated listings to ensure the draft is excluded. Commit applicable `_freeze/` cache files, any newly required `_freeze/site_libs/` libraries, and generated `docs/` changes produced by Quarto. Never hand-edit generated HTML.

## Risks / Trade-offs

- Unofficial counts and calls can change: pin and label the snapshot; any later refresh is an explicit data update.
- Pair-only margins differ from all-candidate percentages: retain other votes and explain the denominator in a concise table/map note.
- Municipality names and district spellings may vary: normalize only explicit known equivalents and fail on unexplained missing AP geography matches.
- A wide results table may overflow: use grouped columns, existing screen layout, and horizontal overflow where needed; validate narrow screens as well as desktop.
- Open-seat party transitions and Independent/Unenrolled aliases can be misclassified: use prior-winner data and verified candidate identity instead of party-label inequality alone.
- Global freeze settings can hide execution problems: force the initial post execution, inspect its cache/dependencies, and then check cached site rendering.

## Migration Plan

Add the draft post and pinned inputs, execute and inspect it, and retain normal generated caches/assets. No schema migration or upstream repository change is required. The author later adds narrative and deliberately changes draft status for publication. Rollback removes the added source/data/cache files and regenerates site output with Quarto.
