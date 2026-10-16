#!/usr/bin/env python3
"""Download the human-approved strain photos from Wikimedia Commons with attribution.

Reads  data/strain_photos.approved.json   (curated; nothing is added automatically)
Writes web/img/strains/<slug>.<ext>       (900 px thumbnails, not the full originals)
       web/data/strain_photos.json        (author, license, license URL, file page, sha256)

Only these licenses are accepted: CC0, public domain, CC BY, CC BY-SA. Anything else is
refused rather than copied. The strain label on Commons is the uploader's claim; this
script records that and never asserts the cultivar's genetics.

Usage: python3 scripts/fetch_strain_photos.py [--refresh]
"""
import hashlib, html, json, re, sys, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "data" / "strain_photos.approved.json"
OUT_DIR = ROOT / "web" / "img" / "strains"
RECORDS = ROOT / "web" / "data" / "strain_photos.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "cannagenetics-photo-fetch/1.0 (https://github.com/coden607/cannagenetics; coden607@gmail.com)"
ALLOWED = re.compile(r"^(cc0|pd|public domain|cc[- ]by(-sa)?[- ]\d)", re.I)
MAX_BYTES = 6 * 1024 * 1024


def api(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        return json.load(r)


def plain(value):
    return html.unescape(re.sub(r"<[^>]*>", "", value or "")).strip()


def sniff(data):
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def main():
    refresh = "--refresh" in sys.argv
    approved = json.loads(APPROVED.read_text())["photos"]
    existing = json.loads(RECORDS.read_text()) if RECORDS.exists() else {}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, failures = {}, []
    for item in approved:
        slug, title = item["slug"], item["commons_title"]
        prev = existing.get(slug)
        if prev and not refresh and (ROOT / "web" / prev["local_path"].lstrip("/")).exists() and prev["commons_title"] == title:
            records[slug] = prev
            continue
        try:
            data = api({"action": "query", "titles": title, "prop": "imageinfo",
                        "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 900})
            page = next(iter(data["query"]["pages"].values()))
            info = (page.get("imageinfo") or [None])[0]
            if not info:
                raise RuntimeError("file not found on Commons")
            meta = info.get("extmetadata", {})
            license_name = plain(meta.get("LicenseShortName", {}).get("value"))
            if not ALLOWED.match(license_name):
                raise RuntimeError(f"license not allowed: {license_name!r}")
            author = plain(meta.get("Artist", {}).get("value"))
            if not author:
                raise RuntimeError("no author recorded")
            thumb = info.get("thumburl") or info["url"]
            req = urllib.request.Request(thumb, headers={"User-Agent": UA})
            blob = urllib.request.urlopen(req, timeout=60).read(MAX_BYTES + 1)
            if len(blob) > MAX_BYTES:
                raise RuntimeError("image larger than 6 MB")
            ext = sniff(blob)
            if not ext:
                raise RuntimeError("download is not a JPEG/PNG/WebP image")
            dest = OUT_DIR / f"{slug}.{ext}"
            dest.write_bytes(blob)
            records[slug] = {
                "slug": slug,
                "commons_title": title,
                "file_page": info.get("descriptionurl"),
                "author": author[:160],
                "license": license_name,
                "license_url": plain(meta.get("LicenseUrl", {}).get("value")) or None,
                "local_path": f"/img/strains/{slug}.{ext}",
                "sha256": hashlib.sha256(blob).hexdigest(),
                "bytes": len(blob),
                "retrieved": date.today().isoformat(),
                "identity": "as labelled by the uploader; not verified",
            }
            print(f"ok   {slug:20} {license_name:14} {author[:40]}")
            time.sleep(0.5)
        except Exception as exc:  # report, keep going: one bad file must not block the rest
            failures.append((slug, str(exc)))
            print(f"FAIL {slug:20} {exc}")
    RECORDS.write_text(json.dumps(dict(sorted(records.items())), indent=1, ensure_ascii=False) + "\n")
    print(f"{len(records)} photos recorded, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
