## 1. Capture the archive before it degrades

- [x] 1.1 Fetch the full Blogger Atom feed to `_sources/blogspot/feed.json` and verify the saved file reports `totalResults: 95` with 95 entries, each carrying non-empty body content
- [x] 1.2 Build `_sources/blogspot/manifest.csv` with one row per post (date, title, labels, permalink, slug) and verify the row count is 95 and dates span 2012-11-13 to 2022-08-21
- [x] 1.3 Extract every external `src`/`href` from the post bodies into `_sources/blogspot/resources.csv`, classified as image / fusion-table / google-sheet / other-embed / outbound-link, and verify the fusion-table rows resolve to 40 unique embed URLs across 27 posts and the image rows to 256 unique imgur URLs
- [x] 1.4 Record an HTTP status and check date for every resource row and verify no resource is left unchecked; flag any imgur URL that no longer returns a real image so recovery gaps are known now rather than later
- [x] 1.5 Download all live imgur images into `_sources/blogspot/images/<imgur-id>.png`, verify each file is a valid image matching the byte size seen during the check, and report the total size added

## 2. Establish what is recoverable

- [x] 2.1 Author checks Google Drive and Google Takeout for a Fusion Tables archive from the 2019 shutdown; record per table ID in `_sources/blogspot/fusion_tables.csv` whether data was found, and treat a definitive "not found" as a completed task
- [x] 2.2 Parse the table ID, geometry column, and map center/zoom out of each of the 40 embed URLs into the same file, and verify every embed is attributed to its post and has a recorded recovery status
- [x] 2.3 Search `_data/`, `_gis/`, and the `mapoli` repo for data matching each map's subject and era, and record per table whether an equivalent dataset exists locally; verify the finding that `mapoli/results/` begins at 2016 and therefore does not cover the 2013-2014 maps
- [x] 2.4 For tables with no local equivalent, check whether `electionstats.state.ma.us` publishes the underlying precinct or municipal results for that contest, and record source URL and granularity per table
- [x] 2.5 Pull Wayback snapshots for a sample of at least 5 map posts and verify directly whether any snapshot contains a rendered map image; record the verdict, since tier 2 depends on it
- [x] 2.6 Assign a provisional fidelity tier (reconstructed / static / declared-missing) to each of the 40 embeds from the findings above, and verify every embed has a tier and a one-line justification

## 3. Convert Blogger HTML to Quarto

- [x] 3.1 Write a conversion script that turns one post's Blogger body HTML into Quarto markdown with front matter, rewriting imgur references to local paths, and verify it runs over all 95 posts without error
- [x] 3.2 Run the script across the archive into a scratch directory and verify the output by measuring how much hand correction each post needs: report counts of posts with clean output, minor artifacts, and heavy `<div>`/inline-style damage
- [x] 3.3 Verify the converter drops or flags every `fusiontables.google.com` and `fusiontables.googleusercontent.com` URL rather than carrying a dead embed into the output

## 4. Pilot port of three representative posts

- [x] 4.1 Select the three pilot posts — one prose-only, one image-heavy, one Fusion Tables map post — and record why each represents its class
- [x] 4.2 Port the prose-only post to `posts/YYYY-MM-DD-slug/index.qmd` with original date, title, author, description, and the provenance link to its Blogger permalink; verify `quarto render` on that file succeeds and the post appears in the listing at its original date
- [x] 4.3 Port the image-heavy post with all images localized under its post directory, verify the rendered HTML references no `i.imgur.com` URL, and record the directory size it adds
- [x] 4.4 Port the map post, applying the tier chosen in 2.6; if reconstructed, build the map with `tmap_mode("view")` printing the `tmap` object directly per the project convention, and verify the rendered page shows a working map
- [x] 4.5 For the map post, verify that the ported prose and the map agree: any figure cited in the text that a reconstruction cannot reproduce drops the map to the declared-missing tier
- [x] 4.6 Read each pilot post against its Blogger original and verify the prose is unchanged apart from formatting, with no added, removed, or reworded claims
- [x] 4.7 Record the actual working time spent on each pilot post, broken out by conversion, image handling, and map handling

## 5. Recommendation

- [x] 5.1 Extrapolate full-port cost from the pilot times and the tier mix across all 95 posts, and verify the estimate is expressed as a range per tier rather than a single average
- [x] 5.2 Assess the listing impact with the three pilot posts live, and note whether 116 posts would need a separate archive listing
- [x] 5.3 Write `_sources/blogspot/FEASIBILITY.md` recommending full port, defined subset, or no port, citing measured per-post effort, tier counts, and what was recovered versus lost; verify every claim traces to a manifest column or a recorded pilot measurement
- [x] 5.4 Present the recommendation and the three live pilot posts to the author for a go/no-go on the remaining 92 posts, which belong to a follow-up change
