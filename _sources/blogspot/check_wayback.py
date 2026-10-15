"""Test whether any Wayback snapshot of a map post contains a rendered map.

Task 2.5 of the port-blogspot-archive change. Tier 2 (static image of the
original map) is only available if a snapshot actually captured map pixels, so
this checks rather than assumes. Two things are tested per post: whether a
snapshot exists at all, and whether the archived HTML carries anything more
than the dead iframe URL.
"""
import csv
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "Mozilla/5.0 (compatible; massnumbers-archive-audit/1.0)"
CDX = ("http://web.archive.org/cdx/search/cdx?url={url}&output=json"
       "&fl=timestamp,statuscode&filter=statuscode:200&limit=8")


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def main():
    rows = list(csv.DictReader((HERE / "fusion_tables.csv").open()))
    posts = []
    for r in rows:
        if r["embed_kind"] == "map-embed" and r["post_permalink"] not in [p[0] for p in posts]:
            posts.append((r["post_permalink"], r["post_date"]))
    posts = posts[:8]  # task asks for at least 5

    results = []
    for url, date in posts:
        bare = re.sub(r"^https?://", "", url)
        try:
            data = get(CDX.format(url=urllib.parse.quote(bare, safe="")))
        except Exception as exc:
            results.append({"post_date": date, "post_url": url, "snapshots": "ERR",
                            "snapshot_used": "", "iframe_present": "", "map_image_present": "",
                            "verdict": f"cdx error: {type(exc).__name__}"})
            continue

        import json
        rowsj = json.loads(data) if data.strip() else []
        stamps = [r[0] for r in rowsj[1:]] if len(rowsj) > 1 else []
        if not stamps:
            results.append({"post_date": date, "post_url": url, "snapshots": 0,
                            "snapshot_used": "", "iframe_present": "", "map_image_present": "",
                            "verdict": "no snapshot"})
            continue

        stamp = stamps[-1]
        snap_url = f"http://web.archive.org/web/{stamp}/{url}"
        try:
            html = get(snap_url, timeout=90)
        except Exception as exc:
            results.append({"post_date": date, "post_url": url, "snapshots": len(stamps),
                            "snapshot_used": stamp, "iframe_present": "", "map_image_present": "",
                            "verdict": f"fetch error: {type(exc).__name__}"})
            continue

        iframe = bool(re.search(r"fusiontables[^\"']*embedviz", html, re.I))
        # A captured map would appear as archived Google map tiles or a
        # fusiontables-served image, not just the iframe URL.
        tiles = bool(re.search(r"web\.archive\.org/web/\d+i?m?_?/[^\"']*(mt\d\.google|maps\.g"
                              r"static|khms\d|fusiontables[^\"']*\.png)", html, re.I))
        results.append({
            "post_date": date, "post_url": url, "snapshots": len(stamps),
            "snapshot_used": stamp, "iframe_present": iframe, "map_image_present": tiles,
            "verdict": "map tiles archived" if tiles else
                       ("iframe url only - no rendered map" if iframe else "no map markup"),
        })
        print(f"  {date}  snaps={len(stamps):2}  iframe={iframe}  tiles={tiles}  {results[-1]['verdict']}")
        time.sleep(2)

    out = HERE / "wayback_check.csv"
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    with_tiles = [r for r in results if r["map_image_present"] is True]
    print(f"\nposts checked        : {len(results)}")
    print(f"with any snapshot    : {len([r for r in results if r['snapshots'] not in (0, 'ERR')])}")
    print(f"with rendered map    : {len(with_tiles)}")
    print(f"VERDICT: tier 2 from Wayback is "
          f"{'AVAILABLE' if with_tiles else 'NOT AVAILABLE'}")


if __name__ == "__main__":
    import urllib.parse
    main()
