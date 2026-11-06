# legislative-results-post Specification

## Purpose

Provide an author-editable legislative-results post whose tables and municipality maps reproducibly compare unofficial election results with the published pre-election forecast.

## Requirements

### Requirement: Post scaffold reserves narrative for the author

The post SHALL exist at `posts/2026-11-06-legislative-results/index.qmd` with title, subtitle, description, author, date, and draft metadata. Its body SHALL contain ordered section headings and working visualizations without drafted narrative. Factual visualization labels, captions, source/status notes, and legends SHALL be permitted.

#### Scenario: Author opens the scaffold

- **WHEN** the author opens the post source
- **THEN** the metadata reflects `_README.md`, with the title spelling corrected to "Winners, losers, and surprises", author Brent Benson, date 2026-11-06, and `draft: true`
- **AND** the body contains sections for the four closest forecast races, other notable results including 22nd Middlesex, and all 57 contested results, in that order
- **AND** there are no drafted introductory, race-analysis, or concluding paragraphs and no visible prose placeholders

### Requirement: Results are pinned and reproducible

The post SHALL use a local, documented snapshot of the November 3, 2026 unofficial AP results from `ma-election-db` and the same 14d-r2 forecast used by the October 29 post. Rendering SHALL require neither the sibling repository nor live result fetching. Data displays SHALL identify the unofficial source and snapshot time.

#### Scenario: Render without sibling repository access

- **WHEN** the post is executed in a checkout with its committed inputs
- **THEN** all tables and maps use those local inputs and record the AP snapshot time
- **AND** provenance identifies source paths, source revision, snapshot time, and the forecast version and cutoff

### Requirement: Featured races follow the pre-election selection

The first results section SHALL contain an overview table and one municipality result map for each of 9th Norfolk, 8th Bristol, 9th Essex, and 3rd Barnstable, matching the pre-election post's order. The table SHALL show candidates/parties, votes, observed and forecast margins, and reporting/call status.

#### Scenario: Read the four-race overview

- **WHEN** the featured results section is rendered
- **THEN** it presents exactly those four districts in that order, regardless of which races ultimately finish closest
- **AND** each district has a named subsection and an interactive municipality map

### Requirement: Municipality maps reflect district-specific results

Maps SHALL display observed candidate-pair margins by municipality within the selected district using a shared diverging scale centered at zero. Popups SHALL identify candidates, votes, margin, and local reporting completeness. Split municipalities SHALL use only the district portion's results and geometry. Missing or zero-denominator results SHALL be marked unavailable.

#### Scenario: Inspect a split municipality

- **WHEN** a municipality is split among districts
- **THEN** its mapped boundary and votes cover only the selected district's portion
- **AND** the map does not present the result as a citywide or precinct-level measurement

#### Scenario: Municipality has no usable votes

- **WHEN** a district-municipality has missing results or zero votes for the modeled candidate pair
- **THEN** it is visibly unavailable rather than shown as tied or silently dropped

### Requirement: Notable results include 22nd Middlesex

The other-notable-results section SHALL include a 22nd Middlesex subsection and a data display identifying Marc Lombardo, the opposing candidate, the AP winner when called, vote totals, observed margin, forecast margin, and reporting/call status.

#### Scenario: Review Lombardo's defeat

- **WHEN** the pinned AP snapshot calls 22nd Middlesex for the Democrat
- **THEN** its display identifies Lombardo's incumbent defeat and the Republican-to-Democratic flip without adding narrative analysis

### Requirement: Full table compares all forecast races consistently

The full results table SHALL contain exactly one row per race in the pre-election 57-race forecast cohort. It SHALL show chamber/district, candidates/parties, candidate votes, AP winner or current leader, reporting/call status, forecast margin and 75% interval, observed margin, signed margin error, and outcome characterization. Observed margins SHALL use the forecast candidate pair's votes; other candidate votes SHALL remain separately identifiable.

#### Scenario: Compare actual and forecast margins

- **WHEN** a race has positive votes for the modeled candidate pair
- **THEN** observed margin equals `100 * (D - comparison) / (D + comparison)` and margin error equals observed minus forecast in percentage points
- **AND** positive error indicates a more Democratic result than forecast
- **AND** candidate vote totals include a separate other-votes field when applicable, with the pair-only denominator explained in a display note

### Requirement: Outcome characterizations separate party control from incumbency

Called races SHALL identify both party hold/flip, relative to the prior seat winner, and incumbent re-elected/defeated or open-seat win. Uncalled races SHALL remain pending and SHALL NOT receive a definitive hold/flip, incumbent outcome, or forecast-correctness judgment. Equivalent Independent/Unenrolled labels for the same incumbent SHALL NOT manufacture a flip.

#### Scenario: Incumbent loses to the other party

- **WHEN** an incumbent is on the ballot and AP calls the race for an opposing-party challenger
- **THEN** the outcome identifies the winning party, the party flip, and the incumbent defeat

#### Scenario: Open seat is decided

- **WHEN** no incumbent is on the ballot and AP calls the race
- **THEN** the outcome identifies an open-seat win and whether the prior party held or lost the seat

#### Scenario: Incumbent retains the seat

- **WHEN** AP calls a race for its incumbent
- **THEN** the outcome identifies incumbent re-election and a party hold

#### Scenario: AP has not called a race

- **WHEN** a race remains uncalled, including 9th Norfolk in the current snapshot
- **THEN** the display labels its current leader and provisional margin, shows reporting completeness, and leaves its definitive outcome pending
- **AND** complete reporting alone does not substitute for an AP call

### Requirement: Visualizations render under the repository toolchain

The post SHALL render successfully with Quarto 1.9 or newer and the repository's R environment. Tables SHALL be readable at their intended widths and map widgets SHALL load, display legends/popups, and retain required local assets in a clean checkout.

#### Scenario: Verify generated output

- **WHEN** the post is re-executed and its rendered output inspected
- **THEN** all specified tables and maps appear with correct values and functioning interactions, and required freeze/widget dependencies are included
- **AND** the unfinished post remains marked as a draft
