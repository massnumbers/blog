"""Download every live image referenced by the archive into images/.

Task 1.5 of the port-blogspot-archive change. Each file is verified against the
byte size recorded during the 1.4 liveness check, so a silent truncation or a
placeholder swap between the two runs is caught rather than stored.
"""
import csv
import hashlib
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
IMAGES = HERE / "images"
UA = "Mozilla/5.0 (compatible; massnumbers-archive-audit/1.0)"

MAGIC = {b"\x89PNG": ".png", b"\xff\xd8\xff": ".jpg", b"GIF8": ".gif", b"RIFF": ".webp"}


def local_name(url, body):
    """Stable filename: imgur/blogger id where available, else a content hash."""
    ext = next((e for m, e in MAGIC.items() if body.startswith(m)), ".img")
    if "i.imgur.com" in url:
        stem = url.rstrip("/").split("/")[-1].split(".")[0]
        return f"imgur-{stem}{ext}"
    if "blogger.googleusercontent.com" in url:
        stem = hashlib.sha1(url.encode()).hexdigest()[:12]
        return f"blogger-{stem}{ext}"
    stem = hashlib.sha1(url.encode()).hexdigest()[:12]
    slug = re.sub(r"[^a-z0-9]+", "-", url.split("/")[-1].lower())[:30].strip("-")
    return f"{slug}-{stem}{ext}"


def fetch(item):
    url, expected = item
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
    except Exception as exc:
        return {"url": url, "local_file": "", "bytes": 0,
                "status": f"FAILED {type(exc).__name__}"}

    name = local_name(url, body)
    status = "ok"
    if expected and len(body) != int(expected):
        status = f"SIZE-MISMATCH expected={expected} got={len(body)}"
    if not any(body.startswith(m) for m in MAGIC):
        status = "NOT-AN-IMAGE"
    (IMAGES / name).write_bytes(body)
    return {"url": url, "local_file": name, "bytes": len(body), "status": status}


def main():
    IMAGES.mkdir(exist_ok=True)
    rows = list(csv.DictReader((HERE / "resources.csv").open()))

    # One download per unique URL, keeping the size seen during the 1.4 check.
    wanted = {}
    for row in rows:
        if row["kind"] == "image" and row["http_status"] == "200":
            wanted.setdefault(row["url"], row["content_length"])

    print(f"downloading {len(wanted)} unique images...")
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(fetch, wanted.items()))

    out = HERE / "images.csv"
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["url", "local_file", "bytes", "status"])
        writer.writeheader()
        writer.writerows(sorted(results, key=lambda r: r["local_file"]))

    bad = [r for r in results if r["status"] != "ok"]
    total = sum(r["bytes"] for r in results)
    print(f"downloaded: {len(results) - len(bad)}/{len(results)}")
    print(f"total size: {total / 1024 / 1024:.1f} MB")
    for r in bad:
        print(f"  {r['status']}  {r['url']}")


if __name__ == "__main__":
    main()
