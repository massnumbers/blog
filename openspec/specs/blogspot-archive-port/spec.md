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
posts sort correctly by date wherever they are listed.

The slug SHALL be a short, readable name in the style of native posts rather than a
truncated copy of the Blogger title, and SHALL be recorded in the archive manifest.

The post's YAML front matter SHALL carry the original title, an author entry for Brent
Benson, a `description`, and the archive category that identifies it as a ported post,
matching the structure used by existing posts.

#### Scenario: Original date is preserved

- **WHEN** a post originally published 2013-06-26 on Blogger is ported
- **THEN** its directory is named `posts/2013-06-26-<slug>/` and its front-matter
  `date` is `2013-06-26`

#### Scenario: Slug is readable and recorded

- **WHEN** a post titled "From Capuano's 7th to Tierney's 6th: a partisan ranking of
  MA congressional districts" is ported
- **THEN** its slug is a short phrase rather than a 60-character truncation of the
  title, and the manifest row for that post records the directory name

#### Scenario: Ported post is identifiable by category

- **WHEN** a ported post's front matter is inspected
- **THEN** it carries the archive category, and no native post does

#### Scenario: Ported post renders under the current toolchain

- **WHEN** `quarto render posts/<slug>/index.qmd` is run for a ported post
- **THEN** it renders without error under Quarto 1.9 or newer and the project's `renv`
  package set, and the post appears in the archive listing and search index

### Requirement: Content fidelity

A ported post SHALL preserve the original prose and its structure. Ported text MUST NOT
be rewritten, summarized, modernized, or extended with analysis the original did not
contain.

Editorial changes SHALL be limited to format conversion: Blogger HTML to Quarto
markdown, image references rewritten to local paths, intra-archive links retargeted to
ported posts, the treatment of dead embeds required below, and distinguishable
editorial notes.

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

### Requirement: Archive listing

Ported posts SHALL be listed on a dedicated archive page reachable from the site
navbar, in reverse-chronological order. The front-page listing and its RSS feed MUST
NOT include ported posts. Ported posts SHALL remain in the site search index and
sitemap.

#### Scenario: Front page shows native posts only

- **WHEN** a reader opens the site's front page after the archive is ported
- **THEN** the listing contains only posts written for the Quarto site, and no post
  dated before 2022-08-21 or carrying the archive category appears in it

#### Scenario: Archive page lists every ported post

- **WHEN** a reader follows the navbar link to the archive page
- **THEN** it lists every ported post, newest first, each at its original date

#### Scenario: Feed subscribers are not flooded

- **WHEN** ported posts are added to the site
- **THEN** the front-page RSS feed gains no entries for them

#### Scenario: Ported posts are searchable

- **WHEN** a reader searches the site for a term that appears in a ported post
- **THEN** the ported post appears in the search results

### Requirement: Intra-archive links resolve to ported posts

A link in a ported post whose target is another post on the legacy Blogger site SHALL
point to that post's ported copy on this site, once that copy exists. The link text
and surrounding prose MUST NOT change.

#### Scenario: Link between two ported posts

- **WHEN** a ported post links to `massnumbers.blogspot.com/2012/11/how-democratic-or-republic-is-my-town.html`
  and that post has also been ported
- **THEN** the rendered link targets the ported post on `www.massnumbers.us` and its
  link text is identical to the original

#### Scenario: Link to a Blogger page that is not a post

- **WHEN** a ported post links to a Blogger page that has no ported counterpart, such
  as a label search or the blog's home page
- **THEN** the link is left as published

### Requirement: Editorial notes are distinguishable

Any text added to a ported post that was not in the original -- the provenance line, a
declared-missing map note, a reconstruction disclosure, or a note on a caption that
refers to something no longer available -- SHALL be visually set apart from the
original prose so a reader can tell which words are from the original.

#### Scenario: Caption promises a vanished interactive map

- **WHEN** an original post says "click the map for an interactive version" above a
  screenshot whose interactive target is gone
- **THEN** the original sentence is kept verbatim and a distinct note beside it states
  that the interactive version is no longer available

#### Scenario: No unresolved placeholders ship

- **WHEN** any ported post is rendered
- **THEN** its output contains no conversion placeholder marker in place of a resolved
  editorial note

### Requirement: Reconstruction agrees with the post's own figures

Before a map is reconstructed, every figure the post's prose states about what the map
shows SHALL be checked against the reconstruction's data. A map whose data contradicts
a stated figure, or which covers materially fewer geographies than the original, MUST
be declared missing rather than reconstructed, and the check's outcome SHALL be
recorded in the manifest.

#### Scenario: Method mismatch demotes the map

- **WHEN** a post ranks districts by a multi-race average and the only available data
  is a presidential-based index that reorders the post's named top and bottom
  districts
- **THEN** the map is declared missing, the post's note explains why it was not
  rebuilt, and the manifest records the failed check

#### Scenario: Agreement allows reconstruction

- **WHEN** every figure the post states is reproduced by the re-sourced data
- **THEN** the map may be reconstructed, with the disclosure required for rebuilt maps

### Requirement: Archive completeness

The migration SHALL end with every post in the archive manifest ported, and the
manifest SHALL record for each post its site directory and port status. A post MUST
NOT be counted as ported until it renders and passes the fidelity, asset, dead-embed,
and provenance checks.

#### Scenario: Manifest accounts for every post

- **WHEN** the migration is declared complete
- **THEN** all 95 manifest rows show a ported status and a site directory that exists
  under `posts/`

#### Scenario: Site-wide verification passes

- **WHEN** the full site is rendered after the final batch
- **THEN** no rendered ported post references `i.imgur.com`, a Blogger-hosted image,
  or a Fusion Tables URL, and every ported post links to its Blogger permalink
