#!/usr/bin/env python3
"""Square cover images (1000x1000) for posts: one big, real number or picture, readable at LinkedIn-card size.

Each cover is used as the post's `thumbnail` (blog list) and, via bin/make_og_cards.py, as the right-hand
panel of its 1200x630 LinkedIn card. Every number drawn here is quoted from the post itself.

    python bin/make_covers.py            # all covers
    python bin/make_covers.py great-war  # one
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W = H = 1000
S = 2  # supersample
BG, INK, MUTED = (243, 245, 249), (24, 28, 36), (96, 103, 116)
BLUE, RED, GREEN, ORANGE, GREY = (46, 111, 216), (210, 69, 59), (31, 138, 80), (214, 120, 20), (178, 186, 198)
NOTO = Path("/usr/share/fonts/truetype/noto")


def F(size, bold=True):
    return ImageFont.truetype(str(NOTO / ("NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf")), int(size * S))


def canvas(tag):
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    d.text((60 * S, 56 * S), tag.upper(), font=F(26), fill=BLUE)
    return im, d


def save(im, rel):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    im.resize((W, H), Image.LANCZOS).save(out)
    print("wrote", rel)


def P(*xy):
    return tuple(v * S for v in xy)


# --------------------------------------------------------------------------- posts
def great_war():
    data = json.loads((ROOT.parent / "family-tree/docs/story/data.json").read_text())["cousins_war"]
    sparse = {s.split(" (")[0] + "|" + s.split("(")[1].rstrip(")") for s in data["sparse"]}
    mons = [m for m in data["monarchs"] if f"{m['name']}|{m['country']}" not in sparse]
    assert len(mons) == 16
    im, d = canvas("1914 · sixteen monarchs")
    cx, cy, r = 500, 540, 300
    pos = {}
    order = [m for m in mons if m["side"] == "Allies"] + [m for m in mons if m["side"] == "Neutral"] + \
            [m for m in mons if m["side"] == "Central Powers"]
    for i, m in enumerate(order):
        a = -math.pi / 2 + 2 * math.pi * i / len(order)
        pos[m["id"]] = (cx + r * math.cos(a), cy + r * math.sin(a))
    side = {m["id"]: m["side"] for m in mons}
    ids = list(pos)
    enemy = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            if {side[a], side[b]} == {"Allies", "Central Powers"}:
                enemy.append((a, b))
            else:
                d.line(P(*pos[a], *pos[b]), fill=GREY, width=2 * S)
    for a, b in enemy:
        d.line(P(*pos[a], *pos[b]), fill=RED, width=4 * S)
    col = {"Allies": BLUE, "Central Powers": RED, "Neutral": MUTED}
    for m in order:
        x, y = pos[m["id"]]
        d.ellipse(P(x - 16, y - 16, x + 16, y + 16), fill=col[m["side"]], outline="white", width=4 * S)
    for name in ("George V", "Wilhelm II", "Nicholas II"):
        m = next(m for m in order if m["name"] == name)
        x, y = pos[m["id"]]
        ang = math.atan2(y - cy, x - cx)
        lx, ly = x + 34 * math.cos(ang), y + 34 * math.sin(ang)
        anchor = ("l" if math.cos(ang) > 0.3 else "r" if math.cos(ang) < -0.3 else "m") + ("b" if math.sin(ang) < -0.5 else "m")
        d.text(P(lx, ly), name, font=F(24), fill=INK, anchor=anchor)
    d.rounded_rectangle(P(330, 455, 670, 625), 24 * S, fill="white")
    d.text(P(500, 515), "120 / 120", font=F(64), fill=INK, anchor="mm")
    d.text(P(500, 580), "pairs related", font=F(28, False), fill=MUTED, anchor="mm")
    for i, (lab, c) in enumerate([("Allies", BLUE), ("Central Powers", RED), ("Neutral", MUTED)]):
        d.ellipse(P(620 + 0, 110 + i * 34, 640, 130 + i * 34), fill=c)
        d.text(P(652, 120 + i * 34), lab, font=F(22, False), fill=INK, anchor="lm")
    d.text(P(60, 935), "Red: the 15 pairs whose countries fought. All related.", font=F(27, False), fill=INK, anchor="lm")
    save(im, "assets/img/family-tree/cover.png")


def congress_417():
    im, d = canvas("U.S. House · energy votes")

    def bar(y, title, yes, no, note):
        d.text(P(60, y), title, font=F(34), fill=INK, anchor="lm")
        x0, x1 = 60, 940
        split = x0 + (x1 - x0) * yes / (yes + no)
        d.rounded_rectangle(P(x0, y + 40, x1, y + 130), 18 * S, fill=RED)
        d.rounded_rectangle(P(x0, y + 40, split, y + 130), 18 * S, fill=GREEN)
        if split < x1 - 30:
            d.rectangle(P(split - 20, y + 40, split, y + 130), fill=GREEN)
        d.text(P(x0 + 26, y + 85), f"{yes} yes", font=F(40), fill="white", anchor="lm")
        d.text(P(x1 + 0, y + 170), note, font=F(27, False), fill=MUTED, anchor="rm")
        d.text(P(x0, y + 170), f"{no} no", font=F(30), fill=RED, anchor="lm")

    bar(190, "GRID Power Act", 216, 206, "a party-line split")
    bar(520, "Data-center power costs", 417, 3, "almost everyone agreed")
    d.text(P(60, 935), "83% of energy votes split on party lines. Not this one.", font=F(27, False), fill=INK, anchor="lm")
    save(im, "assets/img/congress-issues/cover.png")


def factions():
    im, d = canvas("PCA vs the standard ideology scores")
    rows = [("All members", 0.97, GREY), ("Within Republicans", 0.82, RED), ("Within Democrats", 0.52, BLUE)]
    for i, (lab, v, c) in enumerate(rows):
        y = 220 + i * 210
        d.text(P(60, y), lab, font=F(34), fill=INK, anchor="lm")
        d.rounded_rectangle(P(60, y + 40, 940, y + 120), 16 * S, fill=(226, 230, 237))
        d.rounded_rectangle(P(60, y + 40, 60 + 880 * v, y + 120), 16 * S, fill=c)
        d.text(P(60 + 880 * v - 24, y + 80), f"{v:.2f}", font=F(46), fill="white", anchor="rm")
    d.text(P(60, 880), "Separating the parties is the easy part.", font=F(32), fill=INK, anchor="lm")
    d.text(P(60, 932), "Correlation with DW-NOMINATE, 118th House", font=F(26, False), fill=MUTED, anchor="lm")
    save(im, "assets/img/ideology-clusters/cover.png")


def eval_lab():
    im, d = canvas("1 case in 100 is positive")
    for i, (lab, sub, c) in enumerate([("My model", "trained, tuned", BLUE), ("Always says \"no\"", "does nothing", GREY)]):
        x0 = 60 + i * 450
        d.rounded_rectangle(P(x0, 200, x0 + 430, 700), 28 * S, fill="white", outline=(220, 225, 233), width=3 * S)
        d.rounded_rectangle(P(x0, 200, x0 + 430, 226), 0, fill=c)
        d.text(P(x0 + 215, 330), lab, font=F(36), fill=INK, anchor="mm")
        d.text(P(x0 + 215, 380), sub, font=F(26, False), fill=MUTED, anchor="mm")
        d.text(P(x0 + 215, 520), "99.0%", font=F(96), fill=c if i == 0 else MUTED, anchor="mm")
        d.text(P(x0 + 215, 610), "accuracy", font=F(30, False), fill=MUTED, anchor="mm")
    d.text(P(500, 790), "Same score.", font=F(48), fill=INK, anchor="mm")
    d.text(P(500, 860), "Accuracy can't tell your model from doing nothing.", font=F(27, False), fill=MUTED, anchor="mm")
    save(im, "assets/img/eval-lab/cover.png")


def ab_test():
    im, d = canvas("Same real effect, three test runs")
    x0, x1, zero = 120, 900, 120
    scale = (x1 - x0) / 25  # points 0..25
    true_x = x0 + 12 * scale
    runs = [("Run 1", 12.05, 4.6, 19.5, GREEN, "significant"), ("Run 2", 5.6, -1.9, 13.1, ORANGE, "inconclusive (p = 0.14)"),
            ("Run 3", 18.6, 11.1, 26.1, GREEN, "significant, overshoots")]
    d.line(P(true_x, 170, true_x, 760), fill=INK, width=3 * S)
    d.text(P(true_x, 790), "true lift: +12 points", font=F(28), fill=INK, anchor="mm")
    for i, (lab, m, lo, hi, c, note) in enumerate(runs):
        y = 260 + i * 180
        lo_x, hi_x = max(x0 - 60, x0 + lo * scale), min(x1 + 60, x0 + hi * scale)
        d.line(P(lo_x, y, hi_x, y), fill=c, width=8 * S)
        d.ellipse(P(x0 + m * scale - 22, y - 22, x0 + m * scale + 22, y + 22), fill=c, outline="white", width=4 * S)
        d.text(P(60, y - 58), f"{lab}: +{m:g}", font=F(32), fill=INK, anchor="lm")
        d.text(P(940, y - 58), note, font=F(26, False), fill=c, anchor="rm")
    d.text(P(60, 935), "\"Not significant\" means \"too small to measure\", not \"no effect\".", font=F(27, False), fill=INK, anchor="lm")
    save(im, "assets/img/ab-lab/cover.png")


def fpa():
    im, d = canvas("Netflix SEC filings · automated controls")
    d.text(P(500, 330), "$1.83 billion", font=F(120), fill=RED, anchor="mm")
    d.text(P(500, 440), "error, in a number that looked reasonable", font=F(34, False), fill=INK, anchor="mm")
    d.rounded_rectangle(P(140, 540, 860, 700), 24 * S, fill="white", outline=(220, 225, 233), width=3 * S)
    d.text(P(500, 590), "Control: pretax - tax = net income", font=F(32), fill=INK, anchor="mm")
    d.text(P(500, 650), "FAILED: the pipeline stopped", font=F(34), fill=RED, anchor="mm")
    d.text(P(500, 800), "5 defects I would not have found by reading the code", font=F(34), fill=INK, anchor="mm")
    save(im, "assets/img/auditable-fpa-forecast/cover.png")


COVERS = {"great-war": great_war, "congress-417": congress_417, "factions": factions, "eval-lab": eval_lab,
          "ab-test": ab_test, "fpa": fpa}

if __name__ == "__main__":
    for name in (sys.argv[1:] or COVERS):
        COVERS[name]()
