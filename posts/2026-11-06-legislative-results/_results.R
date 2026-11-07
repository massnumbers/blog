# Pinned AP inputs and the published 14d-r2 forecast; see _provenance.json.
comparison <- read_csv("ma_general_2026_forecast_comparison.csv.gz",
                       col_types = cols(snapshot_time = col_character(),
                                        district_id = col_character(),
                                        ap_race_id = col_character()))
races <- read_csv("ma_general_2026_races.csv.gz",
                  col_types = cols(snapshot_time = col_character(),
                                        district_id = col_character(),
                                   ap_race_id = col_character(),
                                   .default = col_guess()))
municipality_results <- read_csv("ma_general_2026_results.csv.gz",
                                col_types = cols(snapshot_time = col_character(),
                                        district_id = col_character(),
                                                 ap_race_id = col_character(),
                                                 ap_candidate_id = col_character(),
                                                 candidate_id = col_character()))
provenance <- jsonlite::read_json("_provenance.json", simplifyVector = TRUE)
stopifnot(nrow(races) == 200, nrow(municipality_results) == 544,
          nrow(comparison) == 57, !anyDuplicated(comparison$target_id),
          !anyDuplicated(comparison[c("office", "district_id")]),
          !anyDuplicated(races[c("office", "district_id")]),
          all(c(races$snapshot_time, comparison$snapshot_time,
                municipality_results$snapshot_time) == provenance$snapshot_time),
          all(between(comparison$precincts_reporting_pct, 0, 100)))

party_label <- function(party) {
    recode(party, "Democratic" = "D", "Republican" = "R",
           "Independent" = "I", "Unenrolled" = "U", "Other" = "Other",
           "Workers Party" = "WP", "Gulf War Veteran" = "GWV",
           .missing = "Unknown")
}

# AP and forecast names differ in middle names and suffixes. The candidate
# pair is selected by party, then verified by first/last name for every race.
identity_key <- function(name) {
    name |>
        str_to_lower() |>
        str_replace_all("[^a-z ]", "") |>
        str_squish() |>
        str_remove(" (jr|sr|ii|iii|iv)$") |>
        str_replace("^([^ ]+).* ([^ ]+)$", "\\1 \\2")
}

candidate_totals <- municipality_results |>
    group_by(ap_race_id, ap_candidate_id, candidate_name, party,
             is_incumbent) |>
    summarize(votes = sum(votes), .groups = "drop")

pair_candidates <- candidate_totals |>
    group_by(ap_race_id) |>
    mutate(role = case_when(
        party == "Democratic" ~ "dem",
        party == "Republican" ~ "comparison",
        !any(party == "Republican") ~ "comparison",
        TRUE ~ "other"
    )) |>
    ungroup()
stopifnot(!anyDuplicated(pair_candidates |>
                            filter(role != "other") |>
                            select(ap_race_id, role)))

pair_identity <- pair_candidates |>
    filter(role != "other") |>
    select(ap_race_id, role, ap_candidate_id, candidate_name, party,
           is_incumbent, votes) |>
    pivot_wider(names_from = role,
                values_from = c(ap_candidate_id, candidate_name, party,
                                is_incumbent, votes))

results <- comparison |>
    left_join(races |>
                  select(office, district_id, id_winner, id_incumbent,
                         name_incumbent, incumbent_running,
                         prior_winner_name, prior_winner_party, total_votes),
              by = c("office", "district_id"), relationship = "one-to-one") |>
    left_join(pair_identity, by = "ap_race_id", relationship = "one-to-one") |>
    mutate(chamber = if_else(office == "State Senate", "Senate", "House"),
           district = str_replace(district, " & ", " and "),
           district_url = str_c(
               "https://mapoli.us/districts/",
               if_else(chamber == "Senate", "state-senate/", "state-rep/"),
               str_replace_all(str_to_lower(district), "[^a-z0-9]+", "-"),
               ".html"),
           comparison_party = party_label(comparison_candidate_party),
           democrat = str_c(candidate_name_dem, " (D)",
                            if_else(is_incumbent_dem == 1, "*", "")),
           opponent = str_c(candidate_name_comparison, " (", comparison_party,
                            ")", if_else(is_incumbent_comparison == 1, "*", "")),
           leader = case_when(
               dem_votes > comparison_votes ~ str_c(candidate_name_dem, " (D)"),
               dem_votes < comparison_votes ~ str_c(candidate_name_comparison,
                                                      " (", comparison_party, ")"),
               TRUE ~ "Tied"
           ),
           result_label = if_else(is_called == 1,
                                  str_c("Winner: ", name_winner, " (",
                                        party_label(party_winner), ")"),
                                  str_c("Leading: ", leader)),
           call_label = if_else(is_called == 1, "AP called", "Uncalled"))

stopifnot(nrow(results) == 57, sum(results$chamber == "House") == 47,
          sum(results$chamber == "Senate") == 10,
          all(!is.na(results$incumbent_running)),
          all(identity_key(results$dem_candidate_name) ==
                  identity_key(results$candidate_name_dem)),
          all(identity_key(results$comparison_candidate_name) ==
                  identity_key(results$candidate_name_comparison)),
          all(results$votes_dem == results$dem_votes),
          all(results$votes_comparison == results$comparison_votes),
          all(results$total_votes == results$dem_votes +
                  results$comparison_votes + results$other_votes))

featured_districts <- c("9th Norfolk", "8th Bristol", "9th Essex", "3rd Barnstable")
stopifnot(all(featured_districts %in% results$district_display))

pair_margin <- function(dem, opponent) {
    denominator <- dem + opponent
    if_else(!is.na(denominator) & denominator > 0,
            100 * (dem - opponent) / denominator, NA_real_)
}

margin_label <- function(margin, opponent_party) {
    case_when(
        is.na(margin) ~ "Unavailable",
        abs(margin) < 0.05 ~ "EVEN",
        margin > 0 ~ str_c("D+", formatC(abs(margin), format = "f", digits = 1)),
        TRUE ~ str_c(opponent_party, "+",
                     formatC(abs(margin), format = "f", digits = 1))
    )
}

results <- results |>
    mutate(observed_margin = pair_margin(dem_votes, comparison_votes),
           signed_error = observed_margin - forecast_margin,
           observed = str_c(margin_label(observed_margin, comparison_party),
                            if_else(is_called == 1, "", " (provisional)")),
           model = margin_label(forecast_margin, comparison_party),
           model_range = str_c(margin_label(lower_75, comparison_party), " to ",
                               margin_label(upper_75, comparison_party)),
           error_label = if_else(is.na(signed_error), "Unavailable",
                                 sprintf("%+.1f", signed_error)))
stopifnot(isTRUE(all.equal(results$observed_margin, results$actual_margin)),
          isTRUE(all.equal(results$signed_error, results$margin_error)),
          all(results$lower_75 <= results$upper_75),
          is.na(pair_margin(0, 0)), is.na(pair_margin(NA_real_, 1)),
          pair_margin(60, 40) == 20, pair_margin(40, 60) == -20)

snapshot_label <- format(
    as.POSIXct(provenance$snapshot_time, format = "%Y-%m-%dT%H:%M:%OSZ", tz = "UTC"),
    "%B %d, %Y, %H:%M UTC", tz = "UTC"
)
stopifnot(!is.na(snapshot_label))
source_note <- paste(
    str_c("Unofficial AP results; snapshot ", snapshot_label, "."),
    "AP calls and precincts reporting are separate measures."
)
margin_note <- paste(
    "Margins and 75% forecast ranges use only the Democratic and comparison",
    "candidates' votes; other votes are shown separately. Blanks/write-ins excluded.",
    "Error = observed minus model, in percentage points; positive = more Democratic.",
    "Uncalled margins/errors are provisional. * Incumbent. Model: 14d-r2,",
    "finance cutoff October 20."
)

same_person <- function(id_a, id_b, name_a, name_b) {
    if_else(!is.na(id_a) & !is.na(id_b),
            as.character(id_a) == as.character(id_b),
            coalesce(identity_key(name_a) == identity_key(name_b), FALSE))
}

classify_outcomes <- function(data) {
    data |>
        mutate(winner_is_incumbent = same_person(
                   id_winner, id_incumbent, name_winner, name_incumbent),
               winner_is_prior = coalesce(identity_key(name_winner) ==
                                              identity_key(prior_winner_name), FALSE),
               # Independent/Unenrolled aliases count as a hold for the same
               # person only; neither label is collapsed for different people.
               alias_hold = winner_is_prior &
                   party_winner %in% c("Independent", "Unenrolled") &
                   prior_winner_party %in% c("Independent", "Unenrolled"),
               party_result = case_when(
                   is_called != 1 ~ "Pending",
                   is.na(prior_winner_party) | is.na(party_winner) |
                       prior_winner_party == "Other" | party_winner == "Other" ~
                       "Party result unknown",
                   party_winner == prior_winner_party | alias_hold ~
                       str_c(party_label(party_winner), " hold"),
                   TRUE ~ str_c(party_label(prior_winner_party), " to ",
                                party_label(party_winner), " flip")
               ),
               candidate_result = case_when(
                   is_called != 1 ~ "Pending",
                   incumbent_running == 0 ~ "Open-seat win",
                   winner_is_incumbent ~ "Incumbent re-elected",
                   TRUE ~ "Incumbent defeated"
               ))
}
results <- classify_outcomes(results)

# Label the outcome indicated by a current lead without changing AP call data.
with_provisional_outcomes <- function(data) {
    provisional <- data$is_called == 0 & !is.na(data$observed_margin) &
        data$observed_margin != 0
    indicated <- data |>
        mutate(id_winner = if_else(provisional, NA_real_, id_winner),
               name_winner = if_else(
                   provisional,
                   if_else(observed_margin > 0, candidate_name_dem,
                           candidate_name_comparison), name_winner),
               party_winner = if_else(
                   provisional,
                   if_else(observed_margin > 0, "Democratic",
                           comparison_candidate_party), party_winner),
               is_called = if_else(provisional, 1, is_called)) |>
        classify_outcomes()
    data |>
        mutate(party_result = if_else(
                   provisional, str_c(indicated$party_result, " (provisional)"),
                   party_result),
               candidate_result = if_else(
                   provisional, str_c(indicated$candidate_result, " (provisional)"),
                   candidate_result))
}

featured <- results |>
    filter(district_display %in% featured_districts) |>
    arrange(match(district_display, featured_districts))
notable <- results |>
    filter(chamber == "House", district_display == "22nd Middlesex")
stopifnot(identical(featured$district_display, featured_districts), nrow(notable) == 1)
