"""Build the per-post manifest from the saved Blogger Atom feed.

Task 1.2 of the port-blogspot-archive change. Reads feed.json, writes manifest.csv.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent


def slugify(title):
    """Kebab-case slug from a post title, matching the posts/ naming convention."""
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-+", "-", s)


def permalink(entry):
    for link in entry.get("link", []):
        if link.get("rel") == "alternate":
            return link["href"]
    return ""


def main():
    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    rows = []
    for entry in feed["entry"]:
        title = entry["title"]["$t"]
        url = permalink(entry)
        body = entry["content"]["$t"]
        rows.append({
            "date": entry["published"]["$t"][:10],
            "title": title,
            "labels": "|".join(sorted(c["term"] for c in entry.get("category", []))),
            "permalink": url,
            "blogger_path": url.split("massnumbers.blogspot.com")[-1] if url else "",
            "slug": slugify(title)[:60].strip("-"),
            "body_chars": len(body),
            "comments": entry.get("thr$total", {}).get("$t", "0"),
        })
    rows.sort(key=lambda r: r["date"])

    # site_dir and port_status are maintained by hand and by the porting
    # scripts; carry them over so a rebuild from the feed does not lose them.
    out = HERE / "manifest.csv"
    if out.exists():
        kept = {r["permalink"]: r for r in csv.DictReader(out.open())}
        for row in rows:
            old = kept.get(row["permalink"], {})
            row["site_dir"] = old.get("site_dir", "")
            row["port_status"] = old.get("port_status", "pending")
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")

    dupes = {r["slug"] for r in rows if sum(x["slug"] == r["slug"] for x in rows) > 1}
    print(f"date range: {rows[0]['date']} .. {rows[-1]['date']}")
    print(f"duplicate slugs: {sorted(dupes) if dupes else 'none'}")


if __name__ == "__main__":
    main()
