#!/usr/bin/env python3
"""Build a 1200x630 LinkedIn/Open Graph card for each blog post.

Card = post title (left) + the post's `thumbnail` figure (right), in the same
dark style as assets/img/og-default.png. Output goes to assets/img/og/<slug>.png
Optional front matter: `og_figure:` (use a different image than the thumbnail),
`og_tag:` (small accent label above the title). The post's front matter gets `og_image:` pointing at it (absolute URL).

Usage:
    python bin/make_og_cards.py                 # every post missing og_image
    python bin/make_og_cards.py --force         # rebuild all
    python bin/make_og_cards.py _posts/X.md     # specific posts (always rebuilt)

After pushing, refresh LinkedIn's cache at https://www.linkedin.com/post-inspector/
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets/img/og"
SITE = "https://willieman.com"

W, H = 1200, 630
BG = (17, 20, 27)
ACCENT = (77, 158, 255)
TITLE = (245, 247, 250)
MUTED = (160, 168, 180)
FONT_DIR = Path("/usr/share/fonts/truetype/noto")
BOLD = str(FONT_DIR / "NotoSans-Bold.ttf")
REG = str(FONT_DIR / "NotoSans-Regular.ttf")

LEFT = 70            # text column x
TEXT_W = 520         # text column width
PANEL = (640, 60, 1150, 570)  # image panel box (x0, y0, x1, y1)


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, {}
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith(" "):
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return m, fm


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_title(draw, title):
    """Largest font size (60 down to 34) whose wrapped title fits 5 lines."""
    for size in range(60, 33, -2):
        font = ImageFont.truetype(BOLD, size)
        lines = wrap(draw, title, font, TEXT_W)
        if len(lines) <= 5:
            return font, lines
    return font, lines[:5]


def trim(fig):
    """Crop near-white margins so the figure fills its panel."""
    mask = ImageOps.invert(fig.convert("L")).point(lambda v: 255 if v > 12 else 0)
    box = mask.getbbox()
    if not box:
        return fig
    m = 10
    return fig.crop((max(box[0] - m, 0), max(box[1] - m, 0),
                     min(box[2] + m, fig.width), min(box[3] + m, fig.height)))


def paste_panel(img, d, fig, panel):
    """Figure on a white rounded panel, letterboxed so nothing is cropped."""
    x0, y0, x1, y1 = panel
    d.rounded_rectangle(panel, radius=18, fill=(255, 255, 255))
    pad = 16
    fig = ImageOps.contain(fig, (x1 - x0 - 2 * pad, y1 - y0 - 2 * pad), Image.LANCZOS)
    img.paste(fig, (x0 + (x1 - x0 - fig.width) // 2, y0 + (y1 - y0 - fig.height) // 2))


def footer(d):
    f = ImageFont.truetype(REG, 28)
    d.text((LEFT, H - 90), "willieman.com", font=f, fill=ACCENT)
    d.text((LEFT + d.textlength("willieman.com  ", font=f), H - 90), "· Willie Man", font=f, fill=MUTED)


def save(img, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)


def card(title, thumb, tag, out):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 14, H], fill=ACCENT)
    fig = trim(Image.open(thumb).convert("RGB"))

    if fig.width / fig.height > 1.8:
        # Wide figure: title across the top, figure full-width below.
        for size in range(52, 31, -2):
            font = ImageFont.truetype(BOLD, size)
            lines = wrap(d, title, font, W - LEFT - 60)
            if len(lines) <= 2:
                break
        y = 50
        for line in lines[:2]:
            d.text((LEFT, y), line, font=font, fill=TITLE)
            y += int(font.size * 1.2)
        paste_panel(img, d, fig, (LEFT, y + 25, W - 50, H - 110))
        footer(d)
        return save(img, out)

    paste_panel(img, d, fig, PANEL)

    # Title, vertically centred in the text column.
    font, lines = fit_title(d, title)
    lh = int(font.size * 1.22)
    block = lh * len(lines)
    y = (H - block) // 2 - 20
    if tag:
        d.text((LEFT, y - 56), tag.upper(), font=ImageFont.truetype(BOLD, 22), fill=ACCENT)
    for line in lines:
        d.text((LEFT, y), line, font=font, fill=TITLE)
        y += lh

    footer(d)
    save(img, out)


def process(post, force):
    text = post.read_text()
    m, fm = front_matter(text)
    if not m or "thumbnail" not in fm:
        print(f"skip (no thumbnail): {post.name}")
        return
    if "og_image" in fm and not force:
        return
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post.stem)
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    out = OUT_DIR / f"{slug}.png"
    card(fm.get("title", slug), ROOT / fm.get("og_figure", fm["thumbnail"]), fm.get("og_tag", ""), out)
    url = f"{SITE}/assets/img/og/{slug}.png"
    block = m.group(0)
    if "og_image" in fm:
        new = re.sub(r"(?m)^og_image:.*$", f"og_image: {url}", block)
    else:
        new = block.replace(f"thumbnail: {fm['thumbnail']}", f"thumbnail: {fm['thumbnail']}\nog_image: {url}", 1)
    post.write_text(text.replace(block, new, 1))
    print(f"wrote {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts", nargs="*", type=Path)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    posts = a.posts or sorted((ROOT / "_posts").glob("*.md"))
    for p in posts:
        process(p, a.force or bool(a.posts))


if __name__ == "__main__":
    sys.exit(main())
