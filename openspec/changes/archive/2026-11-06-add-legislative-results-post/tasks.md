# Tasks

## 1. Pin and validate source inputs

- [x] 1.1 Copy the three existing `ma_general_2026_{races,results,forecast_comparison}.csv.gz` outputs from `ma-election-db/data/ap_results/general_2026/` into the post directory; verify checksums against the source files and confirm the copied files have 200 race, 544 municipality-candidate, and 57 comparison rows for the planned snapshot.
- [x] 1.2 Add an underscore-prefixed provenance file recording source revision/paths/checksums, AP snapshot time, unofficial status, named-candidate-only totals, and 14d-r2 forecast/2026-10-20 finance cutoff; verify the comparison's target IDs, point margins, and 75% bounds agree with the October 29 pinned forecast files.

## 2. Create the scaffold and shared display data

- [x] 2.1 Create `posts/2026-11-06-legislative-results/index.qmd` with the planned metadata, `draft: true`, hidden setup/data chunks, and ordered section/subsection headings; verify the title typo is corrected and the body contains no narrative paragraphs or visible text placeholders.
- [x] 2.2 Load pinned local inputs and prepare the 57-race display dataset with one-to-one race-summary joins, candidate/party labels, district links, vote totals/other votes, AP winner or leader, and reporting fields; verify exact cohort membership, 47 House/10 Senate counts, no duplicate keys, and percentage units.
- [x] 2.3 Compute/check candidate-pair margins, 75% forecast ranges, and signed errors; verify the formula against upstream comparison values, positive-error direction, and missing/zero-denominator handling, and include concise denominator/source/snapshot notes for displays.
- [x] 2.4 Implement party hold/flip and incumbent re-elected/defeated/open-seat outcome labels with explicit pending and unknown cases; verify the pinned 22nd Middlesex, 8th Bristol, 9th Essex, and uncalled 9th Norfolk cases, plus representative open-seat hold/flip behavior and equivalent Independent/Unenrolled identity handling.

## 3. Build the results tables

- [x] 3.1 Add a `gt` overview table for 9th Norfolk, 8th Bristol, 9th Essex, and 3rd Barnstable in that order, with candidates/parties, votes, observed/model margins, AP call/leader, and reporting completeness; render and compare all four rows to the pinned inputs.
- [x] 3.2 Add the 22nd Middlesex results display under other notable results, identifying Lombardo and his opponent, result, forecast, and incumbent defeat/party flip; render and verify every displayed value against the same shared dataset without adding narrative.
- [x] 3.3 Add the full 57-race table with grouped result/forecast/outcome columns, candidate and other votes, 75% ranges, signed margin error, district links, and pending labels; verify each race appears exactly once and inspect both desktop and narrow-screen readability.

## 4. Build and verify municipality result maps

- [x] 4.1 Prepare district-municipality AP totals and district-clipped/dissolved geometry from the existing precinct GeoJSON; verify candidate identity matching, race-level vote reconciliation, join coverage, split-municipality boundaries, and reporting fields without double-counting candidate rows.
- [x] 4.2 Add one interactive `tmap` result map under each featured district heading, using a common symmetric margin scale, visible legend, labels/popups, unavailable styling, and district-call/source captions; execute with `tmap_mode("view")` and direct object printing, then inspect all four maps and exercise popups/zoom, including missing/zero-vote behavior.

## 5. Verify integration and generated assets

- [x] 5.1 Force a post execution with Quarto 1.9+ and the repository R environment, using local draft preview where necessary; verify all data assertions pass, tables/maps render correctly together, and only headings and factual display text appear in the narrative space.
- [x] 5.2 Run a normal site render, inspect the resulting diff and local widget references, and retain required generated `_freeze/`, `_freeze/site_libs/`, and `docs/` assets; verify cached rendering preserves all widgets, the post remains a draft and excluded from published listings, and no unrelated source or upstream repository changes were made.
