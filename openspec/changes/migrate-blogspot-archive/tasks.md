# Tasks

## 1. Archive listing

- [x] 1.1 Confirm under the installed Quarto that a listing `exclude` filter on `categories` matches a value inside a list, by rendering a throwaway two-post listing in the scratchpad; record the result in `design.md` and select the glob-based fallback if it does not match
- [x] 1.2 Add `categories: [blogger-archive]` to the three pilot posts and verify `grep -l blogger-archive posts/*/index.qmd` returns exactly those three
- [x] 1.3 Exclude the archive category from the `index.qmd` listing and add `archive.qmd` listing only that category, newest first, with no feed; add an "Archive" navbar entry in `_quarto.yml`; render `index.qmd`, `archive.qmd`, and the three pilots and verify the front page and `docs/index.xml` no longer contain the pilots, the archive page lists all three, and `docs/search.json` still contains them

## 2. Manifest-driven tooling

- [x] 2.1 Add `site_dir` and `port_status` columns to `_sources/blogspot/manifest.csv`, filling the three pilots as `verified` with their existing directories and the rest as `pending`; verify 95 rows, 3 verified, 92 pending
- [x] 2.2 Choose a short readable slug for each of the 92 pending posts and write it to `site_dir`; verify every value is unique, matches `YYYY-MM-DD-<kebab>` with the post's original date, has at most 6 slug words, and does not collide with an existing `posts/` directory; present the list to the author for review before staging
- [x] 2.3 Extend `convert_post.py` to emit the archive category, use `site_dir` for output directories, and rewrite intra-archive Blogger hrefs to `../<site_dir>/index.qmd` by matching `blogger_path`; verify on a scratch run that all 33 intra-archive links in 30 posts are rewritten or reported as non-post targets, and that `conversion_report.csv` still shows zero residual Fusion Tables URLs, HTML tags, and remote images
- [x] 2.4 Replace `stage_pilot.py` with a `stage_post.py` that takes the converter output directory as an argument, stages one or more manifest rows by `site_dir`, copies images and `_sources/original.html`, sets `image:` to the first local image when there is one, and marks rows `staged`; verify by re-staging one pilot into the scratchpad and diffing against the committed pilot directory, with only the category line differing
- [x] 2.5 Make `verify_fidelity.py` iterate manifest rows with a `site_dir`, strip every editorial callout before comparing, and add rendered-output checks for imgur, Blogger-hosted image, Fusion Tables, and `TODO-TIER` strings and for a link to the post's permalink; verify all three pilots pass at 1.0000 and that a deliberately edited copy of one pilot fails

## 3. Stage one, batch 2012-2013

- [x] 3.1 Convert and stage the 36 remaining 2012-2013 posts that are not stage-two posts, and verify `stage_post.py` reports no remote image and no Fusion Tables URL for any of them
- [x] 3.2 Resolve hand-correction flags in the batch (stale interactive captions as distinct notes after the original sentence, leftover `<pre>`/`<style>` remnants) and verify `grep -L` finds no flagged string left in the staged `.qmd` files; verify the relink pass pointed the 2013-01-03 pilot's link at the newly ported 2012-11-26 post (the 2012-11-18 pilot's target is a stage-two post and upgrades when that lands)
- [x] 3.3 Render the batch's `.qmd` files and verify each renders without error, appears on the archive page at its original date, is absent from the front page and feed, and passes `verify_fidelity.py`; read every post scoring below 1.0000 against its original and record the cause
- [x] 3.4 Mark the batch's manifest rows `verified` and commit the batch

## 4. Stage one, batch 2014

- [x] 4.1 Convert and stage the 30 remaining 2014 posts that are not stage-two posts, and verify no remote image or Fusion Tables URL is reported
- [x] 4.2 Resolve the batch's hand-correction flags and verify no flagged string remains
- [x] 4.3 Render the batch and verify render, archive listing, front-page exclusion, and `verify_fidelity.py` as in 3.3, including that links into the 2012-2013 batch now resolve without Quarto warnings
- [x] 4.4 Mark the batch's manifest rows `verified` and commit the batch

## 5. Stage one, batch 2015-2022

- [x] 5.1 Convert and stage the 15 remaining 2015-2022 posts that are not stage-two posts, and verify no remote image or Fusion Tables URL is reported
- [x] 5.2 Resolve the batch's hand-correction flags and verify no flagged string remains
- [x] 5.3 Render the batch and verify render, archive listing, front-page exclusion, and `verify_fidelity.py` as in 3.3
- [x] 5.4 Mark the batch's manifest rows `verified`, commit the batch, and verify the manifest shows 84 verified rows and 11 pending, all 11 being stage-two posts

## 6. Stage two, declared-missing posts

- [x] 6.1 Port 2013-04-04 and 2013-09-26, keeping their surviving static screenshots and replacing each lost embed with a declared-missing note describing what the original map showed; verify the post passes `verify_fidelity.py` and contains no `TODO-TIER`, then commit each post separately
- [x] 6.2 Port 2013-07-23 and 2014-06-03 with declared-missing notes, verify as in 6.1, and commit each post separately

## 7. Stage two, reconstruction candidates

- [ ] 7.1 For each of the 4 local-data candidates (2012-11-15, 2014-05-27, 2015-11-01, 2017-12-05), list every figure the prose states about the map, compute the same figures from the local data, and record the verdict and evidence in `fusion_tables.csv` `prose_agreement`; verify no tier-1 row for these posts still reads `UNTESTED`
- [ ] 7.2 For each of the 3 external-data candidates (2012-11-13, 2013-01-31, 2017-11-06), download the `electionstats.state.ma.us` CSV into the post's `_sources/`, run the same prose-agreement check, and record the verdict; verify no tier-1 row remains `UNTESTED`
- [ ] 7.3 Port each candidate that passed: build the map in an R chunk reading only local files, with `tmap_mode("view")` and the `tmap` object printed directly, add the reconstruction disclosure naming the data source, and verify the rendered page shows a working map and the post passes `verify_fidelity.py`; commit each post separately
- [ ] 7.4 Port each candidate that failed as a declared-missing post whose note states why it was not rebuilt, update its `fidelity_tier` in `fusion_tables.csv`, verify as in 6.1, and commit each post separately

## 8. Completion

- [ ] 8.1 Run a full `quarto render` and verify it completes, `git status docs/site_libs/` shows no deleted library a page references, and every rendered ported post passes `verify_fidelity.py` with zero intra-archive links still pointing at `massnumbers.blogspot.com` post URLs
- [ ] 8.2 Verify the manifest shows all 95 rows `verified` with existing `site_dir` directories, the archive page lists 95 posts, and the front page lists only native posts
- [ ] 8.3 Append a short "Outcome" section to `_sources/blogspot/FEASIBILITY.md` recording actual hours spent per stage against the estimate and the final tier counts after the prose-agreement checks, and verify each figure traces to the manifest or `fusion_tables.csv`
- [ ] 8.4 Update `CLAUDE.md` to describe the archive listing, the `blogger-archive` category, and the `_sources/blogspot/` porting scripts, and verify the documented commands run as written

## Workflow follow-up

- Archive the change after the author reviews the completed port.
- Decide separately whether to add a notice on the Blogger site pointing to the new archive page.
