# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Feasibility recommendation

**Reason**: Investigation-only requirement, satisfied by the archived
`port-blogspot-archive` change, whose `_sources/blogspot/FEASIBILITY.md` recommended a
full two-stage port. The migration itself is governed by the archive completeness
requirement.
**Migration**: None. `FEASIBILITY.md` remains in `_sources/blogspot/` as the record of
the decision.
