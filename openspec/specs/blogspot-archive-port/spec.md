## Purpose

Defines how posts from the legacy Blogger site (`massnumbers.blogspot.com`, 2012-2022)
are represented on the Quarto site: what counts as a faithful port, how assets and dead
third-party embeds are handled, and what provenance a reader sees on a ported post.

## Requirements

### Requirement: Archive manifest

The system SHALL maintain a machine-readable manifest of every post on the legacy
Blogger site, derived from the Blogger Atom feed, covering all 95 posts published
between 2012-11-13 and 2022-08-21.

Each manifest entry SHALL record the post's original publication date, title, labels,
Blogger permalink, and a classification of every external resource the post body
references, categorized as at minimum: static image, Fusion Tables embed, Google Sheets
link, other embed, or outbound citation link.

#### Scenario: Manifest covers the whole archive

- **WHEN** the manifest is generated from the Blogger feed
- **THEN** it contains one entry per published post, and the entry count matches the
  `totalResults` the feed reports

#### Scenario: External resources are classified

- **WHEN** a manifest entry is inspected for a post that embeds a Fusion Tables map
- **THEN** the entry lists that embed with its table ID, selected geometry column, and
  map center/zoom as preserved in the embed URL

#### Scenario: Liveness is recorded, not assumed

- **WHEN** the manifest records an external resource
- **THEN** it also records the HTTP status observed for that resource and the date the
  check was made, so a later reader can tell recoverable resources from lost ones

### Requirement: Ported posts follow the site's post convention

A ported post SHALL be a directory `posts/YYYY-MM-DD-slug/index.qmd` whose date is the
post's original Blogger publication date, not the date it was ported, so that ported
posts interleave correctly with native posts in the site listing.

The post's YAML front matter SHALL carry the original title, an author entry for Brent
Benson, and a `description`, matching the structure used by existing posts.

#### Scenario: Original date is preserved

- **WHEN** a post originally published 2013-06-26 on Blogger is ported
- **THEN** its directory is named `posts/2013-06-26-<slug>/` and its front-matter
  `date` is `2013-06-26`

#### Scenario: Ported post renders under the current toolchain

- **WHEN** `quarto render posts/<slug>/index.qmd` is run for a ported post
- **THEN** it renders without error under Quarto 1.9 and the project's `renv` package
  set, and the post appears in the site listing and search index

### Requirement: Content fidelity

A ported post SHALL preserve the original prose and its structure. Ported text MUST NOT
be rewritten, summarized, modernized, or extended with analysis the original did not
contain.

Editorial changes SHALL be limited to format conversion: Blogger HTML to Quarto
markdown, image references rewritten to local paths, and the treatment of dead embeds
required below.

#### Scenario: Prose is unchanged

- **WHEN** a ported post is compared against its Blogger original
- **THEN** the body text is the same modulo HTML-to-markdown formatting, with no
  added, removed, or reworded claims

#### Scenario: Outbound links are left as written

- **WHEN** a ported post cites a news article whose URL now 404s
- **THEN** the link is preserved as published rather than silently retargeted or
  removed

### Requirement: Asset localization

Images a ported post depends on SHALL be stored in the repository alongside the post
and referenced by relative path. A rendered ported post MUST NOT depend on a
third-party image host at read time.

#### Scenario: Imgur images are localized

- **WHEN** a post whose original body references `i.imgur.com` images is ported
- **THEN** those images are downloaded into the post's directory and the rendered page
  serves them from the site, making the post readable if imgur later removes them

#### Scenario: An unrecoverable image is declared

- **WHEN** a referenced image can no longer be fetched from any source
- **THEN** the ported post shows an explicit note in place of the image rather than a
  broken image reference

### Requirement: Fidelity tiers for defunct embeds

For each embed whose backing service no longer exists — Google Fusion Tables above all,
which was shut down on 2019-12-03 — a ported post SHALL apply exactly one of the
following tiers, and the tier applied SHALL be recorded in the manifest:

1. **Reconstructed** — the map is rebuilt from recovered or equivalent data as a native
   interactive map, following the project's `tmap` conventions.
2. **Static** — a static image of the original map is used, recovered from an archive
   snapshot or rendered from recovered data, with interactivity lost.
3. **Declared missing** — the post states plainly that the original interactive map is
   no longer available and describes what it showed.

A ported post MUST NOT embed a URL that is known to be dead.

#### Scenario: Reconstruction changes the numbers

- **WHEN** a map is reconstructed from data that is not the original table
- **THEN** the post discloses that the map was rebuilt and names the data source used,
  so a reader is not led to believe they are seeing the 2013 original

#### Scenario: No data is recoverable

- **WHEN** neither the Fusion Table nor equivalent underlying data can be found for a
  post's map
- **THEN** the post applies the declared-missing tier and the manifest records that the
  data is lost, rather than the post shipping a dead embed or an empty frame

#### Scenario: Dead embeds do not survive the port

- **WHEN** any ported post is rendered
- **THEN** no `fusiontables.google.com` or `fusiontables.googleusercontent.com` URL
  appears in its output

### Requirement: Provenance

Every ported post SHALL be identifiable as a repost from the legacy Blogger site and
SHALL link to its original permalink, so that readers and search engines can tell the
port from the original.

#### Scenario: Reader sees the origin

- **WHEN** a reader opens a ported post on `www.massnumbers.us`
- **THEN** the post states that it was originally published on the Blogger site on its
  original date and links to the original permalink

### Requirement: Feasibility recommendation

The investigation SHALL produce a written recommendation on whether to port the full
archive, a defined subset, or none of it.

The recommendation SHALL be grounded in measured evidence from the pilot ports rather
than estimates alone, and SHALL report, per fidelity tier, the effort a ported post
actually required.

#### Scenario: Recommendation is backed by pilot data

- **WHEN** the recommendation is delivered
- **THEN** it cites the per-post effort measured across the pilot posts, the count of
  archive posts in each fidelity tier, and the assets and data recovered versus lost

#### Scenario: A negative result is a valid outcome

- **WHEN** the evidence shows the archive cannot be ported at acceptable fidelity or
  cost
- **THEN** the recommendation says so and proposes the alternative it prefers, and no
  further posts are ported under this change
