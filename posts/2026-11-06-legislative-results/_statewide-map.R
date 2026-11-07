# House and Senate overlap, so display one chamber at a time.
state_results <- with_provisional_outcomes(results) |>
    mutate(outcome = str_remove(party_result, fixed(" (provisional)")),
           outcome_class = case_when(
               outcome == "D hold" ~ "outcome-d-hold",
               outcome == "R to D flip" ~ "outcome-r-to-d",
               outcome == "D to R flip" ~ "outcome-d-to-r",
               outcome == "R hold" ~ "outcome-r-hold"
           ),
           fill_color = if_else(outcome %in% c("D hold", "R to D flip"),
                                "#24589A", "#CB454A"),
           border_dash = if_else(is_called == 0, "5,4", ""),
           hover = str_c(chamber, ": ", district_display, " - ", party_result),
           popup = str_c(
               "<strong>", htmltools::htmlEscape(chamber), ": ",
               htmltools::htmlEscape(district_display), "</strong><br>",
               htmltools::htmlEscape(result_label), "<br>",
               htmltools::htmlEscape(party_result), "<br>",
               htmltools::htmlEscape(candidate_result), "<br>",
               htmltools::htmlEscape(democrat), ": ", scales::comma(dem_votes),
               " votes<br>", htmltools::htmlEscape(opponent), ": ",
               scales::comma(comparison_votes), " votes<br>",
               "Observed margin: ", htmltools::htmlEscape(observed),
               if_else(is_called == 0,
                       str_c("<br>Uncalled: ",
                             str_remove(formatC(precincts_reporting_pct,
                                                digits = 1, format = "f"), "\\.0$"),
                             "% reporting"), "")))
stopifnot(nrow(state_results) == 57, !anyNA(state_results$outcome_class))

house_boundaries <- read_sf("../../_gis/HOUSE2021/HOUSE2021_POLY.shp") |>
    st_make_valid() |>
    st_simplify(dTolerance = 100, preserveTopology = TRUE) |>
    select(district_display = REP_DIST)
house_outcomes <- house_boundaries |>
    inner_join(state_results |> filter(chamber == "House"),
               by = "district_display", relationship = "one-to-one") |>
    st_transform(4326)
senate_outcomes <- read_sf("../../_gis/SENATE2021/SENATE2021_POLY.shp") |>
    st_make_valid() |>
    st_simplify(dTolerance = 100, preserveTopology = TRUE) |>
    select(district = SEN_DIST) |>
    inner_join(state_results |> filter(chamber == "Senate"),
               by = "district", relationship = "one-to-one") |>
    st_transform(4326)
stopifnot(nrow(house_outcomes) == 47, nrow(senate_outcomes) == 10,
          setequal(c(house_outcomes$target_id, senate_outcomes$target_id),
                   state_results$target_id),
          all(st_is_valid(house_outcomes)), all(st_is_valid(senate_outcomes)))

state_outline <- st_union(house_boundaries) |> st_transform(4326)
state_bounds <- st_bbox(state_outline)

outcome_legend <- paste0(
    '<div role="group" aria-label="Election outcomes" ',
    'style="background:white;padding:10px 12px;border-radius:4px;',
    'box-shadow:0 1px 5px #888;font:14px/1.6 sans-serif">',
    '<strong>Seat outcome</strong><br>',
    '<span style="display:inline-block;width:24px;height:14px;background:#24589A;margin-right:8px"></span>D hold<br>',
    '<span style="display:inline-block;width:24px;height:14px;background:repeating-linear-gradient(45deg,#24589A 0px,#24589A 8.5px,#CB454A 8.5px,#CB454A 10px);margin-right:8px"></span>R to D flip<br>',
    '<span style="display:inline-block;width:24px;height:14px;background:repeating-linear-gradient(45deg,#CB454A 0px,#CB454A 8.5px,#24589A 8.5px,#24589A 10px);margin-right:8px"></span>D to R flip<br>',
    '<span style="display:inline-block;width:24px;height:14px;background:#CB454A;margin-right:8px"></span>R hold<br>',
    '<span style="display:inline-block;width:24px;border-top:2px dashed #333;margin-right:8px;vertical-align:middle"></span>Provisional (uncalled)',
    '</div>'
)

statewide_outcome_map <- function() {
    map <- leaflet::leaflet(options = leaflet::leafletOptions(preferCanvas = FALSE),
                            height = 650) |>
        leaflet::addProviderTiles("OpenStreetMap",
                                  options = leaflet::providerTileOptions(opacity = 0.4)) |>
        leaflet::addPolygons(data = state_outline, fill = FALSE,
                             color = "#777777", weight = 1,
                             options = leaflet::pathOptions(interactive = FALSE))
    for (chamber_name in c("House", "Senate")) {
        data <- if (chamber_name == "House") house_outcomes else senate_outcomes
        map <- map |>
            leaflet::addPolygons(
                data = data, group = chamber_name, layerId = ~target_id,
                fillColor = ~fill_color, fillOpacity = 0.85,
                color = "#333333", weight = 1.2, dashArray = ~border_dash,
                label = ~hover, popup = ~popup,
                options = leaflet::pathOptions(className = ~outcome_class),
                highlightOptions = leaflet::highlightOptions(weight = 3,
                                                              bringToFront = TRUE))
    }
    map |>
        leaflet::hideGroup("Senate") |>
        leaflet::addLayersControl(baseGroups = c("House", "Senate"),
                                   options = leaflet::layersControlOptions(collapsed = FALSE)) |>
        leaflet::addControl(html = outcome_legend, position = "bottomright") |>
        leaflet::fitBounds(state_bounds[["xmin"]], state_bounds[["ymin"]],
                           state_bounds[["xmax"]], state_bounds[["ymax"]]) |>
        htmlwidgets::onRender(paste(readLines("_outcome-patterns.js"), collapse = "\n"))
}
