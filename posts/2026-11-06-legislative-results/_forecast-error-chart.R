forecast_error_chart <- function(data) {
    hometowns <- read_csv(
        "../2026-10-29-contested-races/forecast_14d_r2_target.csv",
        col_select = c(target_id, dem_candidate_municipality,
                       comparison_candidate_municipality),
        col_types = cols(.default = col_character())
    )
    chart_data <- data |>
        left_join(hometowns, by = "target_id", relationship = "one-to-one") |>
        transmute(id = target_id, district = district_display, chamber,
                  error = signed_error, forecast = forecast_margin,
                  observed = observed_margin, called = is_called == 1,
                  democrat = dem_candidate_name,
                  opponent = comparison_candidate_name,
                  opponentParty = comparison_candidate_party,
                  demTown = dem_candidate_municipality,
                  oppTown = comparison_candidate_municipality,
                  demShare = dem_votes / total_votes,
                  oppShare = comparison_votes / total_votes)
    stopifnot(nrow(chart_data) == 57, !anyDuplicated(chart_data$id),
              !anyNA(chart_data),
              all(between(chart_data$demShare, 0, 1)),
              all(between(chart_data$oppShare, 0, 1)),
              all(chart_data$demShare + chart_data$oppShare <= 1 + 1e-10))
    template <- paste(readLines("_forecast-error-chart.html"), collapse = "\n")
    stopifnot(str_count(template, fixed("__DATA__")) == 1,
              str_count(template, fixed("__SNAPSHOT__")) == 1)
    template <- str_replace(template, fixed("__SNAPSHOT__"),
                            htmltools::htmlEscape(snapshot_label))
    payload <- jsonlite::toJSON(chart_data, dataframe = "rows",
                                auto_unbox = TRUE, digits = NA)
    payload <- str_replace_all(payload, fixed("<"), function(x) "\\u003c")
    parts <- str_split(template, fixed("__DATA__"))[[1]]
    paste0(parts[1], payload, parts[2])
}
