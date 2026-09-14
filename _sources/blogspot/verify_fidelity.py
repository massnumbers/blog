"""Compare each ported post's prose against its Blogger original.

Task 4.6 of the port-blogspot-archive change. Both sides are reduced to a bare
word sequence -- markup, image syntax, link targets and the added provenance
callout removed -- so the diff shows only genuine additions or losses of prose.
"""
import difflib
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
BLOG = HERE.parent.parent

PILOTS = {
    "2013-01-03-senate-candidate-qualifications": "2013-01-03",
    "2014-08-12-governor-polling-averages": "2014-08-12",
    "2012-11-18-house-district-partisan-ranking": "2012-11-18",
}


def words_from_html(raw):
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return normalize(text)


def words_from_qmd(raw):
    # The subtitle legitimately moves into the front-matter description, and the
    # "by BRENT BENSON" byline into the author field, so count the description
    # as prose and expect the byline to be absent.
    parts = raw.split("---", 2)
    front, body = parts[1], parts[-1]
    body = re.sub(r"^\|[\s\-|]+\|$", "", body, flags=re.M)   # markdown table rules
    desc = re.search(r'^description:\s*"(.*)"\s*$', front, re.M)
    if desc:
        # Only credit the description when the subtitle actually moved out of
        # the body; when it survives as a heading too, counting both duplicates it.
        if normalize(desc.group(1)) and normalize(desc.group(1)) not in \
                [normalize(line) for line in body.split("\n") if line.strip()]:
            body = desc.group(1) + "\n" + body
    # Drop the provenance callout and any tier note: both are additions the
    # spec requires, not original prose.
    body = re.sub(r"::: \{\.callout-note[^}]*\}.*?:::", " ", body, flags=re.S)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)          # images
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)       # link text only
    return normalize(body)


def normalize(text):
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[*#>`]", " ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9%.\- ]", " ", text)
    return [w for w in text.split() if w not in {"-", ".", "%"}]


def drop_byline(words):
    """Remove the 'by BRENT BENSON' byline: it becomes front-matter authorship."""
    for i in range(len(words) - 2):
        if words[i:i + 3] == ["by", "brent", "benson"]:
            return words[:i] + words[i + 3:]
    return words


def main():
    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    failures = 0
    for slug, date in PILOTS.items():
        qmd = (BLOG / "posts" / slug / "index.qmd").read_text()
        title = qmd.split("\n")[1].split('"')[1]
        entry = next(e for e in feed["entry"]
                     if e["published"]["$t"][:10] == date and e["title"]["$t"] == title)

        orig = words_from_html(entry["content"]["$t"])
        orig = drop_byline(orig)
        port = words_from_qmd(qmd)

        sm = difflib.SequenceMatcher(None, orig, port, autojunk=False)
        added, removed = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("delete", "replace"):
                removed += orig[i1:i2]
            if tag in ("insert", "replace"):
                added += port[j1:j2]

        ratio = sm.ratio()
        print(f"\n=== {slug}")
        print(f"    original words {len(orig):5}   ported words {len(port):5}   similarity {ratio:.4f}")
        if removed:
            print(f"    REMOVED ({len(removed)}): {' '.join(removed[:25])}")
        if added:
            print(f"    ADDED   ({len(added)}): {' '.join(added[:25])}")
        if not removed and not added:
            print("    prose identical after formatting normalization")
        if removed or added:
            failures += 1

    print(f"\nposts with any prose difference: {failures}/{len(PILOTS)}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
