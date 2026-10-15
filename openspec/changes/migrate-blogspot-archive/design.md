# Design

## Context

See `proposal.md` -- Why. The archived `port-blogspot-archive` change left a working
pipeline and a measured cost model; this design is about running that pipeline 92
times safely, not rebuilding it. State as found on 2026-10-15:

- **Source and assets are already captured.** `_sources/blogspot/feed.json` holds all
  95 post bodies; `_sources/blogspot/images/` holds all 281 images (256 imgur, 25
  Blogger-hosted), 31.0 MB, each with `status=ok` in `images.csv`. No network access
  is needed for stage one.
- **The converter works across the archive.** `convert_post.py` writes all 95 posts
  with zero residual Fusion Tables URLs, zero residual HTML tags, and zero remote
  images (`conversion_report.csv`). 28 posts need minor hand work: 15
  stale-interactive-caption, 7 `TODO-TIER` markers, 6 leftover `<pre>`/`<style>`.
- **The staging and verification scripts are pilot-shaped.** `stage_pilot.py` reads
  converter output from a hard-coded scratchpad path from a previous session that no
  longer exists. `verify_fidelity.py` iterates a hard-coded `PILOTS` dict. The
  converter's own slugs are 60-character title truncations
  (`from-capuano-s-7th-to-tierney-s-6th-a-partisan-ranking-of-ma`), while the pilots
  were renamed by hand (`2012-11-18-house-district-partisan-ranking`).
- **Tier assignments are per reference, classes are per post.** `fusion_tables.csv`
  holds one row per reference; a post's class is its most expensive tier. Remaining
  stage-two posts: tier 1 external -- 2012-11-13, 2013-01-31, 2017-11-06; tier 1 local
  -- 2012-11-15, 2014-05-27, 2015-11-01, 2017-12-05; declared missing -- 2013-04-04,
  2013-07-23, 2013-09-26, 2014-06-03. All 9 tier-1 rows carry
  `prose_agreement=UNTESTED`.
- **Year distribution is lumpy.** Remaining posts: 42 from 2012-2013, 32 from 2014, 18
  from 2015-2022.
- **The listing is a single `index.qmd`** with `contents: posts`, `sort: date desc`,
  and a partial RSS feed. Native posts carry no `categories`.
- **Toolchain**: Quarto 1.9 or newer (the pilots rendered under 1.10.18), `renv`, and
  the `CLAUDE.md` conventions for `tmap` and `stan_glm`.

## Goals / Non-Goals

**Goals:**

- A repeatable per-post path from feed entry to verified, rendered post, driven by the
  manifest rather than by hand-kept lists.
- Small, reviewable commits: one per stage-one batch, one per stage-two post.
- Every check in the spec runnable as a script over the whole site, not only per post.

**Non-Goals:**

- Generalizing the tooling beyond this archive.
- Re-deriving tiers for stage-one posts. The 2.6 tier assignments stand; only tier-1
  rows get re-examined, via the prose-agreement check.
- Changing anything on `massnumbers.blogspot.com`.

## Decisions

**The manifest is the work queue.** `manifest.csv` gains `site_dir` (the chosen
`posts/` directory name) and `port_status` (`pending` / `staged` / `verified`).
Staging, link rewriting, and verification all read it; the completeness check is a
count over it. `fusion_tables.csv` gets its `prose_agreement` column filled in as each
tier-1 row is tested.
*Alternative considered:* a separate tracking file. Rejected -- the manifest already
has one row per post and is what the spec calls the system of record.

**Slugs are chosen up front, in one pass.** Before any batch, all 92 `site_dir` values
are written into the manifest: 3-6 word kebab-case phrases in the pilots' style,
derived from the title and reviewed as a list. Doing it once means intra-archive link
rewriting knows every target before any post is staged, and the slug list can be
reviewed in a single sitting.
*Alternative considered:* choose each slug at staging time. Rejected -- link rewriting
in an early batch would need targets that do not have names yet.

**Intra-archive links are rewritten to relative site paths at conversion time.** The
converter maps a `massnumbers.blogspot.com/YYYY/MM/*.html` href to its manifest row by
`blogger_path`, matching on path only so `http`/`https` and `www` variants all
resolve, and emits `../<site_dir>/index.qmd`, which Quarto resolves to the post's
rendered URL. Unmatched Blogger hrefs (label pages, the home page) pass through
unchanged. A link whose target is not ported yet would be broken on the site, so
`stage_post.py` runs a relink pass after every staging: relative links to unported
targets go back to their Blogger URL, and Blogger URLs whose target now exists become
relative links. Every commit is therefore self-consistent, and links into stage-two
posts (and the pilots' links into later batches) upgrade on their own when the target
lands. The pass rewrites link targets only, so it is safe on hand-corrected files.
*Alternative considered:* absolute `https://www.massnumbers.us/posts/...` URLs.
Rejected -- relative `.qmd` links let Quarto warn about broken targets at render time.

**Archive membership is a category, the listings split on it.** Ported posts get
`categories: [blogger-archive]`. `index.qmd` excludes that category; a new
`archive.qmd` lists only it, with its own navbar entry and no feed. Quarto listings
support `include`/`exclude` filters on item fields. Confirmed 2026-10-15 under Quarto
1.10.18 with a scratch two-post site: `exclude: {categories: "blogger-archive"}`
drops a post whose `categories` list contains that value from both the listing and
its feed, and `include:` with the same value selects only it. The glob-based fallback
is not needed.
*Alternative considered:* move ported posts to `archive/` instead of `posts/`.
Rejected -- the spec keeps the `posts/YYYY-MM-DD-slug/` convention, and moving
directories would change the three pilots' published URLs.

**Editorial notes use one callout style.** The pilot already uses
`::: {.callout-note appearance="simple"}` for both the provenance line and the
declared-missing note. Stale-interactive captions and reconstruction disclosures use
the same style, placed immediately after the original sentence they qualify. A single
style is what makes "this is not original text" learnable for a reader.

**`verify_fidelity.py` becomes a site-wide gate.** It iterates manifest rows with a
`site_dir`, strips editorial callouts as it already strips the provenance callout,
and reports similarity per post. It is extended, or joined by a sibling script, to
assert the other spec checks on rendered output in `docs/posts/<site_dir>/`: no
`i.imgur.com`, no `blogger.googleusercontent.com`, no Fusion Tables URL, no
`TODO-TIER`, and a link to the post's own permalink. A post moves to `verified` only
when all of these pass.

**Stage one in three year batches, stage two one post at a time.** Stage-one batches
are 2012-2013 (36), 2014 (30), 2015-2022 (15): large enough that the per-post overhead
amortizes, small enough that one batch's review fits in a sitting. Stage-two posts
each get their own commit because each involves a judgment -- reconstruct or declare
missing -- that should be reviewable on its own.
*Alternative considered:* port strictly by class (all image-only first). Rejected --
year batches keep cross-links within a batch mostly resolved and give reviewers a
coherent slice of the blog's history.

**Render per batch, full render once at the end.** Each batch is rendered by passing
its `.qmd` files to `quarto render`, which also rebuilds listings, search, and sitemap.
Stage-one posts contain no executable code, so this is fast. After the last stage-two
post, one full `quarto render` confirms the site builds from a clean state and that
`docs/site_libs/` loses nothing that a page references.

**Reconstruction follows a fixed gate.** For each tier-1 candidate: list every figure
the prose states about the map; compute the same figures from the candidate data;
reconstruct only if all match within rounding and coverage is comparable. External
data from `electionstats.state.ma.us` is fetched once into the post's `_sources/` and
read from there, so re-rendering never touches the network.

## Risks / Trade-offs

- [Quarto's listing `exclude` does not match inside a `categories` array] → Verified in
  the first task, before any batch; the glob-based fallback is decided in advance.
- [Most tier-1 candidates fail the prose-agreement check] → Expected to be likely given
  the pilot. The outcome is cheaper, not blocked: each becomes a declared-missing post
  with a written note. The spec makes this an accepted result.
- [Prose-similarity scores below 1.0 are noisy] → Score is a triage signal; any post
  below 1.0000 is read against its original by hand and the cause recorded, as was
  done for the pilots.
- [Dangling intra-archive links between batches] → Prevented by the relink pass;
  final verification with `--strict-links` requires that none remain.
- [`docs/` diffs are too large to review] → Commits separate source (`posts/`) from
  rendered output where practical, and the review focus is the `.qmd` and image diff.
- [Thumbnail choice for the archive listing] → Posts with images use their first
  image as `image:`; image-free posts get no thumbnail, as image-free native posts
  already do. (Quarto warns about their preview image while a batch is mid-render;
  the warning clears once every post in the batch exists.) Mechanical, so no
  per-post decision is needed.

## Migration Plan

1. Tooling and listing changes land first, with the three pilots recategorized. The
   site is unchanged for readers apart from the pilots moving to the archive page.
2. Stage-one batches land in date order, each a self-contained commit that renders.
3. Stage-two posts land individually.
4. Final full render and site-wide verification; manifest shows 95 `verified`.

Rollback at any point is reverting the batch's commit: posts are additive, and the
listing split does not depend on how many posts are ported.

## Open Questions

- Whether to add a notice to the Blogger site pointing readers to the new archive. It
  is a manual author action on Blogger, does not affect this repo, and can be decided
  after the port completes.
