# Static 9th Essex municipal PVI map used as the post thumbnail and social
# card image. Mirrors district_muni_map() in index.qmd, drawn in tmap's plot
# mode with an OpenStreetMap basemap. Run from the repository root:
#
#   Rscript posts/2026-10-29-contested-races/_make_thumbnail.R

library(tidyverse)
library(sf)
library(tmap)

post_dir <- "posts/2026-10-29-contested-races"
out_file <- "images/ninth-essex-muni-pvi-2026.png"
district_name <- "Ninth Essex"

US_Harris_24 <- 75017626
US_Trump_24 <- 77301997
US_Biden_20 <- 81281502
US_Trump_20 <- 74222593

US_PVI_24 <- (US_Harris_24 + US_Biden_20) /
    (US_Harris_24 + US_Trump_24 + US_Biden_20 + US_Trump_20)

pvi_string <- function(pvi_n) {
    case_when(
        pvi_n <= -0.5 ~ str_c("R+", round(abs(pvi_n))),
        pvi_n >= 0.5 ~ str_c("D+", round(pvi_n)),
        TRUE ~ "EVEN"
    )
}

muni_votes <- read_csv(file.path(post_dir, "ma_precincts_districts_pres_2024.csv"),
                       show_col_types = FALSE) |>
    filter(State_Rep == district_name) |>
    group_by(city_town) |>
    summarize(dem = sum(Harris_24 + Biden_20),
              gop = sum(Trump_24 + Trump_20)) |>
    mutate(PVI_N = (dem / (dem + gop) - US_PVI_24) * 100,
           PVI = pvi_string(PVI_N),
           label = str_glue("{city_town}\n{PVI}"))

muni_pvi <- read_sf("_gis/ma_wards_precincts_w_subs.geojson") |>
    filter(State_Rep == district_name) |>
    group_by(city_town) |>
    summarize() |>
    st_simplify(dTolerance = 10) |>
    inner_join(muni_votes, by = "city_town")

district_pvi <- pvi_string((sum(muni_votes$dem) /
                            sum(muni_votes$dem + muni_votes$gop) - US_PVI_24) * 100)

#' Pad a bounding box out to a width:height ratio so the basemap fills the
#' whole image instead of leaving blank bands beside a tall district.
pad_bbox <- function(bb, aspect) {
    w <- bb[["xmax"]] - bb[["xmin"]]
    h <- bb[["ymax"]] - bb[["ymin"]]
    cx <- (bb[["xmax"]] + bb[["xmin"]]) / 2
    cy <- (bb[["ymax"]] + bb[["ymin"]]) / 2
    if (w / h < aspect) w <- h * aspect else h <- w / aspect
    bb[c("xmin", "xmax", "ymin", "ymax")] <- c(cx - w / 2, cx + w / 2,
                                               cy - h / 2, cy + h / 2)
    bb
}

map_bbox <- muni_pvi |>
    st_buffer(800) |>
    st_bbox() |>
    pad_bbox(aspect = 1200 / 740)

tmap_mode("plot")

thumbnail <- tm_shape(muni_pvi, bbox = map_bbox) +
    tm_basemap("OpenStreetMap") +
    tm_polygons(
        fill = "PVI_N",
        fill.scale = tm_scale_continuous(
            values = c("#FF4949", "white", "#0F4392"),
            limits = c(-20, 20),
            midpoint = 0,
            outliers.trunc = c(TRUE, TRUE)
        ),
        fill.legend = tm_legend_hide(),
        fill_alpha = 0.7,
        col = "black",
        lwd = 2
    ) +
    tm_text("label", size = 1.6, fontface = "bold") +
    tm_title(str_glue("State Representative - 9th Essex ({district_pvi})"),
             size = 1.6) +
    tm_credits("© OpenStreetMap contributors", position = c("right", "bottom")) +
    tm_layout(frame = FALSE, inner.margins = c(0, 0, 0, 0),
              outer.margins = c(0, 0, 0, 0))

tmap_save(thumbnail, out_file, width = 1200, height = 800, dpi = 120)

# Quantize to a 128-colour palette (ImageMagick) to keep the card small.
system2("magick", c(out_file, "-colors", "128", str_c("PNG8:", out_file)))
