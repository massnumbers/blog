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
