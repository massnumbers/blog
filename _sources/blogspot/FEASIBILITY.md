# Porting the Blogger archive: feasibility findings

Investigation for the `port-blogspot-archive` change. Every figure below traces
to a column in this directory's CSVs or to a measurement recorded during the
pilot ports; the source is named on each claim.

## Recommendation

**Port the archive, in two stages.**

Stage one is the 83 posts that need no map reconstruction: 4 prose-only, 65
image-only, and 14 whose maps were published as static screenshots that are
already recovered. Estimated 12-26 hours (`pilot_effort.csv` rates applied to
the class counts in `conversion_report.csv`).

Stage two is the 12 posts whose maps need judgment: 5 declared-missing, 4
reconstructable from local data, 3 needing external data. Estimated 9-21 hours,
and it should be decided per post rather than committed to in advance, for the
reason task 4.5 uncovered.

This is not the answer the change expected. The premise was that Fusion Tables'
shutdown might make the archive unportable. It does not, because most of these
maps were never live embeds on the page.

## What the archive actually contains

Measured from `manifest.csv` and `resources.csv`, checked 2026-09-13:

| | count |
|---|---|
| Posts on the Blogger site | 95 (2012-11-13 to 2022-08-21) |
| Distinct external resources referenced | 621 |
| Image references | 292, of which 256 unique imgur and 25 Blogger-hosted |
| Fusion Tables references | 40 rows, 39 unique URLs, 32 distinct tables, 26 posts |
| Google Sheets links | 17 across 11 posts, all still resolving |
| Outbound citation links | 271, of which 88 are dead or erroring |

## The finding that changes the answer

The 40 Fusion Tables references are not 40 dead maps. Parsed in task 2.2 and
confirmed in 3.1, they break down as:

- **20 references (16 posts)** were a static screenshot wrapped in a link to the
  interactive version. The screenshot is the map as the original reader saw it,
  and all of them were downloaded in task 1.5. Nothing is lost but interactivity.
- **9 references (6 posts)** were text links to the table itself, not maps.
- **6 references (6 posts)** were true `<iframe>` embeds, where the frame is all
  there ever was on the page and nothing visual survives.
- **5 references (3 posts)** were text links to a map with no accompanying
  screenshot.

So the visual content of most map posts already survives. `wayback_check.csv`
confirms Wayback is no help here -- 6 posts sampled, all with snapshots, none
with a rendered map -- but it is not needed.

## Recovery status

`fusion_tables.csv`, one row per reference:

| tier | rows | posts |
|---|---|---|
| 2 - static, from the post's own screenshot | 20 | 16 |
| 3 - declared missing | 11 | 8 |
| 1 - reconstructed from local data | 5 | 4 |
| 1 - reconstructed, needs external data | 4 | 3 |

The original tables are gone: the author confirmed on 2026-09-13 that no Fusion
Tables archive exists in Google Drive and no Takeout export was made before the
2019-12-03 shutdown (task 2.1, recorded for all 32 tables).

Local data covers more than the proposal assumed. `_gis/house2012/` and
`_gis/senate2012/` hold exact-era district geometry, `_data/2023/ma_pres_results_*.csv`
holds municipal presidential results back to 1972, and
`mapoli/pvi/ma_precincts_districts_12_16_pres.csv` holds 2,174 precincts of 2012
Obama/Romney. For the remainder, `electionstats.state.ma.us` serves municipal and
precinct CSVs; the 2012 Senate general and 2013 Senate special were both confirmed
downloadable. What no source covers: Suffolk University poll crosstabs, Boston
municipal election results, and one NOAA tornado dataset.

## The caution on reconstruction

The map pilot was chosen as the expensive case and it failed, usefully.

The 2012-11-18 House district ranking looked like a clean tier 1: exact-era
geometry and a district PVI table both sit in the repo. Rebuilding it from that
data contradicts the post's own prose. The post ranks districts by averaging
Democratic-Republican margins across the 2006-2012 Governor, Senate, and
Presidential races; the available data is a presidential-based PVI, a different
measure. Measured 2026-09-13:

| the post states | local data gives |
|---|---|
| 2nd Hampden: 4.00% Republican lean | D+5 (+4.60) |
| 12th Bristol: 10.89% Republican lean | D+8 (+8.46) |
| most Democratic: 25th Middlesex | 26th Middlesex |
| most Republican: 9th Norfolk | 12th Plymouth |

It also covers 53 of 160 districts. The map was demoted to tier 3 and the post
now describes what the map showed and says plainly why it was not rebuilt.

The general lesson: matching *data class* is not the same as matching the
*method* a post used. The 9 remaining tier-1 rows are flagged `UNTESTED` in
`fusion_tables.csv` and each needs this same check before anyone rebuilds it.
A failed check is cheap -- it costs the test -- but it means tier 1 counts are
an upper bound on what will actually be reconstructed.

**Update, 2026-10-15 (migrate-blogspot-archive).** The investigation missed a
better source: the Google Sheets the posts link to still export as CSV, and they
hold the author's own tables. The 2012-11-18 pilot's sheet reproduces every
figure above (2nd Hampden from +4.22 to -4.00, 12th Bristol from +17.22 to
-10.89, the 25th Middlesex and 9th Norfolk as the extremes, all 160 districts),
so its map was rebuilt after all. The lesson stands in sharper form: the post's
own data, where it survives, comes before any re-sourced equivalent. Outcome of
the tier-1 checks is in `fusion_tables.csv` and summarized under Outcome below.

## Conversion quality

`convert_post.py` run across all 95 posts, graded in `conversion_report.csv`:

| grade | posts |
|---|---|
| clean, no hand correction needed | 67 |
| minor, one or two edits | 28 |
| heavy | 0 |

The 28 minor cases are: 15 posts with a caption promising an interactive map
that no longer exists, 7 with a tier marker to resolve, and 6 with a `<pre>` or
`<style>` remnant. No post requires substantial rework. The `<div>` soup the
design anticipated did not materialize; the one real hazard found was HTML data
tables, which now convert to markdown tables rather than running their cells
together.

## Measured pilot effort

`pilot_effort.csv`, actual working time:

| post | class | total |
|---|---|---|
| 2013-01-03 Senate candidate qualifications | prose-only | 8 min |
| 2014-08-12 Governor polling averages | image-only (10 images) | 11 min |
| 2012-11-18 House district partisan ranking | map, tier 3 | 46 min |

Of the 46 minutes on the map post, 34 were the reconstruction attempt and its
disproof. Scripted conversion averaged 2 minutes per post; reading each post
against its Blogger original averaged 6.

All three render clean under Quarto 1.10.18, appear in the listing at their
original dates, carry a provenance link, and serve every image locally. No
rendered page contains a Fusion Tables URL or an imgur reference.

## Cost of the full port

Class counts across all 95 posts, with per-post ranges anchored on the pilots:

| class | posts | per post | subtotal |
|---|---|---|---|
| prose-only | 4 | 6-12 min | 0.4-0.8 h |
| image-only | 65 | 8-18 min | 8.7-19.5 h |
| map, tier 2 static | 14 | 12-25 min | 2.8-5.8 h |
| map, tier 3 declared missing | 5 | 25-50 min | 2.1-4.2 h |
| map, tier 1 local | 4 | 45-120 min | 3.0-8.0 h |
| map, tier 1 external | 3 | 75-180 min | 3.8-9.0 h |

**Full port: 21-47 hours. Remaining 92 posts: 20-46 hours. Stage one alone
(83 posts): 12-26 hours.**

Ranges rather than point estimates: the pilot measured one post per class, and
the tier-1 classes were not measured at all -- the one tier-1 candidate tried
became a tier-3 post.

## Listing impact

The front page now lists 23 posts with the 3 pilots live. A full port takes it
to 115. The listing is a single undifferentiated reverse-chronological run with
a thumbnail per post, so 115 entries would bury the current work under a decade
of archive.

This does not block the port, but it should be settled before stage one lands.
The options are a separate archive listing page, a year filter on the existing
listing, or a category tag on ported posts. That decision was left open in
`design.md` and the evidence now says it needs making.

## Repository cost

31.0 MB for all 281 images, already downloaded and verified. Per ported post the
measured figures were 32 KB (no images), 792 KB (10 images), and 292 KB (3
images). A full port adds roughly 31 MB, matching the proposal's 30-40 MB estimate.

## What would change this recommendation

- If the 9 `UNTESTED` tier-1 rows mostly fail their prose-agreement check, the 7
  reconstruction posts move to tier 3 and the full port gets *cheaper*, not more
  expensive -- but 7 posts would carry a note where a map used to be.
- If imgur purges these images, the tier-2 posts lose their maps entirely. The
  local copies in `images/` are the hedge, and they are already taken.
