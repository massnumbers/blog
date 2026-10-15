"""Stage converted Blogger posts into posts/ with their images localized.

Replaces stage_pilot.py for the migrate-blogspot-archive change. Reads the
converter's output directory, copies each post's .qmd into posts/<site_dir>/,
copies the images it uses from the shared _sources/blogspot/images/ pool into
a per-post images/ directory, keeps the original Blogger HTML under the post's
own _sources/ for the fidelity check, and marks the manifest row staged.

    python convert_post.py --out <dir>
    python stage_post.py --converted <dir> --year 2014
    python stage_post.py --converted <dir> 2014-03-09-fifth-middlesex-likely-blue
"""
import argparse
import csv
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
BLOG = HERE.parent.parent
MANIFEST = HERE / "manifest.csv"

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(images/([^)]+)\)")


def stage_two_permalinks():
    """Posts with a map needing judgment: any tier-1 or tier-3 reference.

    These are ported one at a time by name, never swept up by --year.
    """
    return {r["post_permalink"] for r in csv.DictReader((HERE / "fusion_tables.csv").open())
            if not r["fidelity_tier"].startswith("2")}


def add_listing_image(qmd, used):
    """Use the post's first image as its listing thumbnail."""
    if not used or re.search(r"^image:", qmd, re.M):
        return qmd
    return re.sub(r"^date:", f"image: images/{used[0]}\ndate:", qmd, count=1, flags=re.M)


def stage(row, converted, originals, dest_root):
    src = converted / row["site_dir"] / "index.qmd"
    dest = dest_root / row["site_dir"]
    qmd = src.read_text()

    used = list(dict.fromkeys(IMAGE_RE.findall(qmd)))
    if used:
        (dest / "images").mkdir(parents=True, exist_ok=True)
        for name in used:
            shutil.copy2(HERE / "images" / name, dest / "images" / name)

    (dest / "_sources").mkdir(parents=True, exist_ok=True)
    (dest / "_sources" / "original.html").write_text(originals[row["permalink"]])
    (dest / "index.qmd").write_text(add_listing_image(qmd, used))

    size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
    remote = len(re.findall(r"!\[[^\]]*\]\(https?://", qmd))
    fusion = len(re.findall(r"fusiontable", qmd, re.I))
    print(f"{row['site_dir']}: {len(used)} images, {size / 1024:.0f} KB, "
          f"remote images {remote}, fusion urls {fusion}")
    return remote == 0 and fusion == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--converted", required=True, type=Path,
                    help="output directory of convert_post.py --out")
    ap.add_argument("--year", action="append", default=[],
                    help="stage every pending stage-one post from this year (repeatable)")
    ap.add_argument("--dest", type=Path, default=BLOG / "posts",
                    help="where to stage; defaults to posts/")
    ap.add_argument("--no-status", action="store_true",
                    help="do not update port_status in the manifest")
    ap.add_argument("site_dirs", nargs="*", help="manifest site_dir values to stage")
    args = ap.parse_args()

    rows = list(csv.DictReader(MANIFEST.open()))
    stage_two = stage_two_permalinks()
    wanted = [r for r in rows if r["site_dir"] in args.site_dirs or
              (r["date"][:4] in args.year and r["port_status"] == "pending"
               and r["permalink"] not in stage_two)]
    unknown = set(args.site_dirs) - {r["site_dir"] for r in rows}
    if unknown:
        raise SystemExit(f"not in manifest: {sorted(unknown)}")
    if not wanted:
        raise SystemExit("nothing to stage")

    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    originals = {}
    for entry in feed["entry"]:
        for link in entry.get("link", []):
            if link.get("rel") == "alternate":
                originals[link["href"]] = entry["content"]["$t"]

    clean = all([stage(r, args.converted, originals, args.dest) for r in wanted])

    if not args.no_status:
        for r in wanted:
            if r["port_status"] == "pending":
                r["port_status"] = "staged"
        with MANIFEST.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    print(f"staged {len(wanted)} posts" + ("" if clean else "; some need attention"))


if __name__ == "__main__":
    main()
