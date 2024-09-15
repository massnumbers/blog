library(tidyverse)

party_abbrev <- function(party) {
    case_when(
        party == "Democratic" ~ "D",
        party == "Republican" ~ "R",
        party == "Libertarian" ~ "L",
        party == "Green-Rainbow" ~ "GR",
        party == "Green" ~ "G",
        party == "United Independent" ~ "UI",
        TRUE ~ "Other",
    )
}

res <- read_csv("../../_data/2024/ma_2024_09_03_results.csv") %>%
    mutate(party_abbrev = party_abbrev(party),
           display_name = str_glue("{first_name} {last_name} ({party_abbrev}-{city_town})")) %>%
    filter(num_candidates > 1)
