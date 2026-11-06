# Shared table layout keeps the overview, notable race, and full cohort aligned.
results_table <- function(data, title, full = FALSE, show_margin_note = TRUE) {
    display <- data |>
        mutate(democrat = str_c(htmltools::htmlEscape(democrat), "<br>",
                               scales::comma(dem_votes), " votes"),
               opponent = str_c(htmltools::htmlEscape(opponent), "<br>",
                               scales::comma(comparison_votes), " votes"),
               status = str_c(
                   htmltools::htmlEscape(result_label),
                   if_else(is_called == 0,
                           str_c("<br>Uncalled: ",
                                 str_remove(formatC(precincts_reporting_pct,
                                                    digits = 1, format = "f"),
                                            "\\.0$"),
                                 "% reporting"), ""))) |>
        select(chamber, district_url, district_display, democrat, opponent,
               other_votes, observed, model, model_range, error_label, status,
               party_result, candidate_result)
    if (!full) display <- display |>
        select(-chamber, -model_range, -error_label)

    table <- display |>
        gt() |>
        gt_theme_538() |>
        fmt_url(columns = district_url, label = from_column("district_display")) |>
        cols_hide(columns = district_display) |>
        fmt_markdown(columns = c(democrat, opponent, status)) |>
        fmt_number(columns = other_votes, decimals = 0) |>
        cols_label(district_url = "District", democrat = "Democrat",
                   opponent = "Comparison candidate", other_votes = "Other votes",
                   observed = "Observed margin", model = "Model margin",
                   status = "AP result / reporting", party_result = "Party control",
                   candidate_result = "Incumbency") |>
        tab_spanner(label = "Candidates and votes", columns = c(democrat, opponent, other_votes)) |>
        tab_spanner(label = "Margin (points)", columns = c(observed, model)) |>
        tab_spanner(label = "Outcome", columns = c(party_result, candidate_result)) |>
        cols_width(district_url ~ px(100), democrat ~ px(165), opponent ~ px(165),
                   other_votes ~ px(70), observed ~ px(115), model ~ px(85),
                   status ~ px(190), party_result ~ px(95), candidate_result ~ px(120)) |>
        tab_style(style = cell_text(whitespace = "normal"),
                  locations = list(cells_body(), cells_column_labels())) |>
        cols_align(align = "left", columns = everything()) |>
        cols_align(align = "right", columns = other_votes) |>
        tab_header(title = title) |>
        tab_source_note(source_note) |>
        tab_options(quarto.disable_processing = TRUE, table.font.size = px(15), data_row.padding = px(10),
                    container.width = pct(100), container.overflow.x = "auto",
                    table.layout = "fixed", table.width = px(if (full) 1420 else 1105))
    if (show_margin_note) table <- table |> tab_source_note(margin_note)
    if (full) table <- table |>
        cols_label(chamber = "Office", model_range = "75% model range",
                   error_label = "Error (pp)") |>
        cols_width(chamber ~ px(65), model_range ~ px(160), error_label ~ px(90))
    table
}

outcome_summary_table <- function(data) {
    outcomes <- with_provisional_outcomes(data) |>
        mutate(party_result = str_remove(party_result, fixed(" (provisional)")),
               incumbency = str_remove(candidate_result, fixed(" (provisional)")))
    party_counts <- outcomes |>
        count(party_result, name = "count") |>
        arrange(match(party_result, c("D hold", "R to D flip",
                                     "D to R flip", "R hold")))
    incumbency_counts <- outcomes |>
        count(incumbency, name = "count") |>
        arrange(match(incumbency, c("Incumbent re-elected", "Incumbent defeated",
                                   "Open-seat win")))
    stopifnot(sum(party_counts$count) == nrow(data),
              sum(incumbency_counts$count) == nrow(data), nrow(data) == 57)
    rows <- seq_len(max(nrow(party_counts), nrow(incumbency_counts)))
    summary <- tibble(party = party_counts$party_result[rows],
                      party_count = party_counts$count[rows],
                      incumbency = incumbency_counts$incumbency[rows],
                      incumbency_count = incumbency_counts$count[rows]) |>
        bind_rows(tibble(party = "Total", party_count = nrow(data),
                         incumbency = "Total", incumbency_count = nrow(data)))
    summary |>
        gt() |>
        gt_theme_538() |>
        cols_label(party = "Party", party_count = "Count",
                   incumbency = "Incumbency", incumbency_count = "Count") |>
        fmt_number(columns = c(party_count, incumbency_count), decimals = 0) |>
        sub_missing(columns = everything(), missing_text = "") |>
        cols_align(align = "center", columns = c(party_count, incumbency_count)) |>
        cols_width(party ~ pct(32), party_count ~ pct(12),
                   incumbency ~ pct(44), incumbency_count ~ pct(12)) |>
        tab_style(style = cell_borders(sides = "left", color = "#dddddd"),
                  locations = list(cells_body(columns = incumbency),
                                   cells_column_labels(columns = incumbency))) |>
        tab_style(style = list(cell_text(weight = "bold"),
                               cell_borders(sides = "top", color = "#333333")),
                  locations = cells_body(rows = party == "Total")) |>
        tab_header(title = "Outcomes across 57 contested races") |>
        tab_source_note(source_note) |>
        tab_source_note("Some results are provisional.") |>
        tab_options(quarto.disable_processing = TRUE, table.width = pct(100),
                    data_row.padding = px(8), container.overflow.x = "auto")
}
