# Recovered data for map reconstruction

Fetched 2026-10-15 for tasks 7.1-7.2 of migrate-blogspot-archive. Read-only
copies; the prose-agreement verdict for each map is in `../fusion_tables.csv`.

Google Sheets linked from the original posts (CSV export of the first tab):

| file | sheet key | linked from |
|---|---|---|
| sheet_2012-11-15_town_ranking.csv | 0AkWPTnj-k6-kdDJ1a1EzT2VSdllabXZEZ2xVeXFxdWc | 2012-11-15 |
| sheet_2012-11-18_house_ranking.csv | 0AkWPTnj-k6-kdHU4dEo1ZzZENHlkQ1dleU9SOU1SNnc | 2012-11-18 |
| sheet_2013-01-31_district_towns.csv | 0AkWPTnj-k6-kdEE5SjRIcEE5Y3cycUMybDF1WlRWbXc | 2013-01-31 |
| sheet_2013-01-31_town_votes.csv | 0AkWPTnj-k6-kdG5Xci1CWmQ3bDV3TFdlRXk5eVRmcmc | 2013-01-31 |
| sheet_2014-05-27_state_rep_ranking.csv | 13y5sVnaJJsh87Gyo9qoIjkTuhieQ9odle0_PvY1f0OE | 2014-05-27 |
| sheet_2014-05-27_contested_races.csv | 1-1Mj3U1SwZvIkXKCM_0eyLwnkz7-DqDhVOggROxwZ50 | 2014-05-27 |

Sheet exports carry the sheet's display formatting, so percentages are rounded
as they were shown (whole points in the 2012-2013 town sheets).

electionstats.state.ma.us downloads (`/elections/download/<id>/precincts_include:0|1/`):

| file | election id |
|---|---|
| electionstats_104711_senate_special_2010_towns.csv | 104711, 2010 US Senate special, by town |
| electionstats_112702_senate_2012_towns.csv | 112702, 2012 US Senate, by town |
| electionstats_104457_president_2008_precincts.csv | 104457, 2008 President, by precinct |
| electionstats_112698_president_2012_precincts.csv | 112698, 2012 President, by precinct |

Known defect: in 112698, Easton precinct 1 records Obama 15 and Stein 633, an
apparent column error.
