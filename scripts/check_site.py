#!/usr/bin/env python3
"""Validate the generated static site: every internal link resolves.

Checks, against web/:
  1. Every href/src starting with "/" in every generated .html file
     points at a file that exists (fragments and query strings stripped).
  2. Every <loc> in sitemap.xml resolves to a generated file.
  3. Every nav link in the shared site nav resolves.
  4. Strain photos: every record in data/strain_photos.json has its image file, an
     author, an allow-listed license and a Commons file page, and every page that shows
     the photo carries that credit. A photo without attribution fails the build.

Exit 0 = clean, 1 = broken links found. Stdlib only.
"""
import json
import re
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"

LINK_RE = re.compile(r'(?:href|src)="(/[^"#?]*)"')
SCRIPT_RE = re.compile(r"<script.*?</script>", re.S)
LOC_RE = re.compile(r"<loc>https://[^/]+(/[^<]*)</loc>")
NAV_RE = re.compile(r'<nav class="wrap">(.*?)</nav>', re.S)


def resolve(url_path: str) -> bool:
    """Map a site-absolute path to a file under web/ (cleanUrls aware)."""
    rel = url_path.lstrip("/")
    if not rel:
        return (WEB / "index.html").exists()
    direct = WEB / rel
    if direct.is_file():
        return True
    # cleanUrls: /clones -> clones.html, /suppliers/ -> suppliers/index.html
    if (WEB / (rel + ".html")).is_file():
        return True
    if (WEB / rel / "index.html").is_file():
        return True
    return False


ALLOWED_LICENSE = re.compile(r"^(cc0|pd|public domain|cc[- ]by(-sa)?[- ]\d)", re.I)


def check_photos(html_files):
    """Attribution is a license condition, so a missing credit is a build failure."""
    problems = []
    records_file = WEB / "data" / "strain_photos.json"
    if not records_file.exists():
        return problems
    records = json.loads(records_file.read_text())
    for slug, rec in records.items():
        img = WEB / rec.get("local_path", "").lstrip("/")
        if not img.exists() or img.stat().st_size < 20_000:
            problems.append(f"photo {slug}: image file missing or implausibly small")
        if not rec.get("author"):
            problems.append(f"photo {slug}: no author recorded")
        if not ALLOWED_LICENSE.match(rec.get("license", "")):
            problems.append(f"photo {slug}: license {rec.get('license')!r} is not allowed")
        if not str(rec.get("file_page", "")).startswith("https://commons.wikimedia.org/"):
            problems.append(f"photo {slug}: no Commons file page recorded")
        page = WEB / "cultivars" / f"{slug}.html"
        if page.exists():
            text = page.read_text()
            if rec["author"] not in text or "via Wikimedia Commons" not in text:
                problems.append(f"photo {slug}: cultivar page does not show the credit")
            if "not verified" not in text and "unverified" not in text:
                problems.append(f"photo {slug}: cultivar page lacks the identity caveat")
    return problems


def main() -> int:
    broken = []
    html_files = sorted(WEB.rglob("*.html"))

    for f in html_files:
        text = SCRIPT_RE.sub("", f.read_text())
        for link in LINK_RE.findall(text):
            if not resolve(link):
                broken.append(f"{f.relative_to(WEB)}: broken link {link}")

    sitemap = WEB / "sitemap.xml"
    if sitemap.exists():
        for loc in LOC_RE.findall(sitemap.read_text()):
            if not resolve(loc):
                broken.append(f"sitemap.xml: broken loc {loc}")

    index = WEB / "index.html"
    if index.exists():
        nav = NAV_RE.search(index.read_text())
        if nav:
            for link in LINK_RE.findall(nav.group(1)):
                if not resolve(link):
                    broken.append(f"nav: broken link {link}")
        else:
            broken.append("index.html: site nav not found")

    broken.extend(check_photos(html_files))

    if broken:
        print(f"BROKEN {len(broken)}")
        for line in broken:
            print("  " + line)
        return 1
    print(f"OK {len(html_files)} html files, all internal links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
