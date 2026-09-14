"""Extract and classify every external resource referenced by the archive posts.

Task 1.3 of the port-blogspot-archive change. Reads feed.json, writes resources.csv.
"""
import csv
import html
import json
import re
from pathlib import Path

from build_manifest import permalink, slugify

HERE = Path(__file__).parent

# (src|href)="..." plus the attribute name, so an <img src> is distinguishable
# from an <a href> pointing at the same host.
ATTR_RE = re.compile(r'\b(src|href)\s*=\s*"([^"]+)"', re.IGNORECASE)

IMAGE_HOSTS = ("i.imgur.com", "blogger.googleusercontent.com", "bp.blogspot.com")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def classify(url, attr):
    """Bucket a URL into the categories the spec's manifest requirement names."""
    low = url.lower()
    if "fusiontable" in low:
        return "fusion-table"
    if "docs.google.com/spreadsheet" in low or "spreadsheets/d/" in low:
        return "google-sheet"
    if any(h in low for h in IMAGE_HOSTS) or low.split("?")[0].endswith(IMAGE_EXTS):
        return "image"
    if attr == "src":
        return "other-embed"
    return "outbound-link"


def main():
    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    rows = []
    for entry in feed["entry"]:
        title = entry["title"]["$t"]
        post_date = entry["published"]["$t"][:10]
        slug = slugify(title)[:60].strip("-")
        body = entry["content"]["$t"]
        seen = set()
        for attr, raw in ATTR_RE.findall(body):
            url = html.unescape(raw).strip()
            if not url.startswith("http"):
                continue
            key = (attr.lower(), url)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "post_date": post_date,
                "post_slug": slug,
                "post_permalink": permalink(entry),
                "attr": attr.lower(),
                "kind": classify(url, attr.lower()),
                "url": url,
                "host": re.sub(r"^https?://", "", url).split("/")[0],
                # 1.4 fills these in.
                "http_status": "",
                "content_length": "",
                "checked_date": "",
                "note": "",
            })

    out = HERE / "resources.csv"
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")

    for kind in ("image", "fusion-table", "google-sheet", "other-embed", "outbound-link"):
        sub = [r for r in rows if r["kind"] == kind]
        print(f"  {kind:16} rows={len(sub):4}  unique={len({r['url'] for r in sub}):4}  posts={len({r['post_slug'] for r in sub}):3}")

    imgur = {r["url"] for r in rows if "i.imgur.com" in r["url"]}
    ft = {r["url"] for r in rows if r["kind"] == "fusion-table"}
    ft_posts = {r["post_slug"] for r in rows if r["kind"] == "fusion-table"}
    print(f"\nimgur unique: {len(imgur)}")
    print(f"fusion-table unique: {len(ft)} across {len(ft_posts)} posts")


if __name__ == "__main__":
    main()
