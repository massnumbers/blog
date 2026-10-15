"""Verify ported Blogger posts against their originals and the port rules.

Started as task 4.6 of port-blogspot-archive; driven by the manifest since
migrate-blogspot-archive. For every manifest row that has been staged or
verified (or the site_dirs named on the command line), two kinds of check run:

- Prose: both sides are reduced to a bare word sequence -- markup, image
  syntax, link targets and the added editorial callouts removed -- so the diff
  shows only genuine additions or losses of prose.
- Rendered output in docs/posts/<site_dir>/index.html: no imgur or
  Blogger-hosted image, no Fusion Tables URL, no unresolved TODO-TIER marker,
  and a link to the post's own Blogger permalink. With --strict-links, no link
  to any other Blogger post may remain either.

--mark-verified moves passing staged rows to port_status=verified.
"""
import argparse
import csv
import difflib
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
BLOG = HERE.parent.parent
MANIFEST = HERE / "manifest.csv"

FORBIDDEN = {
    "imgur": re.compile(r"i\.imgur\.com", re.I),
    "blogger-image": re.compile(r"blogger\.googleusercontent\.com|bp\.blogspot\.com", re.I),
    "fusion": re.compile(r"fusiontables?\.(google|googleusercontent)\.com|google\.com/fusiontables", re.I),
    "tier-marker": re.compile(r"TODO-TIER"),
}
BLOGGER_POST_RE = re.compile(r'href="(https?://massnumbers\.blogspot\.com/\d{4}/\d{2}/[^"#?]+)')


def words_from_html(raw):
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    # Inline tags can sit inside a word (a link starting mid-word), so they
    # vanish without a space; every other tag separates words.
    text = re.sub(r"</?(a|b|i|em|strong|span|font|u)\b[^>]*>", "", text, flags=re.I)
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
        # A description drawn from the opening sentences is a copy of body
        # text, not a moved subtitle, so it is not credited either.
        desc_words = normalize(desc.group(1).rstrip("."))
        body_words = normalize(strip_markup(body))
        if desc_words and desc_words not in \
                [normalize(line) for line in body.split("\n") if line.strip()] \
                and not contains_run(body_words, desc_words):
            body = desc.group(1) + "\n" + body
    # Drop the provenance callout and any tier note: both are additions the
    # spec requires, not original prose.
    body = re.sub(r"::: \{\.callout-note[^}]*\}.*?:::", " ", body, flags=re.S)
    # Executable chunks (a rebuilt map) are code, not prose; plain fenced
    # blocks converted from <pre> are prose and stay.
    body = re.sub(r"^```\{.*?^```[ \t]*$", " ", body, flags=re.S | re.M)
    return normalize(strip_markup(body))


def strip_markup(body):
    """Images removed, links reduced to their text. Link targets may contain
    balanced parentheses, as some poll PDF URLs do."""
    target = r"\((?:<[^>]*>|(?:[^()\s]|\([^()]*\))*)\)"
    body = re.sub(r"!\[[^\]]*\]" + target, " ", body)
    return re.sub(r"\[([^\]]*)\]" + target, r"\1", body)


def normalize(text):
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[*#>`]", " ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9%.\- ]", " ", text)
    # Trailing periods and leading dashes attach to whichever word markup left
    # them next to, so they are not part of the comparison.
    words = (w.rstrip(".").lstrip("-") for w in text.split())
    return [w for w in words if w and w != "%"]


def contains_run(words, run):
    """True when run appears as a contiguous sequence in words."""
    n = len(run)
    return any(words[i:i + n] == run for i in range(len(words) - n + 1))


def drop_byline(words):
    """Remove the 'by BRENT BENSON' byline: it becomes front-matter authorship."""
    for i in range(len(words) - 2):
        if words[i:i + 3] == ["by", "brent", "benson"]:
            return words[:i] + words[i + 3:]
    return words


def prose_diff(entry, qmd):
    orig = drop_byline(words_from_html(entry["content"]["$t"]))
    port = words_from_qmd(qmd)
    sm = difflib.SequenceMatcher(None, orig, port, autojunk=False)
    added, removed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            removed += orig[i1:i2]
        if tag in ("insert", "replace"):
            added += port[j1:j2]
    return len(orig), len(port), sm.ratio(), added, removed


def rendered_problems(row, strict_links):
    page = BLOG / "docs" / "posts" / row["site_dir"] / "index.html"
    if not page.exists():
        return ["not rendered"]
    out = page.read_text()
    problems = [name for name, rx in FORBIDDEN.items() if rx.search(out)]
    own = row["permalink"].split("://", 1)[1]
    if own not in out:
        problems.append("no provenance link")
    if strict_links:
        others = {u for u in BLOGGER_POST_RE.findall(out) if u.split("://", 1)[1] != own}
        if others:
            problems.append(f"blogger post links {len(others)}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site_dirs", nargs="*", help="limit to these manifest site_dirs")
    ap.add_argument("--strict-links", action="store_true",
                    help="fail on any remaining link to another Blogger post")
    ap.add_argument("--mark-verified", action="store_true",
                    help="set port_status=verified on staged rows that pass")
    args = ap.parse_args()

    rows = list(csv.DictReader(MANIFEST.open()))
    if args.site_dirs:
        unknown = set(args.site_dirs) - {r["site_dir"] for r in rows}
        if unknown:
            raise SystemExit(f"not in manifest: {sorted(unknown)}")
        targets = [r for r in rows if r["site_dir"] in args.site_dirs]
    else:
        targets = [r for r in rows if r["port_status"] in ("staged", "verified")]

    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    entries = {}
    for e in feed["entry"]:
        for link in e.get("link", []):
            if link.get("rel") == "alternate":
                entries[link["href"]] = e

    failures = []
    for row in targets:
        qmd = (BLOG / "posts" / row["site_dir"] / "index.qmd").read_text()
        n_orig, n_port, ratio, added, removed = prose_diff(entries[row["permalink"]], qmd)
        problems = rendered_problems(row, args.strict_links)

        status = "ok" if not (added or removed or problems) else "FAIL"
        print(f"{status:4} {ratio:.4f} {row['site_dir']}"
              f"  (words {n_orig} -> {n_port})" + (f"  [{', '.join(problems)}]" if problems else ""))
        if removed:
            print(f"       REMOVED ({len(removed)}): {' '.join(removed[:25])}")
        if added:
            print(f"       ADDED   ({len(added)}): {' '.join(added[:25])}")
        if status == "ok" and args.mark_verified and row["port_status"] == "staged":
            row["port_status"] = "verified"
        if status != "ok":
            failures.append(row["site_dir"])

    if args.mark_verified:
        with MANIFEST.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    print(f"\nchecked {len(targets)}, failing {len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
