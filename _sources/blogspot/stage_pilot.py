"""Stage a pilot post into posts/ with its images localized beside it.

Tasks 4.2-4.4 of the port-blogspot-archive change. Copies the converted .qmd,
rewrites its image paths from the shared _sources/blogspot/images/ pool to a
per-post images/ directory, and keeps the original Blogger HTML under the
post's own _sources/ for the fidelity check in 4.6.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
BLOG = HERE.parent.parent
CONVERTED = Path("/private/tmp/claude-501/-Users-bwb-src-github-com-massnumbers-blog/"
                 "47615086-d0de-46f9-8dfe-371a4e927a4f/scratchpad/converted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="converted dir name")
    ap.add_argument("--dest", required=True, help="posts/ dir name")
    args = ap.parse_args()

    src = CONVERTED / args.source
    dest = BLOG / "posts" / args.dest
    (dest / "images").mkdir(parents=True, exist_ok=True)
    (dest / "_sources").mkdir(parents=True, exist_ok=True)

    qmd = (src / "index.qmd").read_text()

    used = sorted(set(re.findall(r"!\[[^\]]*\]\(images/([^)]+)\)", qmd)))
    for name in used:
        shutil.copy2(HERE / "images" / name, dest / "images" / name)

    (dest / "index.qmd").write_text(qmd)

    date = args.dest[:10]
    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    for entry in feed["entry"]:
        if entry["published"]["$t"][:10] == date and \
                entry["title"]["$t"] in qmd.split("\n")[1]:
            (dest / "_sources" / "original.html").write_text(entry["content"]["$t"])
            break

    size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
    img_size = sum(f.stat().st_size for f in (dest / "images").iterdir())
    print(f"{args.dest}")
    print(f"  images copied : {len(used)}")
    print(f"  images bytes  : {img_size / 1024:.0f} KB")
    print(f"  dir total     : {size / 1024:.0f} KB")
    print(f"  remote images : {len(re.findall(r'!\[[^\]]*\]\(https?://', qmd))}")
    print(f"  fusion urls   : {len(re.findall(r'fusiontable', qmd, re.I))}")


if __name__ == "__main__":
    main()
