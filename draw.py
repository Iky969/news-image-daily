"""Draws entry.png for the 19 Nov 2026 news-image bounty.

Everything is computed from a fixed seed, so the committed PNG is reproducible
and the entry program can simply copy it to /output with no network or deps.
Run with Pillow at authoring time:  python3 draw.py
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import random

W = H = 1024
random.seed(19112026)

NAVY = (9, 21, 36)
NAVY2 = (20, 39, 58)
CREAM = (239, 226, 198)
GOLD = (226, 177, 86)
RED = (198, 62, 48)
RED2 = (240, 118, 62)
SLATE = (96, 121, 140)
DARK = (6, 14, 25)


def gradient():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / H
        # deep navy at top, slightly warmer slate at horizon, dark at bottom
        if t < 0.62:
            k = t / 0.62
            c = (int(NAVY[0] + (NAVY2[0] - NAVY[0]) * k),
                 int(NAVY[1] + (NAVY2[1] - NAVY[1]) * k),
                 int(NAVY[2] + (NAVY2[2] - NAVY[2]) * k))
        else:
            k = (t - 0.62) / 0.38
            c = (int(NAVY2[0] * (1 - k) + DARK[0] * k),
                 int(NAVY2[1] * (1 - k) + DARK[1] * k),
                 int(NAVY2[2] * (1 - k) + DARK[2] * k))
        for x in range(W):
            px[x, y] = c
    return im


def glow(im, cx, cy, r, color, strength=110):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.55))
    lpx, ipx = layer.load(), im.load()
    for y in range(H):
        for x in range(W):
            v = lpx[x, y]
            if v[0] or v[1] or v[2]:
                f = strength / 255.0
                ipx[x, y] = tuple(min(255, int(ipx[x, y][i] + v[i] * f)) for i in range(3))


def silhouette(d, cx, head_y, scale, tint):
    """A suited leader seen from behind: shoulders, neck, head."""
    s = scale
    # torso / shoulders
    d.polygon([
        (cx - 105 * s, head_y + 250 * s), (cx - 96 * s, head_y + 118 * s),
        (cx - 58 * s, head_y + 80 * s), (cx - 28 * s, head_y + 66 * s),
        (cx + 28 * s, head_y + 66 * s), (cx + 58 * s, head_y + 80 * s),
        (cx + 96 * s, head_y + 118 * s), (cx + 105 * s, head_y + 250 * s),
    ], fill=tint)
    # neck
    d.rectangle((cx - 20 * s, head_y + 48 * s, cx + 20 * s, head_y + 76 * s), fill=tint)
    # head
    d.ellipse((cx - 39 * s, head_y, cx + 39 * s, head_y + 70 * s), fill=tint)
    # subtle lapel line
    d.line((cx, head_y + 90 * s, cx, head_y + 245 * s), fill=(22, 36, 52), width=max(1, int(3 * s)))


def skyline(d, y0, alpha_color, seed):
    r = random.Random(seed)
    x = 0
    while x < W:
        bw = r.randint(26, 60)
        bh = r.randint(40, 165)
        d.rectangle((x, y0 - bh, x + bw, y0), fill=alpha_color)
        # lit windows
        for wy in range(y0 - bh + 8, y0 - 6, 12):
            for wx in range(x + 5, x + bw - 5, 11):
                if r.random() < 0.35:
                    d.rectangle((wx, wy, wx + 3, wy + 5), fill=GOLD)
        x += bw + r.randint(3, 10)


def missile(d, x1, y1, x2, y2, color):
    d.line((x1, y1, x2, y2), fill=color, width=3)
    for k in range(6):
        t = k / 6
        cx = x1 + (x2 - x1) * t
        cy = y1 + (y2 - y1) * t
        d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=RED2)


def main():
    im = gradient()
    glow(im, 512, 372, 250, (120, 88, 38), 90)

    # distant Shenzhen skyline behind the summit
    sky = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sky)
    skyline(sd, 470, (28, 50, 70, 255), 7)
    sd.rectangle((0, 466, W, 470), fill=(35, 60, 80, 255))
    im = Image.alpha_composite(im.convert("RGBA"), sky).convert("RGB")
    d = ImageDraw.Draw(im)

    # globe
    gx, gy, gr = 512, 372, 168
    d.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(19, 48, 68), outline=GOLD, width=4)
    for i in range(1, 5):
        rr = gr * i / 5
        d.arc((gx - rr, gy - rr, gx + rr, gy + rr), 0, 360, fill=(46, 86, 108), width=2)
    for i in (0.3, 0.62):
        yy = gy - gr + 2 * gr * i
        rx = math.sqrt(max(0.0, 1 - ((yy - gy) / gr) ** 2)) * gr
        d.arc((gx - rx, yy - 18, gx + rx, yy + 18), 0, 360, fill=(52, 96, 118), width=2)
    d.line((gx - gr, gy, gx + gr, gy), fill=(52, 96, 118), width=2)
    d.line((gx, gy - gr, gx, gy + gr), fill=(52, 96, 118), width=2)
    # hotspots on the globe
    for hx, hy, col, rad in [(gx - 70, gy - 40, RED, 11), (gx + 55, gy - 25, RED2, 9), (gx + 18, gy + 62, GOLD, 7)]:
        d.ellipse((hx - rad * 2, hy - rad * 2, hx + rad * 2, hy + rad * 2), outline=col, width=2)
        d.ellipse((hx - rad, hy - rad, hx + rad, hy + rad), fill=col)

    # three leaders, backs to viewer, around the globe
    silhouette(d, 268, 250, 1.18, (8, 17, 29))
    silhouette(d, 512, 214, 1.30, (11, 22, 36))
    silhouette(d, 756, 250, 1.18, (8, 17, 29))

    # left vignette: Gulf war, tankers, refinery fire
    d.polygon([(0, 690), (340, 690), (300, 860), (0, 880)], fill=(16, 38, 56))
    for bx, by, bw, bh in [(40, 700, 45, 95), (100, 720, 38, 75), (150, 690, 30, 105)]:
        d.rectangle((bx, by, bx + bw, by + bh), fill=(28, 45, 58))
        d.rectangle((bx + 8, by - 30, bx + 20, by), fill=(44, 60, 72))
    for fx, fy, fs in [(60, 650, 26), (128, 672, 20), (178, 640, 15)]:
        d.polygon([(fx, fy - fs), (fx + fs * .55, fy), (fx - fs * .55, fy)], fill=RED2)
        d.polygon([(fx, fy - fs * .6), (fx + fs * .3, fy), (fx - fs * .3, fy)], fill=GOLD)
    missile(d, 250, 700, 60, 610, RED2)
    missile(d, 285, 730, 110, 650, RED)
    for tx in (210, 280, 340):
        d.polygon([(tx, 820), (tx + 60, 820), (tx + 48, 838), (tx + 10, 838)], fill=(60, 84, 98))
        d.rectangle((tx + 25, 806, tx + 38, 820), fill=(60, 84, 98))

    # right vignette: shattered city, reconstruction crane, bridge of light
    d.polygon([(690, 700), (1024, 680), (1024, 885), (720, 865)], fill=(16, 38, 56))
    r = random.Random(11)
    for bx in range(710, 1020, 46):
        bh = r.randint(60, 190)
        d.rectangle((bx, 700 - bh, bx + 38, 700), fill=(28, 46, 63))
        for wy in range(710 - bh, 690, 14):
            for wx in range(bx + 5, bx + 34, 10):
                if r.random() < 0.3:
                    d.rectangle((wx, wy, wx + 3, wy + 5), fill=GOLD)
    d.line((700, 690, 1010, 660), fill=GOLD, width=3)
    d.line((700, 700, 1010, 670), fill=(120, 90, 45), width=2)

    # bomber silhouettes crossing the upper sky
    for bx, by, bs in [(120, 200, 1.0), (830, 170, .85)]:
        d.polygon([(bx - 40 * bs, by), (bx + 30 * bs, by), (bx + 44 * bs, by - 6 * bs),
                   (bx - 20 * bs, by - 6 * bs)], fill=(70, 92, 108))
        d.line((bx - 10 * bs, by, bx - 40 * bs, by + 10 * bs), fill=(70, 92, 108), width=3)

    # foreground: scattered ballots and a toppled coin (politics / elections)
    for i in range(7):
        bx, by = 380 + i * 38, 905 + (i % 3) * 18
        d.rectangle((bx, by, bx + 26, by + 36), fill=CREAM)
        d.line((bx + 4, by + 12, bx + 21, by + 12), fill=SLATE, width=2)
        d.line((bx + 4, by + 20, bx + 17, by + 20), fill=SLATE, width=2)
    d.ellipse((700, 900, 770, 970), fill=GOLD, outline=CREAM, width=3)
    d.ellipse((710, 910, 760, 960), fill=(180, 132, 60))

    # frame
    d.rectangle((18, 18, W - 18, H - 18), outline=(120, 98, 62), width=3)

    # fine grain, deterministic
    px = im.load()
    for y in range(H):
        for x in range(W):
            n = random.randint(-6, 6)
            px[x, y] = tuple(max(0, min(255, c + n)) for c in px[x, y])

    im.save("entry.png", "PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
