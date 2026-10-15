"""Record an HTTP status and check date for every resource row.

Task 1.4 of the port-blogspot-archive change. Updates resources.csv in place.
Imgur serves a known placeholder for removed images, so an image row is only
treated as live if it returns a real image body.
"""
import csv
import datetime
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
UA = "Mozilla/5.0 (compatible; massnumbers-archive-audit/1.0)"
TIMEOUT = 30

# imgur's "image removed" placeholder is a small fixed GIF/PNG served with a 200.
IMGUR_PLACEHOLDER_MAX = 1000


def check(row):
    url = row["url"]
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read()
            row["http_status"] = str(resp.status)
            row["content_length"] = str(len(body))
            row["final_url"] = resp.geturl()
            note = []
            if row["kind"] == "image":
                if len(body) <= IMGUR_PLACEHOLDER_MAX:
                    note.append("SUSPECT-PLACEHOLDER")
                if not body[:8].startswith((b"\x89PNG", b"\xff\xd8", b"GIF8", b"RIFF", b"<svg", b"<?xml")):
                    note.append("NOT-AN-IMAGE")
            if "removed" in resp.geturl() or "/error" in resp.geturl():
                note.append("REDIRECT-TO-ERROR")
            if row["kind"] == "fusion-table":
                note.append("DEAD-SERVICE")
            row["note"] = ";".join(note)
    except urllib.error.HTTPError as exc:
        row["http_status"] = str(exc.code)
        row["content_length"] = ""
        row["final_url"] = url
        row["note"] = f"HTTPError {exc.reason}"
    except Exception as exc:  # DNS failures, timeouts, TLS errors
        row["http_status"] = "ERR"
        row["content_length"] = ""
        row["final_url"] = url
        row["note"] = f"{type(exc).__name__}: {exc}"[:120]
    row["checked_date"] = datetime.date.today().isoformat()
    return row


def main():
    path = HERE / "resources.csv"
    rows = list(csv.DictReader(path.open()))
    for row in rows:
        row.setdefault("final_url", "")

    with ThreadPoolExecutor(max_workers=12) as pool:
        rows = list(pool.map(check, rows))

    fields = [f for f in rows[0] if f != "final_url"] + ["final_url"]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    unchecked = [r for r in rows if not r["http_status"] or not r["checked_date"]]
    print(f"checked {len(rows)} rows; unchecked: {len(unchecked)}")

    import collections
    for kind in sorted({r["kind"] for r in rows}):
        sub = [r for r in rows if r["kind"] == kind]
        codes = collections.Counter(r["http_status"] for r in sub)
        print(f"  {kind:16} {dict(codes)}")

    flagged = [r for r in rows if r["kind"] == "image" and
               ("SUSPECT-PLACEHOLDER" in r["note"] or "NOT-AN-IMAGE" in r["note"]
                or r["http_status"] not in ("200",))]
    print(f"\nimage recovery gaps: {len(flagged)}")
    for r in flagged:
        print(f"  {r['http_status']:4} {r['note'][:40]:42} {r['url']}")


if __name__ == "__main__":
    main()
