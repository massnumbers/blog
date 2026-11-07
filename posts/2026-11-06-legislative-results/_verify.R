# Run from this post directory after loading tidyverse and sourcing _results.R.
expected <- tribble(
    ~district_display, ~party_result, ~candidate_result,
    "22nd Middlesex", "R to D flip", "Incumbent defeated",
    "8th Bristol", "D to R flip", "Incumbent defeated",
    "9th Essex", "R hold", "Incumbent re-elected",
    "9th Norfolk", "R hold", "Incumbent re-elected",
    "2nd Plymouth", "Pending", "Pending",
    "1st Worcester", "R to D flip", "Open-seat win",
    "18th Essex", "D hold", "Open-seat win"
)
actual <- expected |>
    select(district_display) |>
    left_join(results |> select(all_of(names(expected))), by = "district_display")
stopifnot(identical(actual, expected),
          identical(results$district_display[results$is_called == 0], "2nd Plymouth"),
          all(is.na(results$forecast_correct[results$is_called == 0])),
          all(str_starts(results$result_label[results$is_called == 0], "Leading:")))

# Exercise alias, missing-party, uncalled-at-100%-reporting, and ID fallback
# behavior independently of which candidates happen to run in this cohort.
edge_cases <- tibble(
    is_called = c(1, 1, 1, 0),
    id_winner = c(NA_real_, 2, 3, NA_real_),
    id_incumbent = c(NA_real_, 1, NA_real_, 4),
    name_winner = c("Susannah Whipps", "Different Person", "New Winner", NA),
    name_incumbent = c("Susannah M. Whipps", "Prior Person", NA, "Incumbent"),
    prior_winner_name = c("Susannah M. Whipps", "Prior Person", "Prior Winner", "Incumbent"),
    party_winner = c("Independent", "Independent", "Democratic", NA),
    prior_winner_party = c("Unenrolled", "Unenrolled", NA, "Republican"),
    incumbent_running = c(1, 1, 0, 1),
    precincts_reporting_pct = rep(100, 4)
) |>
    classify_outcomes()
stopifnot(identical(edge_cases$party_result,
                    c("I hold", "U to I flip", "Party result unknown", "Pending")),
          identical(edge_cases$candidate_result,
                    c("Incumbent re-elected", "Incumbent defeated",
                      "Open-seat win", "Pending")))
