"""Convert a Blogger post body into Quarto markdown.

Task 3.1 of the port-blogspot-archive change. Handles the markup this archive
actually uses: <br/>-separated paragraphs, an <i> subtitle and <span> byline in
the first lines, imgur <img> tags (often wrapped in <a> or <div>), and dead
Fusion Tables references.

Conversion is deliberately conservative. Prose is never rewritten -- only
re-marked -- and anything the converter is unsure about is flagged in the
report rather than silently dropped, so hand correction is directed.
"""
import argparse
import csv
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from build_manifest import permalink, slugify

HERE = Path(__file__).parent

ARCHIVE_CATEGORY = "blogger-archive"

FUSION_RE = re.compile(r"fusiontables?\.(google|googleusercontent)\.com|"
                       r"google\.com/fusiontables", re.I)


def load_image_map():
    """imgur/blogger URL -> local filename, from the 1.5 download."""
    path = HERE / "images.csv"
    if not path.exists():
        return {}
    return {r["url"]: r["local_file"] for r in csv.DictReader(path.open())
            if r["status"] == "ok"}


def load_site_dirs():
    """Blogger post path -> posts/ directory name, from the manifest."""
    return {r["blogger_path"]: r["site_dir"]
            for r in csv.DictReader((HERE / "manifest.csv").open())}


def strip_attrs(tag_html, keep):
    return {k.lower(): html.unescape(v) for k, v in
            re.findall(r'\b([a-zA-Z-]+)\s*=\s*"([^"]*)"', tag_html) if k.lower() in keep}


class Converter:
    def __init__(self, image_map, site_dirs):
        self.image_map = image_map
        self.site_dirs = site_dirs
        self.flags = []

    def flag(self, kind, detail=""):
        self.flags.append(f"{kind}:{detail}" if detail else kind)

    def convert(self, body):
        text = body

        # Fusion Tables iframes and their wrapping anchors are dead; remove the
        # markup and leave a marker for the tier decision to replace by hand.
        text = re.sub(r"<iframe\b[^>]*>.*?</iframe>", self._iframe, text,
                      flags=re.S | re.I)
        text = re.sub(r"<iframe\b[^>]*/?>", self._iframe, text, flags=re.I)

        # <a href=fusion><img></a> -> keep the image, drop the dead link.
        text = re.sub(r'<a\b([^>]*)>(\s*<img\b[^>]*/?>\s*)</a>', self._linked_image,
                      text, flags=re.S | re.I)

        text = re.sub(r"<img\b([^>]*?)/?>", self._image, text, flags=re.I)
        text = re.sub(r"<a\b([^>]*)>(.*?)</a>", self._anchor, text, flags=re.S | re.I)

        for tag, mark in (("b", "**"), ("strong", "**"), ("i", "*"), ("em", "*")):
            text = re.sub(rf"<{tag}\b[^>]*>(.*?)</{tag}>",
                          lambda m, k=mark: f"{k}{m.group(1).strip()}{k}" if m.group(1).strip() else "",
                          text, flags=re.S | re.I)

        for level in range(1, 7):
            text = re.sub(rf"<h{level}\b[^>]*>(.*?)</h{level}>",
                          lambda m, l=level: f"\n\n{'#' * l} {m.group(1).strip()}\n\n",
                          text, flags=re.S | re.I)

        text = re.sub(r"<table\b[^>]*>(.*?)</table>", self._table, text, flags=re.S | re.I)

        text = re.sub(r"<li\b[^>]*>(.*?)</li>", lambda m: f"\n- {m.group(1).strip()}",
                      text, flags=re.S | re.I)
        text = re.sub(r"</?[ou]l\b[^>]*>", "\n\n", text, flags=re.I)
        text = re.sub(r"<blockquote\b[^>]*>(.*?)</blockquote>",
                      lambda m: "\n\n> " + m.group(1).strip().replace("\n", "\n> ") + "\n\n",
                      text, flags=re.S | re.I)

        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"</(p|div)>", "\n\n", text, flags=re.I)
        text = re.sub(r"<(p|div|span|center|table|tbody|thead|tfoot|tr|td|th|font)\b[^>]*>", "", text, flags=re.I)
        text = re.sub(r"</(span|center|table|tbody|thead|tfoot|tr|td|th|font)>", "", text, flags=re.I)

        leftover = re.findall(r"<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>", text)
        if leftover:
            self.flag("leftover-tags", ",".join(sorted(set(t.lower() for t in leftover))[:6]))
        text = re.sub(r"<[^>]+>", "", text)

        text = html.unescape(text)
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"^\*{1,2}$", "", text, flags=re.M)     # empty <b>/<i> pairs
        text = re.sub(r"(?<!\*)\*{2}\s*\*{2}(?!\*)", "", text)
        text = re.sub(r"[ \t]+$", "", text, flags=re.M)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _table(self, m):
        """Render an HTML table as a markdown pipe table.

        Several posts carry real data tables. Stripping their tags runs the
        cells together into one unreadable string, so they are converted rather
        than flattened.
        """
        rows = []
        for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", m.group(1), re.S | re.I):
            cells = []
            for cell in re.findall(r"<(?:td|th)\b[^>]*>(.*?)</(?:td|th)>", tr, re.S | re.I):
                value = re.sub(r"<br\s*/?>", " ", cell, flags=re.I)
                value = re.sub(r"<[^>]+>", "", value)
                value = html.unescape(value).replace("\xa0", " ")
                cells.append(re.sub(r"\s+", " ", value).strip().replace("|", "\\|"))
            if cells:
                rows.append(cells)

        if not rows:
            self.flag("table-empty")
            return "\n\n"

        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        self.flag("table-converted", f"{len(rows)}x{width}")

        out = ["| " + " | ".join(rows[0]) + " |",
               "|" + "|".join(["---"] * width) + "|"]
        out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n\n" + "\n".join(out) + "\n\n"

    def _iframe(self, m):
        src = strip_attrs(m.group(0), {"src"}).get("src", "")
        if FUSION_RE.search(src):
            self.flag("fusion-embed-removed")
            return ("\n\n::: {.callout-note}\nTODO-TIER: the original interactive "
                    "Fusion Tables map appeared here.\n:::\n\n")
        self.flag("iframe-removed", src[:40])
        return "\n\n"

    def _linked_image(self, m):
        href = strip_attrs(f"<a {m.group(1)}>", {"href"}).get("href", "")
        inner = self._image_from_tag(m.group(2))
        if FUSION_RE.search(href):
            self.flag("fusion-link-on-image")
            return f"\n\n{inner}\n\n"
        if href:
            return f"\n\n[{inner}]({href})\n\n"
        return f"\n\n{inner}\n\n"

    def _image_from_tag(self, tag_html):
        attrs = strip_attrs(tag_html, {"src", "alt"})
        src, alt = attrs.get("src", ""), attrs.get("alt", "")
        local = self.image_map.get(src)
        if local:
            return f"![{alt}](images/{local})"
        self.flag("image-not-localized", src[:50])
        return f"![{alt}]({src})"

    def _image(self, m):
        return f"\n\n{self._image_from_tag(m.group(0))}\n\n"

    def _anchor(self, m):
        href = strip_attrs(f"<a {m.group(1)}>", {"href"}).get("href", "")
        inner = m.group(2)
        label = re.sub(r"<br\s*/?>", "\n", inner, flags=re.I)
        label = re.sub(r"<[^>]+>", "", label).strip()
        label = html.unescape(label).replace("\xa0", " ")
        if not href:
            return label

        if FUSION_RE.search(href):
            # Anchors wrapping an image are the archive's dominant map pattern:
            # a still screenshot that linked out to the interactive version.
            # The screenshot is the map, so keep it and drop only the dead link.
            if "![" in label:
                self.flag("fusion-link-on-image")
                return f"\n\n{label}\n\n"
            self.flag("fusion-link-removed")
            return label

        href = self._archive_target(href)
        return f"[{label}]({href})" if label else ""

    def _archive_target(self, href):
        """Point a link to another Blogger post at that post's ported copy.

        Matching is on the path alone so http/https and host variants resolve.
        Blogger pages that are not posts (static /p/ pages, label searches,
        the home page) have no ported copy and are left as published.
        """
        parts = urlsplit(href)
        if not parts.netloc.endswith("massnumbers.blogspot.com"):
            return href
        site_dir = self.site_dirs.get(parts.path)
        if not site_dir:
            self.flag("archive-link-kept", parts.path[:40])
            return href
        self.flag("archive-link-rewritten", site_dir)
        anchor = f"#{parts.fragment}" if parts.fragment else ""
        return f"../{site_dir}/index.qmd{anchor}"


def split_lead(text):
    """Pull the italic subtitle and 'by BRENT BENSON' byline off the top."""
    lines = [l for l in text.split("\n")]
    subtitle = ""
    body_start = 0
    for i, line in enumerate(lines[:6]):
        stripped = line.strip()
        if not stripped:
            body_start = i + 1
            continue
        if re.fullmatch(r"\*+by brent benson\*+|by brent benson", stripped, re.I):
            body_start = i + 1
            continue
        if not subtitle and stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 4:
            subtitle = stripped.strip("*").strip()
            body_start = i + 1
            continue
        break
    return subtitle, "\n".join(lines[body_start:]).strip()


def first_sentences(body, limit=220):
    """A description drawn from the opening prose, not from its markup.

    Headings are a better summary than the paragraph that follows, so a leading
    heading is used when there is one; otherwise the opening sentences are taken
    up to a sentence boundary rather than cut mid-word.
    """
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
        if stripped:
            break

    text = re.sub(r"[*#>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    return (cut[:end + 1] if end > 60 else cut.rsplit(" ", 1)[0] + "...").strip()


def yaml_escape(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_qmd(entry, image_map, site_dirs):
    conv = Converter(image_map, site_dirs)
    title = entry["title"]["$t"]
    date = entry["published"]["$t"][:10]
    url = permalink(entry)
    text = conv.convert(entry["content"]["$t"])
    subtitle, body = split_lead(text)

    description = subtitle or first_sentences(body)

    front = [
        "---",
        f"title: {yaml_escape(title)}",
        f"description: {yaml_escape(description)}",
        "author:",
        "  - name: Brent Benson",
        "    url: https://massnumbers.us/brentbenson",
        f"date: {date}",
        f"categories: [{ARCHIVE_CATEGORY}]",
        "---",
        "",
        f"::: {{.callout-note appearance=\"simple\"}}",
        f"Originally published on the [Mass. Numbers Blogger site]({url}) on {date}.",
        ":::",
        "",
        "",
    ]
    return "\n".join(front) + body + "\n", conv.flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="directory to write .qmd files into")
    ap.add_argument("--report", default=None, help="csv path for the per-post flag report")
    args = ap.parse_args()

    feed = json.loads((HERE / "feed.json").read_text())["feed"]
    image_map = load_image_map()
    site_dirs = load_site_dirs()
    out_dir = Path(args.out) if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    report = []
    for entry in feed["entry"]:
        title = entry["title"]["$t"]
        date = entry["published"]["$t"][:10]
        slug = slugify(title)[:60].strip("-")
        site_dir = site_dirs.get(urlsplit(permalink(entry)).path) or f"{date}-{slug}"
        qmd, flags = build_qmd(entry, image_map, site_dirs)

        if out_dir:
            post_dir = out_dir / site_dir
            post_dir.mkdir(parents=True, exist_ok=True)
            (post_dir / "index.qmd").write_text(qmd)

        kinds = [f.split(":")[0] for f in flags]
        report.append({
            "date": date, "slug": slug, "site_dir": site_dir, "title": title,
            "chars": len(qmd),
            "flags": ";".join(sorted(set(kinds))),
            "flag_detail": " | ".join(flags[:6]),
            "fusion_markers": qmd.count("TODO-TIER"),
            "residual_fusion_urls": len(FUSION_RE.findall(qmd)),
            "residual_html": len(re.findall(r"<[a-zA-Z][^>]*>", qmd)),
            "remote_images": len(re.findall(r"!\[[^\]]*\]\(https?://", qmd)),
            "archive_links": kinds.count("archive-link-rewritten"),
            "archive_links_kept": kinds.count("archive-link-kept"),
        })

    if args.report:
        with Path(args.report).open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(report[0]))
            writer.writeheader()
            writer.writerows(report)

    print(f"converted {len(report)} posts")
    print(f"  posts with residual fusion urls : {sum(1 for r in report if r['residual_fusion_urls'])}")
    print(f"  posts with residual html tags   : {sum(1 for r in report if r['residual_html'])}")
    print(f"  posts with un-localized images  : {sum(1 for r in report if r['remote_images'])}")
    print(f"  posts with a tier marker        : {sum(1 for r in report if r['fusion_markers'])}")
    print(f"  intra-archive links rewritten   : {sum(r['archive_links'] for r in report)}"
          f" in {sum(1 for r in report if r['archive_links'])} posts")
    print(f"  intra-archive links kept        : {sum(r['archive_links_kept'] for r in report)}")


if __name__ == "__main__":
    main()
