# VELMORA — a travel poster for a place that does not exist.
# gta6-style MakeFun bounty: the-poster-for-a-place-that-i-2-20261121-0539
#
# The place: VELMORA, a desert valley where one giant crystal spire rises
# out of the dunes at dusk. Violet sky melting into amber at the horizon,
# a low sun, a teal crystal glowing against the dark, and a tiny caravan
# crossing the dunes for scale. Palette is 4 colours: violet, amber,
# teal, dark plum.
#
# Everything is drawn with PIL only — no network, no downloaded assets.
# Writes /output/entry.png (1024x1024, PNG, under 1 MiB).
#
# Usage (local check):
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")

# --- palette ---------------------------------------------------------------
VIOLET_TOP = (38, 24, 74)       # deep dusk violet, top of sky
VIOLET_MID = (96, 52, 110)      # purple band
AMBER = (232, 130, 63)          # horizon glow
SUN_CORE = (255, 216, 138)      # low sun
SUN_HALO = (255, 178, 92)
TEAL_HI = (201, 255, 242)       # crystal highlight facet
TEAL_MID = (88, 216, 200)       # crystal main facet
TEAL_DARK = (28, 128, 128)      # crystal shadow facet
TEAL_GLOW = (64, 200, 190)
DUNE_FAR = (74, 42, 66)         # far dune
DUNE_NEAR = (42, 24, 48)        # near dune, darkest
CREAM = (255, 246, 224)         # place-name type
SHADOW = (24, 12, 40)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def vertical_gradient(size, stops):
    """Blend `stops` (list of (y_frac, rgb)) top to bottom."""
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    n = len(stops)
    for y in range(h):
        f = y / max(h - 1, 1)
        # find the segment
        for i in range(n - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                t = 0.0 if f1 == f0 else (f - f0) / (f1 - f0)
                px_color = tuple(
                    int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3)
                )
                break
        else:
            px_color = stops[-1][1]
        for x in range(w):
            px[x, y] = px_color
    return img


def draw_glow(base, cx, cy, rx, ry, color, blur):
    """Soft elliptical glow on its own layer, blurred, composited."""
    layer = Image.new("RGB", base.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(base, Image.composite(layer, base, layer.convert("L").point(lambda v: v)), 1.0)


def smooth_dune(draw, y_base, amp, phase, color, x0=0, x1=W, step=8):
    """A dune ridge: filled polygon whose top edge is a sine curve."""
    pts = [(x0, H)]
    for x in range(x0, x1 + 1, step):
        y = y_base + amp * math.sin((x / W) * math.pi * 1.6 + phase)
        pts.append((x, y))
    pts.append((x1, H))
    draw.polygon(pts, fill=color)


def draw_crystal(draw, apex, base_y, half_w, facets):
    """Tall faceted spire. apex=(x,y); facets: list of (polygon, color)."""
    for poly, color in facets:
        draw.polygon(poly, fill=color)
    # thin bright edge on the sun side
    draw.line([apex, (apex[0] - half_w, base_y)], fill=TEAL_HI, width=4)


def main():
    random.seed(20261121)

    # --- sky: violet dusk melting into amber at the horizon ---------------
    sky = vertical_gradient(
        (W, H),
        [
            (0.00, VIOLET_TOP),
            (0.38, VIOLET_MID),
            (0.58, (176, 92, 96)),
            (0.66, AMBER),
            (1.00, AMBER),
        ],
    )

    # --- faint stars in the upper sky --------------------------------------
    d = ImageDraw.Draw(sky, "RGBA")
    for _ in range(90):
        x = random.randint(0, W - 1)
        y = random.randint(0, 300)
        r = random.choice([1, 1, 2])
        a = random.randint(60, 170)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 244, 220, a))

    # --- sun glow + sun, low on the left, just above the horizon ----------
    sun_x, sun_y, sun_r = 300, 565, 52
    sky = draw_glow(sky, sun_x, sun_y, 190, 130, SUN_HALO, 60)
    d = ImageDraw.Draw(sky, "RGBA")
    d.ellipse(
        [sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r],
        fill=SUN_CORE + (255,),
    )
    # sun sits half behind the far dune: redraw a soft lower half later

    # --- the crystal spire: one dominant landmark, centre-right -----------
    # glow behind the crystal so it reads as the light source of the valley
    sky = draw_glow(sky, 640, 440, 150, 260, TEAL_GLOW, 70)
    d = ImageDraw.Draw(sky, "RGBA")
    apex = (640, 250)
    base_y = 690
    half_w = 105
    # facet polygons (left = sunlit, right = shadow)
    left_facet = [apex, (apex[0] - half_w, base_y), (apex[0] - 18, base_y)]
    mid_facet = [apex, (apex[0] - 18, base_y), (apex[0] + 30, base_y)]
    right_facet = [apex, (apex[0] + 30, base_y), (apex[0] + half_w, base_y)]
    # a small notch cut near the top for a faceted silhouette
    notch = [(640, 250), (612, 310), (640, 337), (668, 310)]
    draw_crystal(d, apex, base_y, half_w,
                 [(left_facet, TEAL_HI), (mid_facet, TEAL_MID),
                  (right_facet, TEAL_DARK)])
    d.polygon(notch, fill=TEAL_DARK)
    # bright core line down the sunlit edge
    d.line([apex, (apex[0] - half_w, base_y)], fill=(235, 255, 248, 255), width=5)
    # small shard crystals at the base
    for sx, sw, sh in [(505, 34, 120), (742, 28, 95), (700, 20, 70)]:
        shard = [(sx, base_y - sh), (sx - sw, base_y), (sx + sw, base_y)]
        d.polygon(shard, fill=TEAL_MID)
        d.polygon([(sx, base_y - sh), (sx - sw, base_y), (sx, base_y)],
                  fill=TEAL_HI)

    # --- dunes: three ridges, far to near, crystal base tucked behind ------
    def dune_y(x, y_base=640, amp=26, phase=0.4):
        return y_base + amp * math.sin((x / W) * math.pi * 1.6 + phase)

    smooth_dune(d, 640, 26, 0.4, DUNE_FAR)
    # tiny caravan walking ON the far ridge, for scale
    for cx in (330, 395, 460):
        gy = dune_y(cx)
        # camel: body + hump, long neck + head, four legs, rider
        d.ellipse([cx - 18, gy - 16, cx + 18, gy + 2], fill=SHADOW)
        d.ellipse([cx - 9, gy - 26, cx + 9, gy - 10], fill=SHADOW)
        d.polygon([(cx + 10, gy - 12), (cx + 24, gy - 34),
                   (cx + 30, gy - 32), (cx + 18, gy - 8)], fill=SHADOW)
        d.ellipse([cx + 22, gy - 38, cx + 33, gy - 28], fill=SHADOW)
        for lx in (cx - 11, cx - 3, cx + 5, cx + 13):
            d.line([(lx, gy), (lx, gy + 13)], fill=SHADOW, width=3)
        d.ellipse([cx - 5, gy - 34, cx + 5, gy - 24], fill=SHADOW)
    smooth_dune(d, 700, 22, 1.2, (58, 32, 56))
    smooth_dune(d, 760, 34, 2.2, DUNE_NEAR)
    # re-draw the crystal base over the far dune so the spire sits IN the valley
    d.polygon([(505, 690), (505 - 34, 690), (505, 570)], fill=TEAL_MID)

    # --- birds --------------------------------------------------------------
    for bx, by, s in [(180, 210, 14), (240, 180, 11), (830, 250, 13), (880, 205, 10)]:
        d.line([(bx - s, by), (bx, by - 6), (bx + s, by)], fill=(30, 16, 44, 220),
               width=3)

    # --- the place name: VELMORA, large, letterspaced, top centre ---------
    name = "VELMORA"
    target_w = 840
    size = 200
    font = ImageFont.truetype(FONT_PATH, size)
    # fit width by shrinking the font
    while True:
        widths = [font.getbbox(ch)[2] for ch in name]
        total = sum(widths) + 26 * (len(name) - 1)
        if total <= target_w or size <= 60:
            break
        size -= 4
        font = ImageFont.truetype(FONT_PATH, size)
    widths = [font.getbbox(ch)[2] for ch in name]
    total = sum(widths) + 26 * (len(name) - 1)
    x = (W - total) // 2
    y_name = 78
    # soft shadow, then cream letters, one by one for even letterspacing
    for ch, wch in zip(name, widths):
        d.text((x + 4, y_name + 5), ch, font=font, fill=SHADOW + (255,))
        d.text((x, y_name), ch, font=font, fill=CREAM + (255,))
        x += wch + 26

    # --- save ----------------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sky.save(OUT_PATH, format="PNG", optimize=True)
    n_bytes = os.path.getsize(OUT_PATH)
    print(f"wrote {OUT_PATH}: {W}x{H}, {n_bytes} bytes "
          f"({'OK' if n_bytes <= 1_048_576 else 'OVER 1 MiB'})")


if __name__ == "__main__":
    main()
