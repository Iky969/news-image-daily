#!/usr/bin/env python3
"""Authoring script for entry.png — "19 November 2026, in one image".

Draws a 1024x1024 editorial news illustration with Pillow, composing the
day's stories into one collage:

  * the Xi-Trump-Putin trilateral at APEC in Shenzhen, above a globe
  * missile trails and oil tankers in the Gulf
  * a shattered city, already rebuilding (cranes among the ruins)
  * bombers overhead; ballots and a coin in the foreground

Fixed seed (20261119) makes every run produce the identical picture.
NOTE: running this file REGENERATES entry.png; the committed entry.png is
the canonical artifact for the make.fun entry and should not be overwritten
lightly.

Usage: python3 draw.py [output_path]   (default: entry.png beside this script)
Requires: Pillow
"""

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SEED = 20261119
W = H = 1024

# Editorial palette: night sky, ember horizon, ink silhouettes, paper, gold.
NIGHT = (11, 16, 38)
MID = (35, 48, 94)
EMBER = (179, 85, 47)
INK = (9, 12, 24)
PAPER = (232, 226, 210)
GOLD = (212, 175, 55)
SEA = (24, 52, 84)
STEEL = (120, 132, 156)
ALERT = (222, 90, 60)

GLOBE_CX, GLOBE_CY, GLOBE_R = 512, 810, 310
HORIZON = 660


def font(size, bold=False):
    """DejaVu when available, Pillow's built-in font otherwise."""
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def vertical_gradient(draw, y0, y1, c0, c1):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip(c0, c1))
        draw.line([(0, y), (W, y)], fill=c)


def globe_layer():
    """Wireframe globe with seeded landmasses, clipped to its disc."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, r = GLOBE_CX, GLOBE_CY, GLOBE_R
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(18, 30, 58))
    grid = (70, 86, 120)
    for k in range(1, 6):  # meridians
        rx = r * k / 6
        d.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=grid, width=1)
    for k in (-2, -1, 0, 1, 2):  # parallels
        yy = cy + r * k / 3
        half = math.sqrt(max(0.0, r * r - (yy - cy) ** 2))
        d.ellipse([cx - half, yy - half * 0.18, cx + half, yy + half * 0.18],
                  outline=grid, width=1)
    rng = random.Random(SEED + 1)
    for _ in range(7):  # abstract landmass blobs
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0.15, 0.70) * r
        bx, by = cx + dist * math.cos(ang), cy + dist * math.sin(ang)
        pts = []
        for i in range(9):
            a = 2 * math.pi * i / 9
            rad = rng.uniform(18, 50)
            pts.append((bx + rad * math.cos(a), by + rad * math.sin(a) * 0.7))
        d.polygon(pts, fill=(46, 74, 96))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=STEEL, width=3)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    layer.putalpha(mask)
    return layer


def bomber(draw, x, y, s):
    """Top-down swept-wing silhouette, nose to the right, with contrail."""
    draw.line([(x - 46 * s, y), (x - 46 * s - 140, y)],
              fill=(140, 150, 175), width=2)
    pts = [
        (x, y), (x - 10 * s, y - 3 * s),
        (x - 26 * s, y - 20 * s), (x - 32 * s, y - 18 * s),
        (x - 22 * s, y - 3 * s), (x - 40 * s, y - 2 * s),
        (x - 44 * s, y - 8 * s), (x - 46 * s, y - 7 * s),
        (x - 44 * s, y),
        (x - 46 * s, y + 7 * s), (x - 44 * s, y + 8 * s),
        (x - 40 * s, y + 2 * s), (x - 22 * s, y + 3 * s),
        (x - 32 * s, y + 18 * s), (x - 26 * s, y + 20 * s),
        (x - 10 * s, y + 3 * s),
    ]
    draw.polygon(pts, fill=INK, outline=STEEL)


def summit(draw):
    """Three leaders at one table on a platform resting on the globe."""
    py = 488  # platform top, just above the globe's crown (y=500)
    # banner on poles
    draw.line([(392, 370), (392, 450)], fill=STEEL, width=2)
    draw.line([(632, 370), (632, 450)], fill=STEEL, width=2)
    draw.rectangle([372, 338, 652, 370], fill=INK, outline=GOLD, width=2)
    draw.text((512, 354), "APEC · SHENZHEN", font=font(20, True),
              fill=GOLD, anchor="mm")
    # silhouetted figures
    for fx in (432, 512, 592):
        draw.ellipse([fx - 13, py - 71, fx + 13, py - 45],
                     fill=INK, outline=STEEL)
        draw.rectangle([fx - 5, py - 47, fx + 5, py - 38], fill=INK)
        draw.polygon([(fx - 24, py), (fx - 16, py - 40),
                      (fx + 16, py - 40), (fx + 24, py)],
                     fill=INK, outline=STEEL)
    # table in front of the figures
    draw.rectangle([392, py - 38, 632, py - 10],
                   fill=(58, 42, 28), outline=GOLD, width=2)
    # small table flags: China, USA, Russia
    flags = {
        432: [(222, 60, 50)],
        512: [(70, 80, 150), (235, 235, 235), (222, 60, 50)],
        592: [(240, 240, 240), (70, 90, 170), (222, 60, 50)],
    }
    for fx, cols in flags.items():
        band = 12 // len(cols)
        for i, c in enumerate(cols):
            draw.rectangle([fx - 10, py - 32 + i * band,
                            fx + 10, py - 32 + (i + 1) * band], fill=c)
    # platform
    draw.polygon([(332, py), (692, py), (712, py + 26), (312, py + 26)],
                 fill=INK, outline=STEEL, width=2)
    for fx, name in ((432, "XI"), (512, "TRUMP"), (592, "PUTIN")):
        draw.text((fx, py + 13), name, font=font(12, True),
                  fill=PAPER, anchor="mm")


def tanker(draw, x, y, w):
    """Hull, stern superstructure and deck pipeline."""
    draw.polygon([(x, y), (x + w, y), (x + w - 14, y + 16), (x + 10, y + 16)],
                 fill=INK, outline=STEEL)
    draw.rectangle([x + w - 34, y - 20, x + w - 12, y],
                   fill=INK, outline=STEEL)
    draw.line([(x + w - 23, y - 20), (x + w - 23, y - 30)], fill=STEEL, width=2)
    draw.line([(x + 12, y - 4), (x + w - 38, y - 4)], fill=STEEL, width=2)


def trail(draw, p0, p1):
    """Quadratic missile trail with a warhead glint at the top."""
    x0, y0 = p0
    x1, y1 = p1
    cx = (x0 + x1) / 2 + 30
    cy = min(y0, y1) - 110
    pts = []
    for i in range(41):
        t = i / 40
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1,
                    (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
    draw.line(pts, fill=(150, 60, 40), width=6, joint="curve")
    draw.line(pts, fill=(255, 176, 96), width=2, joint="curve")
    draw.ellipse([x1 - 4, y1 - 4, x1 + 4, y1 + 4], fill=(255, 210, 130))
    draw.ellipse([x0 - 6, y0 - 3, x0 + 6, y0 + 3], fill=(255, 150, 70))


def gulf(draw):
    """Water band on the left: tankers under incoming missile trails."""
    x0, x1, y0, y1 = 20, 270, 600, HORIZON
    draw.rectangle([x0, y0, x1, y1], fill=SEA, outline=STEEL, width=2)
    rng = random.Random(SEED + 2)
    for _ in range(14):  # wave strokes
        yy = rng.randint(y0 + 8, y1 - 6)
        xx = rng.randint(x0 + 4, x1 - 60)
        draw.line([(xx, yy), (xx + rng.randint(20, 50), yy)],
                  fill=(58, 96, 130), width=2)
    tanker(draw, 40, 612, 110)
    tanker(draw, 160, 630, 96)
    trail(draw, (50, 596), (300, 430))
    trail(draw, (120, 592), (360, 470))
    draw.text((24, HORIZON + 12), "THE GULF", font=font(13, True), fill=PAPER)


def crane(draw, x, base_y, h):
    """Tower crane: mast, jib, tie bars, cable and hook load."""
    top = base_y - h
    draw.line([(x, base_y), (x, top)], fill=GOLD, width=3)
    draw.line([(x - 26, top), (x + 70, top)], fill=GOLD, width=3)
    draw.line([(x, top), (x, top - 18)], fill=GOLD, width=2)
    draw.line([(x, top - 18), (x + 70, top)], fill=GOLD, width=1)
    draw.line([(x, top - 18), (x - 26, top)], fill=GOLD, width=1)
    hx = x + 52
    draw.line([(hx, top), (hx, top + 46)], fill=STEEL, width=1)
    draw.rectangle([hx - 8, top + 46, hx + 8, top + 58], fill=STEEL)
    draw.line([(x - 12, base_y), (x + 12, base_y)], fill=GOLD, width=3)


def city(draw):
    """Right-hand skyline: shattered rooftops, rubble, lit windows, cranes."""
    rng = random.Random(SEED + 3)
    x = 790
    while x < 1000:
        w = rng.randint(34, 60)
        h = rng.randint(100, 260)
        top = HORIZON - h
        if rng.random() < 0.45:  # shattered building
            pts = [(x, HORIZON), (x, top + 18)]
            for i in range(5):
                pts.append((int(x + w * i / 4), top + rng.randint(0, 34)))
            pts.append((x + w, HORIZON))
            draw.polygon(pts, fill=(26, 32, 52), outline=STEEL)
            for _ in range(5):  # rubble at the base
                rx = x + rng.randint(-6, w + 6)
                draw.rectangle([rx, HORIZON - 6,
                                rx + rng.randint(4, 10), HORIZON],
                               fill=(40, 46, 66))
        else:  # intact building with lit windows
            draw.rectangle([x, top, x + w, HORIZON],
                           fill=(30, 38, 62), outline=STEEL)
            for wy in range(top + 10, HORIZON - 10, 16):
                for wx in range(x + 6, x + w - 8, 12):
                    if rng.random() < 0.4:
                        draw.rectangle([wx, wy, wx + 5, wy + 7], fill=GOLD)
        x += w + rng.randint(6, 14)
    crane(draw, 812, HORIZON, 268)
    crane(draw, 952, HORIZON, 216)
    draw.text((790, HORIZON + 12), "SHATTERED, REBUILDING",
              font=font(13, True), fill=PAPER)


def ballots(draw, x, y):
    """Ballot box with a paper going into the slot."""
    draw.rectangle([x, y, x + 120, y + 70],
                   fill=(40, 46, 66), outline=PAPER, width=2)
    draw.rectangle([x + 30, y - 4, x + 90, y + 4], fill=INK, outline=PAPER)
    draw.polygon([(x + 44, y - 40), (x + 80, y - 44),
                  (x + 78, y - 2), (x + 46, y - 2)], fill=PAPER)
    draw.line([(x + 52, y - 30), (x + 70, y - 32)], fill=INK, width=2)
    draw.line([(x + 52, y - 20), (x + 70, y - 22)], fill=INK, width=2)
    draw.line([(x + 40, y + 34), (x + 54, y + 48), (x + 84, y + 18)],
              fill=GOLD, width=4)


def coin(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=GOLD, outline=(140, 110, 30), width=3)
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
                 outline=(140, 110, 30), width=2)
    draw.text((cx, cy), "$", font=font(2 * r - 24, True),
              fill=(96, 74, 20), anchor="mm")


def grain(img, rng, amount=9000):
    """Seeded per-pixel jitter for a printed-editorial texture."""
    px = img.load()
    for _ in range(amount):
        x, y = rng.randrange(W), rng.randrange(H)
        r, g, b = px[x, y]
        d = rng.randint(-14, 14)
        px[x, y] = (max(0, min(255, r + d)),
                    max(0, min(255, g + d)),
                    max(0, min(255, b + d)))


def compose():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H), NIGHT)
    draw = ImageDraw.Draw(img)

    # sky, ember horizon, ground
    vertical_gradient(draw, 0, 560, NIGHT, MID)
    vertical_gradient(draw, 560, HORIZON, MID, EMBER)
    draw.rectangle([0, HORIZON, W, H], fill=INK)
    draw.line([(0, HORIZON), (W, HORIZON)], fill=(230, 140, 80), width=2)

    # bombers cross the upper sky
    bomber(draw, 280, 160, 1.7)
    bomber(draw, 540, 205, 1.2)
    bomber(draw, 830, 140, 2.0)

    # globe, then the summit resting on its crown
    globe = globe_layer()
    img.paste(globe, (0, 0), globe)
    summit(draw)

    # regional vignettes
    gulf(draw)
    city(draw)

    # foreground desk: ballots and coin
    draw.rectangle([0, 930, W, H], fill=INK)
    draw.line([(0, 930), (W, 930)], fill=GOLD, width=1)
    ballots(draw, 110, 945)
    coin(draw, 884, 976, 36)
    draw.text((512, 976), "votes and money — the day's two ledgers",
              font=font(17), fill=PAPER, anchor="mm")

    # masthead
    draw.text((512, 50), "19 NOVEMBER 2026", font=font(46, True),
              fill=PAPER, anchor="mm")
    draw.text((512, 92), "the world in one image · make.fun news-image-20261119",
              font=font(18), fill=STEEL, anchor="mm")

    grain(img, rng)
    draw.rectangle([8, 8, W - 9, H - 9], outline=GOLD, width=2)
    return img


def main():
    out = (Path(sys.argv[1]) if len(sys.argv) > 1
           else Path(__file__).resolve().parent / "entry.png")
    img = compose()
    img.save(out, format="PNG", optimize=True)
    print(f"drew {out} ({W}x{H}, seed {SEED})")


if __name__ == "__main__":
    main()
