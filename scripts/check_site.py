#!/usr/bin/env python3
"""Validate the generated static site: every internal link resolves.

Checks, against web/:
  1. Every href/src starting with "/" in every generated .html file
     points at a file that exists (fragments and query strings stripped).
  2. Every <loc> in sitemap.xml resolves to a generated file.
  3. Every nav link in the shared site nav resolves.

Exit 0 = clean, 1 = broken links found. Stdlib only.
"""
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

    if broken:
        print(f"BROKEN {len(broken)}")
        for line in broken:
            print("  " + line)
        return 1
    print(f"OK {len(html_files)} html files, all internal links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
