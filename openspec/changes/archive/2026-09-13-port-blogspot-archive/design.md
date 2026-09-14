## Context

See `proposal.md` — Why. Constraints that shape the approach:

- **The Blogger feed is a complete, usable source.** `https://massnumbers.blogspot.com/feeds/posts/default?max-results=500&alt=json` returns all 95 entries with full body HTML (`totalResults: 95`, range 2012-11-13 to 2022-08-21). No scraping or Blogger login is needed to get the text. A Blogger XML export would be a fallback if the feed ever truncates.
- **The old and new blogs are contiguous.** The last Blogger post (2022-08-21) and this site's `posts/welcome/` share a date, so the archive extends the timeline backward cleanly with no overlap to reconcile.
- **Fusion Tables is unrecoverable from the web.** All 40 embed URLs across 27 posts now redirect to a Google help FAQ. The URLs retain the table ID, the selected geometry column (`col11`, `col28`, ...), and the map's lat/lng/zoom — enough to know what each map framed, not enough to get its data back.
- **Images are alive but unowned.** All 256 unique `i.imgur.com` URLs returned HTTP 200 when checked on 2026-09-13. That is the recovery window, not a guarantee; imgur has purged old anonymous uploads before.
- **Local data covers more of the era than first assumed** (corrected during task 2.3). `mapoli/results/` does start at 2016, but it is not the only local source: `_gis/house2012/` and `_gis/senate2012/` hold exact-era district geometry, `_data/2023/ma_pres_results_*.csv` holds municipal presidential results back to 1972, and `mapoli/pvi/ma_precincts_districts_12_16_pres.csv` holds 2,174 precincts of Obama/Romney 2012. Of the 32 tables behind the maps, 16 have both geometry and attributes available locally. The gap is concentrated in non-presidential races (2012 Warren/Brown, the 2013 Markey special), municipal Boston elections, and poll crosstabs.
- **electionstats.state.ma.us closes most of the remaining gap.** Its `/elections/download/<id>/precincts_include:0|1/` endpoints return municipal and precinct CSVs; the 2012 US Senate general and the 2013 Senate special were both confirmed downloadable. Boston municipal elections and Suffolk University poll crosstabs are not covered by it.
- **The build toolchain is fixed**: Quarto 1.9, `renv`, and the `CLAUDE.md` conventions — print the `tmap` object directly under `tmap_mode("view")`, `seed=1234` on any `stan_glm()`.

## Goals / Non-Goals

**Goals:**

- Answer "can these posts be ported, and at what cost per post" with measured evidence rather than an estimate.
- Capture the archive's text and images now, while both are still retrievable, regardless of what the recommendation turns out to be.
- Establish the reusable rules — fidelity tiers, provenance, asset localization — that a later full port would follow.

**Non-Goals:**

- Building a general-purpose Blogger-to-Quarto converter. The pilot tooling only has to work on these 95 posts.
- Perfect visual fidelity to the Blogger theme. Ported posts should look like Mass. Numbers posts.
- Reconstructing every Fusion Tables map. Tier 3 (declared missing) is an acceptable outcome for a post.

## Decisions

**Capture the archive before deciding whether to port it.** The inventory and the image
pull run first and unconditionally, because the imgur dependency is the one part of this
that can disappear while we deliberate. A `_sources/blogspot/` snapshot plus localized
images is worth having even if the recommendation is "do not port."
*Alternative considered:* decide first, capture second. Rejected — it gambles the only
copy of 256 images on the timing of a decision we have not made.

**Atom feed as the source of record, Wayback as a supplement.** The feed gives clean
post HTML for all 95 posts in one request. Wayback has 78 archived post-permalink URLs,
so it is a useful cross-check for anything the feed mangles, and the only possible source
for a screenshot of a rendered map.
*Alternative considered:* Wayback as primary. Rejected — coverage is partial and
snapshot HTML carries the Blogger template's wrapper markup.

**Fidelity tiers, chosen per map rather than per post.** A post can carry a reconstructed
map and a declared-missing one. Assigning a tier per embed keeps the choice honest and
keeps the manifest a useful cost model: the tier mix across 27 posts is what makes a
full-port estimate credible.
*Alternative considered:* one rule for all dead embeds. Rejected — the cost difference
between reconstruction and a note is roughly an order of magnitude, so a single rule
either overstates or understates the whole project.

**Pilot selection spans the cost range, not the highlights.** One prose-only post, one
image-heavy post, one Fusion Tables map post — deliberately including the expensive case
rather than three easy ones, because the map posts are the reason this is a question.

**Reconstruction discloses itself.** A rebuilt map is a 2026 artifact made from re-sourced
data, not the 2013 original. The post says so inline. This is a content decision, not a
technical one: a reader who cannot tell an original from a reconstruction cannot judge
either.

**HTML-to-markdown conversion is scripted, then hand-corrected.** Blogger bodies carry
inline styles, `<div>` soup, and imgur `<a><img></a>` pairs. A script gets the bulk;
each pilot post is then read against its original. The measured hand-correction time per
post is one of the numbers the recommendation reports.

**Ported posts are not backdated into `docs/`.** They render through the normal pipeline.
Per the project's build notes, a single-post render rebuilds `search.json`, `index.html`,
and the sitemap correctly, so pilot posts can be added without a risky full-site render.

## Risks / Trade-offs

- **Imgur purges the images before we pull them** → The inventory and image download are
  the first tasks, ahead of any porting work. All 256 were live on 2026-09-13.
- **No Fusion Tables data is recoverable anywhere** → Measured in task 2.3/2.4 and it is
  not the case: 16 of 32 tables have a local equivalent and the rest have an identified
  external source, though for polls and Boston municipal elections that source is an
  organization to ask rather than a file to download. The Drive check remains worthwhile
  because the original table is the only thing that reproduces a map exactly.
- **Wayback snapshots turn out not to contain rendered maps** → Likely: Wayback archives
  the iframe URL, not JS-rendered map tiles. Verified early so tier 2 is not planned
  around a source that does not exist.
- **Reconstructed maps silently disagree with the original post's numbers** → Re-sourced
  data may aggregate differently than the 2013 table. Where the post's text cites
  specific figures and a reconstruction cannot reproduce them, the map drops to tier 3
  rather than shipping a map that contradicts its own prose.
- **116 posts swamp the front-page listing** → Measured during the pilot with 24. If the
  full port would make the listing unusable, the follow-up change scopes a separate
  archive listing; that is a decision for the recommendation, not a blocker now.
- **Repo size grows by 30-40 MB of PNGs** → Acceptable for a GitHub Pages repo of this
  size; the pilot reports the real per-post figure so the full-port number is measured
  rather than extrapolated from a guess.
- **Effort is underestimated because the pilot posts are the ones we understood** →
  Mitigated by picking the pilot to span the cost range, and by reporting the range
  rather than a single average.

## Open Questions

- Do ported posts belong in the main listing interleaved by date, or in a separate
  archive section? Deferred deliberately: the pilot produces the evidence, and either
  answer is a front-matter and listing change that does not affect the specs or the
  task breakdown here.
- Should `massnumbers.blogspot.com` eventually redirect to the ported posts? Out of
  scope until there is something to redirect to.
