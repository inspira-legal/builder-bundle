#!/usr/bin/env python3
"""
Fetch web pages and download the images they show, so an agent can open them with Read.

For each page URL: fetch the HTML, collect og:image / twitter:image and <img> sources,
then download a bounded number of real images into a new, empty folder outside any git
repository (a fresh temp dir by default). Prints JSON to stdout.

Usage:
  python3 fetch_images.py https://example.com/pricing https://example.com/onboarding
  python3 fetch_images.py --out DIR --per-page 6 --max-total 30 --max-bytes 5000000 URL...
"""

from __future__ import annotations

import http.client
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

DEFAULT_PER_PAGE = 6
DEFAULT_MAX_TOTAL = 30
DEFAULT_MAX_BYTES = 5_000_000
# Below this an image is a tracking pixel or an icon, not a reference worth opening.
MIN_IMAGE_BYTES = 2_048
MAX_HTML_BYTES = 3_000_000
TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

META_IMAGE_KEYS = {
    "og:image",
    "og:image:url",
    "og:image:secure_url",
    "twitter:image",
    "twitter:image:src",
}
# Lazy-load attributes first: on those pages `src` is a tiny placeholder.
IMG_ATTRS = ("data-src", "data-original", "data-lazy-src", "src")

# The Content-Type header can lie, so the bytes decide the type.
MAGIC = (
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
)


class ImageCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: list[str] = []
        self.imgs: list[str] = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            key = (a.get("property") or a.get("name") or "").strip().lower()
            if key in META_IMAGE_KEYS and a.get("content"):
                self.meta.append(a["content"].strip())
        elif tag in ("img", "source"):
            for attr in IMG_ATTRS:
                if a.get(attr):
                    self.imgs.append(a[attr].strip())
                    break
            else:
                srcset = a.get("srcset") or a.get("data-srcset")
                if srcset:
                    self.imgs.append(largest_from_srcset(srcset))
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title and len(self.title) < 300:
            self.title += data


def largest_from_srcset(srcset: str) -> str:
    best, best_w = "", -1.0
    for part in srcset.split(","):
        bits = part.strip().split()
        if not bits:
            continue
        w = 0.0
        if len(bits) > 1:
            try:
                w = float(bits[1].rstrip("wx"))
            except ValueError:
                w = 0.0
        if w > best_w:
            best, best_w = bits[0], w
    return best


def sniff(head: bytes) -> str | None:
    for sig, ext in MAGIC:
        if head.startswith(sig):
            return ext
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


def is_http(url: str) -> bool:
    return urlparse(url).scheme in ("http", "https")


def open_url(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def fetch_html(url: str) -> tuple[str, str]:
    with open_url(url) as resp:
        ctype = resp.headers.get("Content-Type", "")
        if "html" not in ctype.lower():
            raise ValueError(f"not an HTML page (Content-Type: {ctype or 'none'})")
        raw = resp.read(MAX_HTML_BYTES)
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.geturl(), raw.decode(charset, errors="replace")


def download(url: str, dest_base: str, max_bytes: int) -> dict:
    with open_url(url) as resp:
        ctype = (resp.headers.get("Content-Type") or "").lower()
        # Some CDNs serve images as octet-stream; the magic bytes decide below.
        if ctype and not ctype.startswith(("image/", "application/octet-stream", "binary/octet-stream")):
            return {"skip": f"Content-Type {ctype}"}
        length = resp.headers.get("Content-Length")
        if length and length.isdigit() and int(length) > max_bytes:
            return {"skip": f"{length} bytes over the {max_bytes} byte cap"}
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        return {"skip": f"over the {max_bytes} byte cap"}
    if len(data) < MIN_IMAGE_BYTES:
        return {"skip": f"{len(data)} bytes, too small to be a reference"}
    ext = sniff(data[:16])
    if not ext:
        return {"skip": "bytes are not a PNG, JPEG, GIF or WebP image"}
    path = f"{dest_base}.{ext}"
    with open(path, "xb") as fh:
        fh.write(data)
    return {"path": path, "bytes": len(data), "type": ext}


def inside_git_repo(path: str) -> bool:
    cur = os.path.abspath(path)
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return True
        parent = os.path.dirname(cur)
        if parent == cur:
            return False
        cur = parent


def prepare_out(out: str | None) -> str:
    if not out:
        return tempfile.mkdtemp(prefix="bb-research-images-")
    out = os.path.abspath(out)
    # Checked before makedirs, so a refused run leaves no folder behind in the repo.
    if inside_git_repo(out):
        raise ValueError(f"output folder sits inside a git repository: {out}")
    os.makedirs(out, exist_ok=True)
    if os.listdir(out):
        raise ValueError(f"output folder is not empty: {out}")
    return out


def parse_args(argv: list[str]) -> dict:
    opts = {
        "urls": [],
        "out": None,
        "per_page": DEFAULT_PER_PAGE,
        "max_total": DEFAULT_MAX_TOTAL,
        "max_bytes": DEFAULT_MAX_BYTES,
    }
    flags = {"--per-page": "per_page", "--max-total": "max_total", "--max-bytes": "max_bytes"}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--out" and i + 1 < len(argv):
            opts["out"] = argv[i + 1]
            i += 2
        elif arg in flags and i + 1 < len(argv):
            opts[flags[arg]] = int(argv[i + 1])
            i += 2
        else:
            opts["urls"].append(arg)
            i += 1
    return opts


def main() -> None:
    try:
        opts = parse_args(sys.argv[1:])
    except ValueError as exc:
        print(json.dumps({"error": f"bad flag value: {exc}"}))
        sys.exit(1)
    if not opts["urls"]:
        print(json.dumps({"error": "No page URLs provided"}))
        sys.exit(1)

    try:
        out_dir = prepare_out(opts["out"])
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)

    pages: list[dict] = []
    total = 0
    for page_no, page_url in enumerate(opts["urls"], start=1):
        page: dict = {"url": page_url, "title": "", "images": [], "skipped": [], "error": None}
        pages.append(page)
        if not is_http(page_url):
            page["error"] = "only http and https URLs are fetched"
            continue
        try:
            final_url, html = fetch_html(page_url)
        except (urllib.error.URLError, http.client.HTTPException, LookupError, ValueError, OSError) as exc:
            page["error"] = str(exc)
            continue

        parser = ImageCollector()
        try:
            parser.feed(html)
        except Exception as exc:  # html.parser rarely raises; keep what was collected
            page["error"] = f"HTML parse stopped early: {exc}"
        page["title"] = " ".join(parser.title.split())

        candidates: list[tuple[str, str]] = []
        seen: set[str] = set()
        for source, raw in [("meta", u) for u in parser.meta] + [("img", u) for u in parser.imgs]:
            if not raw or raw.startswith("data:"):
                continue
            url = urljoin(final_url, raw)
            if is_http(url) and url not in seen:
                seen.add(url)
                candidates.append((source, url))
        page["found"] = len(candidates)

        kept = 0
        page["left_out_by_cap"] = 0
        for source, url in candidates:
            if kept >= opts["per_page"] or total >= opts["max_total"]:
                page["left_out_by_cap"] += 1
                continue
            base = os.path.join(out_dir, f"page{page_no:02d}-{kept + 1:02d}")
            try:
                result = download(url, base, opts["max_bytes"])
            except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as exc:
                result = {"skip": str(exc)}
            if "skip" in result:
                page["skipped"].append({"url": url, "reason": result["skip"]})
                continue
            page["images"].append({"url": url, "source": source, **result})
            kept += 1
            total += 1

        if not candidates and page["error"] is None:
            page["note"] = "no image sources in the HTML; the page may render only in JavaScript"

    print(json.dumps({"out_dir": out_dir, "images": total, "pages": pages}, indent=2))


if __name__ == "__main__":
    main()
