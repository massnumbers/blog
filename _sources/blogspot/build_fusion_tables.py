"""Parse what survives inside the dead Fusion Tables embed URLs.

Task 2.2 of the port-blogspot-archive change. The embeds render nothing, but the
URLs still carry the table ID, the selected geometry column, and the map's
center/zoom -- enough to say what each map framed. Writes fusion_tables.csv, the
file that later tasks annotate with recovery status and fidelity tier.
"""
import csv
import html
import re
import urllib.parse
from pathlib import Path

HERE = Path(__file__).parent


def parse_embed(url, attr):
    """Pull table id, selected column, and viewport out of a Fusion Tables URL.

    Two shapes appear in the archive and they are not equivalent:
      * embedviz?q=select+colN+from+<id>  -- an iframe that rendered a live map
      * DataSource|data?docid=<id>        -- an <a> link to the table itself
    Only the first was ever a map on the page; the second is a citation whose
    target is gone. They earn different fidelity treatment, so record which.
    """
    url = html.unescape(url)
    parts = urllib.parse.urlparse(url)
    field = {k: v[0] for k, v in urllib.parse.parse_qs(parts.query).items()}

    table_id, column = "", ""
    query = field.get("q", "")
    m = re.search(r"select\s+(\S+)\s+from\s+(\S+)", query, re.IGNORECASE)
    if m:
        column, table_id = m.group(1), m.group(2)
    elif query:
        m = re.search(r"\bfrom\s+(\S+)", query, re.IGNORECASE)
        if m:
            table_id = m.group(1)
    if not table_id:
        table_id = field.get("docid", "")

    if "embedviz" in parts.path or attr == "src":
        embed_kind = "map-embed"
    elif table_id:
        embed_kind = "table-link"
    else:
        embed_kind = "other"

    return {
        "embed_kind": embed_kind,
        "table_id": table_id,
        "geometry_column": column,
        "lat": field.get("lat", ""),
        "lng": field.get("lng", ""),
        "zoom": field.get("z", field.get("zoom", "")),
        "viz": field.get("viz", ""),
    }


def main():
    rows = list(csv.DictReader((HERE / "resources.csv").open()))
    # A link to the Fusion Tables project site is not a reference to a table.
    embeds = [r for r in rows if r["kind"] == "fusion-table"
              and "sites.google.com" not in r["url"]]

    out_rows = []
    for r in embeds:
        parsed = parse_embed(r["url"], r["attr"])
        out_rows.append({
            "post_date": r["post_date"],
            "post_slug": r["post_slug"],
            "post_permalink": r["post_permalink"],
            "embed_url": r["url"],
            "http_status": r["http_status"],
            **parsed,
            # 2.1 / 2.3 / 2.4 / 2.6 fill these in.
            "drive_archive_found": "",
            "local_equivalent": "",
            "external_source": "",
            "external_granularity": "",
            "fidelity_tier": "",
            "justification": "",
        })

    out_rows.sort(key=lambda r: (r["post_date"], r["embed_url"]))
    out = HERE / "fusion_tables.csv"
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote {out} ({len(out_rows)} rows)")

    import collections
    print(f"unique urls    : {len({r['embed_url'] for r in out_rows})}")
    print(f"unique tables  : {len({r['table_id'] for r in out_rows if r['table_id']})}")
    print(f"posts          : {len({r['post_slug'] for r in out_rows})}")
    for kind, n in collections.Counter(r["embed_kind"] for r in out_rows).items():
        sub = [r for r in out_rows if r["embed_kind"] == kind]
        print(f"  {kind:12} rows={n:3}  tables={len({r['table_id'] for r in sub}):3}"
              f"  posts={len({r['post_slug'] for r in sub}):3}")

    missing_id = [r for r in out_rows if not r["table_id"]]
    print(f"rows with no recoverable table id: {len(missing_id)}")
    for r in missing_id:
        print(f"   {r['post_date']} {r['embed_url'][:110]}")
    no_geo = [r for r in out_rows if r["embed_kind"] == "map-embed" and not r["geometry_column"]]
    print(f"map-embeds with no geometry column: {len(no_geo)}")


if __name__ == "__main__":
    main()
