#!/usr/bin/env python3
"""Fetch a project writeup from a GitHub repo and localize its image assets.

Mechanical half of the `publish-writeup` skill: it downloads the article
markdown and every image it references into the al-folio site's assets, then
prints a ref -> local-path mapping that Claude uses to rewrite the post into
`figure.liquid` includes. Stdlib only (no pip installs).

Usage:
  localize_assets.py --repo OWNER/NAME --article PATH/IN/REPO.md --slug SLUG \
      [--ref BRANCH] [--site-root .] [--save-article DRAFT_SRC.md]

Example (the CWRU migration this skill was modeled on):
  localize_assets.py --repo godot107/predictive-maintenance-cwru \
      --article blog/medium_article.md --slug predictive-maintenance-cwru \
      --save-article /tmp/writeup_src.md

What it does:
  * downloads <raw>/<article> and (optionally) saves it for Claude to read;
  * finds markdown ![alt](url) and <img src="..."> references;
  * resolves absolute URLs and repo-relative paths (relative to the article dir);
  * downloads real images into <site-root>/assets/img/<slug>/;
  * skips embeds/tracking pixels/non-images and reports them;
  * prints a mapping table + summary (and exits non-zero if any image failed).
"""
import argparse
import os
import posixpath
import re
import sys
import urllib.request
from urllib.parse import urlparse

IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
SKIP_HINTS = ("embedly", "/embed", "/_/stat", "/stat?", "emoji", "avatar", "badge", "shield")
MD_IMG = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
HTML_IMG = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "publish-writeup-skill"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def is_image_ref(ref: str) -> bool:
    if ref.startswith("data:") or any(h in ref for h in SKIP_HINTS):
        return False
    path = urlparse(ref).path if "://" in ref else ref
    return path.lower().endswith(IMG_EXT)


def resolve_url(ref: str, raw_base: str, article_dir: str) -> str:
    if ref.startswith(("http://", "https://")):
        return ref
    rel = ref.lstrip("/") if ref.startswith("/") else posixpath.join(article_dir, ref)
    return f"{raw_base}/{posixpath.normpath(rel)}"


def unique_name(dest_dir: str, name: str, taken: set) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name) or "asset.png"
    base, ext = os.path.splitext(name)
    candidate, i = name, 1
    while candidate in taken or os.path.exists(os.path.join(dest_dir, candidate)):
        candidate, i = f"{base}_{i}{ext}", i + 1
    taken.add(candidate)
    return candidate


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="OWNER/NAME")
    ap.add_argument("--article", required=True, help="path to the .md inside the repo")
    ap.add_argument("--slug", required=True, help="asset folder slug under assets/img/")
    ap.add_argument("--ref", default="main", help="branch/tag/sha (default: main)")
    ap.add_argument("--site-root", default=".", help="al-folio site root (default: cwd)")
    ap.add_argument("--save-article", help="also write the fetched markdown here")
    args = ap.parse_args()

    raw_base = f"https://raw.githubusercontent.com/{args.repo}/{args.ref}"
    article_dir = posixpath.dirname(args.article)
    article_url = f"{raw_base}/{args.article}"

    try:
        md = fetch(article_url).decode("utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"ERROR fetching article {article_url}: {e}", file=sys.stderr)
        return 2
    if args.save_article:
        with open(args.save_article, "w", encoding="utf-8") as fh:
            fh.write(md)

    refs, seen = [], set()
    for m in list(MD_IMG.finditer(md)) + list(HTML_IMG.finditer(md)):
        ref = m.group(1).strip()
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)

    dest_dir = os.path.join(args.site_root, "assets", "img", args.slug)
    os.makedirs(dest_dir, exist_ok=True)
    rel_root = os.path.join("assets", "img", args.slug)

    mapping, skipped, failed, taken = [], [], [], set()
    for ref in refs:
        if not is_image_ref(ref):
            skipped.append(ref)
            continue
        url = resolve_url(ref, raw_base, article_dir)
        fname = unique_name(dest_dir, posixpath.basename(urlparse(url).path), taken)
        try:
            data = fetch(url)
            with open(os.path.join(dest_dir, fname), "wb") as fh:
                fh.write(data)
            mapping.append((ref, f"{rel_root}/{fname}"))
        except Exception as e:  # noqa: BLE001
            failed.append((ref, str(e)))

    print(f"# article: {article_url}")
    if args.save_article:
        print(f"# saved markdown -> {args.save_article}")
    print(f"# assets dir: {dest_dir}\n")
    print("## ref -> local path (rewrite these to figure.liquid includes)")
    for ref, local in mapping:
        print(f"  {ref}\n    -> {local}")
    if skipped:
        print("\n## skipped (not an image / embed / tracking — handle manually if a hero):")
        for ref in skipped:
            print(f"  {ref}")
    if failed:
        print("\n## FAILED downloads:")
        for ref, err in failed:
            print(f"  {ref}  ({err})")
    print(f"\n# summary: {len(mapping)} localized, {len(skipped)} skipped, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
