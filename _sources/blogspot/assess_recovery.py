"""Assess, per Fusion Table, what data survives to rebuild its map.

Tasks 2.3 and 2.4 of the port-blogspot-archive change. Two separate questions
per table:
  * is there an equivalent dataset already in this repo or in mapoli? (2.3)
  * if not, does electionstats.state.ma.us publish the underlying results? (2.4)

Geometry and attributes are tracked separately: every map needs both, and for
several of these maps the boundaries survive locally while the numbers do not.
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent
BLOG = HERE.parent.parent
MAPOLI = Path("/Users/bwb/src/github.com/bwbensonjr/mapoli")

# Local candidates, verified to exist before any table is allowed to claim one.
LOCAL = {
    "pres-muni": ["_data/2023/ma_pres_results_2008.csv", "_data/2023/ma_pres_results_2012.csv",
                  "_data/2023/ma_pres_results_2016.csv"],
    "pres-precinct-12-16": ["@mapoli/pvi/ma_precincts_districts_12_16_pres.csv"],
    "leg-pvi": ["_data/2020/ma_leg_two_party_2008_2021_pvi.csv"],
    "pvi-2016": ["@mapoli/pvi/ma_precinct_pvi_2016.csv", "@mapoli/pvi/ma_city_town_pvi_2016.csv"],
    "geom-dist-2012": ["_gis/house2012/HOUSE2012_POLY.shp", "_gis/senate2012/SENATE2012_POLY.shp"],
    "geom-precinct": ["_gis/ma_wards_precincts_w_subs.geojson"],
    "geom-boston-nbhd": ["_gis/Boston_Neighborhoods.geojson"],
    "geom-town": ["_gis/townssurvey_shp/TOWNSSURVEY_POLYM.shp"],
}

ES = "https://electionstats.state.ma.us"

# Per table: which local bundles apply, and what is still missing.
# "attr" = the numbers the map coloured by; "geom" = the boundaries it drew.
ASSESS = {
    # --- statewide municipal election results ---
    "1imKtQ0D7zJNbECIauYmRy4Ze-5o1u5r0yHZ469Y": ("geom-town", "none",
        "2012 US Senate (Warren/Brown) municipal results not held locally",
        f"{ES}/elections/download/112702/precincts_include:0/", "municipality"),
    "1dTQlxPkO94dd5lxE5sL6Fs6D66XF5Bkxhjn4bfQ": ("geom-town", "none",
        "2013 Senate special (Markey) municipal results not held locally",
        f"{ES}/elections/download/124797/precincts_include:0/", "municipality"),
    "1JX4TSP6eXnppTimtyQY5l3YFgIuVBAAOsY13EwKU": ("geom-town", "pres-muni",
        "fully local: 2008 and 2016 presidential by municipality", "", ""),
    "1Kfs4Y1IpoPsQhC7SQdHkpItDvSMCx_Sx0hfnPuM": ("geom-town", "pres-muni",
        "presidential years local; the 2006-2012 Gov and Senate races in the average are not",
        f"{ES}/elections/search/", "municipality"),
    # --- district-level partisan rankings ---
    "1Tz0rWIHm5ICHujtja2FoRkDP1iru5GI70GdgbAE": ("geom-dist-2012", "leg-pvi",
        "2012-era House geometry and 2008+ district PVI both local", "", ""),
    "13ktkhgEIon7fxqIC0BNzgnaktvIhQgwyKwPGK0mU": ("geom-dist-2012", "leg-pvi",
        "2012-era House geometry and 2008+ district PVI both local", "", ""),
    "1_mq12Ew1dCwkw0TamHKnlCePGXet2ZdhBAliNag": ("none", "pvi-2016",
        "congressional PVI local for 2016; no 2012-era congressional geometry in _gis",
        f"{ES}/elections/search/", "municipality"),
    "1Wmf2piOPp2qAEXXPxGacn2QnvpabE8xP6c0r4Nds": ("geom-dist-2012", "none",
        "2014 Senate candidate roster was hand-compiled; no dataset holds it",
        f"{ES}/elections/search/", "district"),
    # --- district geometry illustrations ---
    "1X-Atx72YsyPZ5_C9SFy0rvofN0NhupPL-chxkyI": ("geom-dist-2012", "n/a",
        "pure geometry map; 2012-era House shapefile is local", "", ""),
    "1yOfQUuUmGW_JmBJ0xQoXg7rzvuQts_Aw-WmOdz8": ("geom-dist-2012", "n/a",
        "pure geometry map; 2012-era Senate shapefile is local", "", ""),
    "1zBfjVCB16qdkMFnlt6fufIChTYpF1-TnEsgYe_k": ("geom-dist-2012", "n/a",
        "pure geometry overlay of candidate House districts", "", ""),
    "1IR8sygpAf7DXpzZhseYrfyDd6UVRIOrIGxmkSUw": ("geom-dist-2012", "n/a",
        "pure geometry overlay of Senate and House districts", "", ""),
    "1oY4dYL_lXUnfAXKiCwjF8sfNbMQYmCeQVziiMQLf": ("geom-dist-2012", "n/a",
        "pure geometry map of the 5th Middlesex", "", ""),
    # --- precinct election results ---
    "13z7T3CzHv8KRbT3z9Wi52-imSmuXOom3T2yr2Zc": ("geom-precinct", "none",
        "2013 First Suffolk primary precinct results came from the Dorchester Reporter, not an official file",
        f"{ES}/elections/search/", "precinct"),
    "1BI83pCOR9B072Qer33AP0Tw4yHOmRRAm6Cf23aw": ("geom-precinct", "none",
        "backing table for the same First Suffolk race", f"{ES}/elections/search/", "precinct"),
    "132ioBeYzVhxw8zANa2yH_DWPpPdiUi88Iu2HeVI": ("geom-precinct", "none",
        "16th Worcester precinct results not held locally", f"{ES}/elections/search/", "precinct"),
    "1xc1aAZKOXSe46ws8Wlrk45gt9c6cYyWpIngdLVQ": ("geom-precinct", "none",
        "16th Worcester precinct results not held locally", f"{ES}/elections/search/", "precinct"),
    "18TEI8WNtnyADNPzpoY2SpTc-QQDo05JSDz24o2o": ("geom-precinct", "none",
        "2013 Boston mayoral preliminary is a municipal election; not in electionstats state files",
        "City of Boston Elections Department", "boston-precinct"),
    "1JoDSYF7vaRjk86TvUDL5aiu_h14pIBKXdhkK7JE": ("geom-precinct", "none",
        "backing table for the 2013 Boston mayoral map",
        "City of Boston Elections Department", "boston-precinct"),
    "17y_Yh1_nIZndtIG49JHMg9U4oErs7eZszZnbmhHm": ("geom-boston-nbhd", "none",
        "2017 Boston mayoral preliminary by neighborhood; municipal election",
        "City of Boston Elections Department", "boston-neighborhood"),
    "15uNiS9zskaKiIMzGde-igYLMVdBxI_cWhgtaMnZo": ("geom-precinct", "none",
        "2017 Boston mayoral preliminary by precinct; municipal election",
        "City of Boston Elections Department", "boston-precinct"),
    "145mKZ1F1X2wpH6QCbfTlVz9y8b-QAehZkVaTN6c": ("geom-town", "none",
        "2nd Hampden and Hampshire profile built from pre-2016 results",
        f"{ES}/elections/search/", "municipality"),
    # --- PVI-style precinct indices ---
    "1JxPgasJNST0QetCcXhobS2Wf5kwwSWyjXBlWxjZI": ("geom-precinct", "pvi-2016",
        "precinct PVI method reproducible from local 2016 PVI, but the 2015 vintage differs", "", ""),
    "12fUG7DAFn6PfjpEBQfl6sQ0t7CO3Xc07egI-lAr5": ("geom-precinct", "pvi-2016",
        "precinct PVI reproducible from local 2016 PVI files", "", ""),
    "1rRB6uJLalsHCY7R1ZM9kfHmIkj1MaS3zMZUufFLg": ("geom-precinct", "pvi-2016",
        "precinct PVI reproducible from local 2016 PVI files", "", ""),
    "1XMhXwkKl9Bm6Zm8mtKFSNEUOJ52r9Zxtb2xnetmC": ("geom-precinct", "pvi-2016",
        "precinct PVI reproducible from local 2016 PVI files", "", ""),
    "1XszEjZQhUWsTh3eAa3JI-7CtoXQOZIrAGWLO9Z29": ("geom-town", "pvi-2016",
        "3rd Congressional municipal profile reproducible from local PVI", "", ""),
    # --- derived projections: the derivation is the artifact ---
    "1vReKtagR3HCDjZEVBt0alFfkDxYYmHh5qkepNyhd": ("geom-precinct", "pres-precinct-12-16",
        "Obama 2012 precinct inputs are local, but the 2008-to-2012 projection method was bespoke",
        "", ""),
    "1Jojf7fbpaH8vWBXGNluBo2IVB2SQZFjbEv9Md6C_": ("geom-precinct", "pres-precinct-12-16",
        "projection inputs local; April 2014 special precinct results are not",
        f"{ES}/elections/search/", "precinct"),
    # --- not election data at all ---
    "1LS40Q6GOSh_1WPiow1vnCMFpvdOGLdu2ZlKMwA4": ("geom-precinct", "none",
        "Suffolk University poll ward crosstabs; no election dataset can reproduce a poll",
        "Suffolk University Political Research Center release", "boston-ward"),
    "1srQkE8-DjAGYBng46q8l1vC_Mj1K2-Zm6tkBVts": ("geom-precinct", "none",
        "Suffolk University poll ward crosstabs; no election dataset can reproduce a poll",
        "Suffolk University Political Research Center release", "boston-ward"),
    "1eYCAStq8erHv6l80rj4uNW5YimCl2RYslIeuf7MU": ("none", "none",
        "tornado history by county; not election data",
        "NOAA Storm Prediction Center severe weather database", "county"),
}


def verify_local():
    """Refuse to credit a local bundle whose files are not actually present."""
    ok = {}
    for key, files in LOCAL.items():
        resolved = []
        for f in files:
            path = MAPOLI / f[8:] if f.startswith("@mapoli/") else BLOG / f
            if path.exists():
                resolved.append(f)
            else:
                print(f"  MISSING {f}")
        ok[key] = resolved
    return ok


def main():
    print("verifying local data bundles...")
    local_ok = verify_local()
    for key, files in local_ok.items():
        print(f"  {key:22} {len(files)} file(s)")

    subjects = {r["table_id"]: r for r in csv.DictReader((HERE / "table_subjects.csv").open())}
    rows = list(csv.DictReader((HERE / "fusion_tables.csv").open()))

    for row in rows:
        tid = row["table_id"]
        subj = subjects.get(tid, {})
        geom_key, attr_key, note, ext_src, ext_gran = ASSESS[tid]

        geom = "; ".join(local_ok.get(geom_key, [])) if geom_key not in ("none", "n/a") else geom_key
        attr = "; ".join(local_ok.get(attr_key, [])) if attr_key not in ("none", "n/a") else attr_key

        row["subject"] = subj.get("subject", "")
        row["data_class"] = subj.get("data_class", "")
        row["geography"] = subj.get("geography", "")
        row["local_geometry"] = geom
        row["local_equivalent"] = attr
        row["local_note"] = note
        row["external_source"] = ext_src
        row["external_granularity"] = ext_gran

    fields = list(rows[0])
    with (HERE / "fusion_tables.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    tables = {r["table_id"]: r for r in rows}
    print(f"\nassessed {len(tables)} unique tables across {len(rows)} rows")
    full = [r for r in tables.values() if r["local_equivalent"] not in ("none", "")
            and r["local_geometry"] not in ("none", "")]
    attr_gap = [r for r in tables.values() if r["local_equivalent"] == "none"]
    has_ext = [r for r in attr_gap if r["external_source"]]
    print(f"  attributes + geometry local : {len(full)}")
    print(f"  attribute gap               : {len(attr_gap)}")
    print(f"    of which an external source is identified: {len(has_ext)}")
    print(f"  no source anywhere          : {len([r for r in attr_gap if not r['external_source']])}")


if __name__ == "__main__":
    main()
