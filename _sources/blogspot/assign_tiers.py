"""Assign a provisional fidelity tier to every Fusion Tables reference.

Task 2.6 of the port-blogspot-archive change.

The decisive fact, found in task 3.1: most of these maps were published as a
static screenshot wrapped in a link to the interactive version. Where that
screenshot survives -- and all of them do, downloaded in task 1.5 -- tier 2 is
not a degraded fallback but the most faithful option available: it is exactly
the image the original reader saw. A 2026 reconstruction from re-sourced data
would look different from the published post and would carry a disclosure
burden, so tier 1 is reserved for references where no screenshot survives.
"""
import csv
import html
import json
import re
from pathlib import Path

from build_manifest import permalink

HERE = Path(__file__).parent

# Map subjects whose artifact was a bespoke derivation or a poll, where the
# inputs alone do not reproduce the published map.
NOT_REPRODUCIBLE = {"poll-crosstab", "derived-projection", "candidate-roster", "external-dataset"}


def screenshot_links(feed):
    """URLs referenced as <a href=fusion> wrapping an <img> -- i.e. the map was
    published as a still image that linked out to the interactive version."""
    linked = set()
    for entry in feed["entry"]:
        body = entry["content"]["$t"]
        # The image is often not the anchor's only child -- a bold caption and a
        # <br/> commonly sit inside the same link -- so match any <img> within.
        for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', body, re.S | re.I):
            href = re.search(r'href\s*=\s*"([^"]+)"', m.group(1), re.I)
            if href and "fusiontable" in href.group(1).lower() and "<img" in m.group(2).lower():
                linked.add(html.unescape(href.group(1)))
    return linked


def main():
    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    linked = screenshot_links(feed)
    rows = list(csv.DictReader((HERE / "fusion_tables.csv").open()))

    for row in rows:
        has_shot = row["embed_url"] in linked
        local_attr = row["local_equivalent"] not in ("none", "")
        local_geom = row["local_geometry"] not in ("none", "")
        reproducible = row["data_class"] not in NOT_REPRODUCIBLE

        row["screenshot_survives"] = "yes" if has_shot else "no"

        if row["embed_kind"] == "table-link":
            row["fidelity_tier"] = "3-declared-missing"
            row["justification"] = ("text link to the table itself, not a map; the link target "
                                    "is deleted so the citation is noted rather than linked")
        elif has_shot:
            row["fidelity_tier"] = "2-static"
            row["justification"] = ("the published map was a still image linking to the "
                                    "interactive version; that image is preserved locally, so "
                                    "it shows exactly what the original reader saw")
        elif local_attr and local_geom and reproducible:
            row["fidelity_tier"] = "1-reconstructed"
            row["justification"] = (f"no screenshot survives, but geometry and attributes are "
                                    f"local ({row['data_class']}); rebuildable with disclosure")
        elif row["external_source"] and reproducible:
            row["fidelity_tier"] = "1-reconstructed-external"
            row["justification"] = ("no screenshot survives; rebuildable only after fetching "
                                    f"data from {row['external_source'][:60]}")
        else:
            row["fidelity_tier"] = "3-declared-missing"
            row["justification"] = (f"no screenshot survives and the map was a {row['data_class']}, "
                                    "which its inputs alone do not reproduce")

    with (HERE / "fusion_tables.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    import collections
    print(f"rows: {len(rows)}   all tiered: {all(r['fidelity_tier'] for r in rows)}")
    print(f"all justified: {all(r['justification'] for r in rows)}\n")
    for tier, n in sorted(collections.Counter(r["fidelity_tier"] for r in rows).items()):
        posts = len({r["post_slug"] for r in rows if r["fidelity_tier"] == tier})
        print(f"  {tier:26} rows={n:3}  posts={posts:3}")

    print("\nper post, the highest-effort tier it contains:")
    order = {"2-static": 0, "3-declared-missing": 1, "1-reconstructed": 2, "1-reconstructed-external": 3}
    worst = {}
    for r in rows:
        s = r["post_slug"]
        if s not in worst or order[r["fidelity_tier"]] > order[worst[s]]:
            worst[s] = r["fidelity_tier"]
    for tier, n in sorted(collections.Counter(worst.values()).items()):
        print(f"  {tier:26} {n:3} posts")


if __name__ == "__main__":
    main()
