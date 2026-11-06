# AP reporting units are municipalities within districts, not precinct results.
# The precinct geometry supplies only district-clipped municipality boundaries.
normalize_town <- function(name) str_to_lower(str_squish(name))
mapped_races <- bind_rows(featured, notable)
stopifnot(!anyDuplicated(mapped_races$ap_race_id))
mapped_rows <- municipality_results |>
    semi_join(mapped_races, by = "ap_race_id") |>
    left_join(pair_candidates |> select(ap_race_id, ap_candidate_id, role),
              by = c("ap_race_id", "ap_candidate_id"),
              relationship = "many-to-one")
stopifnot(!anyNA(mapped_rows$role),
          !anyDuplicated(mapped_rows[c("ap_race_id", "city_town", "ap_candidate_id")]))

municipality_votes <- mapped_rows |>
    group_by(ap_race_id, city_town) |>
    summarize(dem_votes = if (any(role == "dem")) sum(votes[role == "dem"]) else NA_real_,
              comparison_votes = if (any(role == "comparison")) sum(votes[role == "comparison"]) else NA_real_,
              other_votes = sum(votes[role == "other"]),
              precincts_reporting = first(precincts_reporting),
              precincts_total = first(precincts_total),
              reporting_pct = first(precincts_reporting_pct),
              consistent_reporting = n_distinct(precincts_reporting_pct) == 1 &
                  n_distinct(precincts_reporting) == 1 & n_distinct(precincts_total) == 1,
              .groups = "drop") |>
    left_join(mapped_races |>
                  select(ap_race_id, district, district_display, democrat,
                         opponent, comparison_party),
              by = "ap_race_id", relationship = "many-to-one") |>
    mutate(town_key = normalize_town(city_town),
           observed_margin = pair_margin(dem_votes, comparison_votes),
           margin = margin_label(observed_margin, comparison_party),
           dem_result = str_c(democrat, ": ", scales::comma(dem_votes), " votes"),
           comparison_result = str_c(opponent, ": ", scales::comma(comparison_votes), " votes"),
           other_result = scales::comma(other_votes),
           reporting = str_c(precincts_reporting, " / ", precincts_total,
                            " precincts (", formatC(reporting_pct, digits = 1,
                                                    format = "f"), "%)"))
stopifnot(all(municipality_votes$consistent_reporting))
reconciliation <- municipality_votes |>
    group_by(ap_race_id) |>
    summarize(across(c(dem_votes, comparison_votes, other_votes), sum), .groups = "drop") |>
    inner_join(mapped_races |> select(ap_race_id, dem_votes, comparison_votes, other_votes),
               by = "ap_race_id", suffix = c("_municipal", "_race"))
stopifnot(nrow(reconciliation) == nrow(mapped_races),
          all(reconciliation$dem_votes_municipal == reconciliation$dem_votes_race),
          all(reconciliation$comparison_votes_municipal == reconciliation$comparison_votes_race),
          all(reconciliation$other_votes_municipal == reconciliation$other_votes_race))

precinct_geometry <- read_sf("../../_gis/ma_wards_precincts_w_subs.geojson") |>
    filter(State_Rep %in% mapped_races$district) |>
    select(district = State_Rep, city_town) |>
    st_make_valid()
municipality_geometry <- precinct_geometry |>
    mutate(town_key = normalize_town(city_town)) |>
    group_by(district, town_key) |>
    summarize(city_town = first(city_town), .groups = "drop") |>
    st_simplify(dTolerance = 100, preserveTopology = TRUE)

# An AP town without matching district geometry indicates a bad join. Geometry
# without AP votes remains on the map, explicitly marked unavailable.
stopifnot(nrow(anti_join(municipality_votes,
                        st_drop_geometry(municipality_geometry),
                        by = c("district", "town_key"))) == 0)
municipality_map_data <- municipality_geometry |>
    left_join(municipality_votes |> select(-city_town),
              by = c("district", "town_key"), relationship = "one-to-one") |>
    mutate(margin = coalesce(margin, "Unavailable"),
           map_label = str_c(city_town, "\n", margin),
           across(c(dem_result, comparison_result, other_result, reporting),
                  ~ coalesce(.x, "Unavailable")))
stopifnot(nrow(municipality_map_data) == nrow(municipality_geometry),
          all(st_is_valid(municipality_map_data)),
          !any(st_is_empty(municipality_map_data)))

map_limit <- max(10, 10 * ceiling(max(abs(municipality_votes$observed_margin), na.rm = TRUE) / 10))
map_breaks <- c(-map_limit, -map_limit / 2, 0, map_limit / 2, map_limit)

map_caption <- function(district_name) {
    race <- mapped_races |> filter(district == district_name)
    str_c(race$result_label, "; ", race$call_label, "; ",
          formatC(race$precincts_reporting_pct, format = "f", digits = 1),
          "% district precincts reporting. ", source_note,
          " Municipality margins use the candidate pair's votes within this district;",
          " reporting is provisional and excludes blanks/write-ins. Gray = unavailable.")
}

municipality_result_map <- function(district_name, data = municipality_map_data) {
    map_data <- data |> filter(district == district_name)
    stopifnot(nrow(map_data) > 0)
    tm_shape(map_data) +
        tm_polygons(
            fill = "observed_margin",
            fill.scale = tm_scale_continuous(
                values = c("#CB454A", "white", "#24589A"),
                # Shared ticks also set the range for a one-municipality map.
                midpoint = 0,
                ticks = map_breaks,
                labels = margin_label(map_breaks, "R"),
                value.na = "#cccccc", label.na = "Unavailable"
            ),
            fill.legend = tm_legend(title = "Observed margin (points)"),
            fill_alpha = 0.8, col = "#333333", lwd = 1,
            id = "city_town",
            popup.vars = c("Democrat" = "dem_result",
                           "Comparison candidate" = "comparison_result",
                           "Other votes" = "other_result",
                           "Pair margin" = "margin",
                           "Municipality reporting" = "reporting")) +
        tm_text("map_label", size = 0.8) +
        tm_basemap("OpenStreetMap")
}
