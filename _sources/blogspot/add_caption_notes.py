"""Add the vanished-interactive-map note after stale captions.

Hand correction for the stale-interactive-caption issue in
conversion_report.csv. stale_captions.tsv lists, per staged post, a fragment of
the original caption or sentence that promises an interactive map; the note is
inserted after the paragraph containing it, leaving the original words intact.
Idempotent, so it is safe to rerun after re-staging a batch.

    python _sources/blogspot/add_caption_notes.py   (from the repo root)
"""
from pathlib import Path

HERE = Path(__file__).parent
BLOG = HERE.parent.parent
NOTE = '''::: {.callout-note appearance="simple"}
The interactive version of this map was built with Google Fusion Tables, which
Google shut down on 3 December 2019. Only the static image survives.
:::'''
rows = [line.split("\t", 1) for line in (HERE / "stale_captions.tsv").read_text().splitlines()
        if line and not line.startswith("#")]
for d, marker in rows:
    p = BLOG / "posts" / d / "index.qmd"
    if not p.exists():
        continue
    t = p.read_text()
    body_start = t.index("\n---\n", 4) + 5
    added = 0
    i = t.find(marker, body_start)
    while i != -1:
        end = t.find("\n\n", i)
        end = len(t) if end == -1 else end
        # Every occurrence gets the note once; rerunning adds nothing.
        if not t[end:].startswith("\n\n" + NOTE):
            t = t[:end] + "\n\n" + NOTE + t[end:]
            added += 1
        i = t.find(marker, end + len(NOTE) + 2)
    if added:
        p.write_text(t)
        print(f"noted {d} ({added})")
