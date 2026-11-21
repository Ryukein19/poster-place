# VELMORA — a travel poster for a place that does not exist.
# MakeFun bounty: the-poster-for-a-place-that-i-2-20261121-0539
#
# The place: VELMORA, a desert valley where one giant crystal spire rises
# out of the dunes at dusk. Violet sky melting into amber at the horizon,
# a low sun, a teal crystal glowing against the dark, and a tiny caravan
# crossing the dunes for scale. Palette is 4 colours: violet, amber,
# teal, dark plum.
#
# STANDARD LIBRARY ONLY. The grading image is python:3.13-slim: no Pillow,
# no fonts, no network. Everything is drawn on a raw RGB bytearray with
# pure-Python helpers and encoded to PNG with zlib + struct. The place
# name is drawn with a geometric bitmap font defined in this file.
# Writes /output/entry.png (1024x1024, PNG, under 1 MiB).
#
# Usage (local check):
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import math
import os
import random
import struct
import zlib

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
DUNE_MID = (58, 32, 56)         # middle dune
DUNE_NEAR = (42, 24, 48)        # near dune, darkest
CREAM = (255, 246, 224)         # place-name type
SHADOW = (24, 12, 40)
STAR = (255, 244, 220)
BIRD = (30, 16, 44)
EDGE_HI = (235, 255, 248)

# --- raw RGB pixel buffer --------------------------------------------------
buf = bytearray(W * H * 3)


def _idx(x, y):
    return (y * W + x) * 3


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = _idx(x, y)
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def blend_px(x, y, color, alpha):
    """Blend color over the pixel with alpha 0..255."""
    if 0 <= x < W and 0 <= y < H and alpha > 0:
        i = _idx(x, y)
        if alpha >= 255:
            buf[i] = color[0]
            buf[i + 1] = color[1]
            buf[i + 2] = color[2]
        else:
            inv = 255 - alpha
            buf[i] = (color[0] * alpha + buf[i] * inv) // 255
            buf[i + 1] = (color[1] * alpha + buf[i + 1] * inv) // 255
            buf[i + 2] = (color[2] * alpha + buf[i + 2] * inv) // 255


def hspan(y, x0, x1, color):
    """Fill a horizontal span [x0, x1) on row y (clipped)."""
    if y < 0 or y >= H:
        return
    x0 = max(x0, 0)
    x1 = min(x1, W)
    if x1 <= x0:
        return
    i0 = _idx(x0, y)
    n = x1 - x0
    buf[i0:i0 + n * 3] = bytes(color) * n


def fill_rect(x0, y0, w, h, color):
    for y in range(max(0, y0), min(H, y0 + h)):
        hspan(y, x0, x0 + w, color)


def fill_polygon(pts, color):
    """Scanline fill of a polygon (list of (x, y), floats ok)."""
    if len(pts) < 3:
        return
    ys = [p[1] for p in pts]
    y_min = max(0, int(math.floor(min(ys))))
    y_max = min(H - 1, int(math.ceil(max(ys))))
    n = len(pts)
    for y in range(y_min, y_max + 1):
        yc = y + 0.5
        xs = []
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                t = (yc - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            hspan(y, int(math.ceil(xs[k])), int(math.floor(xs[k + 1])) + 1, color)


def fill_ellipse(cx, cy, rx, ry, color, alpha=255):
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / ry
        t = 1.0 - dy * dy
        if t <= 0:
            continue
        dx = int(rx * math.sqrt(t))
        if alpha >= 255:
            hspan(y, cx - dx, cx + dx + 1, color)
        else:
            for x in range(max(0, cx - dx), min(W, cx + dx + 1)):
                blend_px(x, y, color, alpha)


def draw_line(x0, y0, x1, y1, color, width=1, alpha=255):
    """Thick line: stamp small discs along the segment."""
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    r = max(1, width // 2)
    for s in range(steps + 1):
        x = int(round(x0 + dx * s / steps))
        y = int(round(y0 + dy * s / steps))
        fill_ellipse(x, y, r, r, color, alpha)


def draw_glow(cx, cy, rx, ry, color, strength=0.9):
    """Soft elliptical glow: radial falloff, alpha-blended."""
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        ny = (y - cy) / ry
        ny2 = ny * ny
        for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
            nx = (x - cx) / rx
            d2 = nx * nx + ny2
            if d2 < 1.0:
                f = 1.0 - d2
                a = int(strength * 255 * f * f)
                if a > 0:
                    blend_px(x, y, color, a)


def sky_gradient(stops):
    """Fill the buffer with a vertical gradient; stops = [(y_frac, rgb)]."""
    n = len(stops)
    for y in range(H):
        f = y / (H - 1)
        for i in range(n - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                t = 0.0 if f1 == f0 else (f - f0) / (f1 - f0)
                c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
                break
        else:
            c = stops[-1][1]
        i0 = y * W * 3
        buf[i0:i0 + W * 3] = bytes(c) * W


def write_png(path, width, height):
    """Encode the RGB buffer as PNG (filter 0 per scanline), stdlib only."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# --- geometric bitmap font for the place name ------------------------------
# 7 wide x 9 tall per letter, '#' = filled. Bold blocky letterforms,
# drawn at 16px cells -> 144px cap height. Must read clearly as VELMORA
# at full size and at a 300px downscale.
FONT = {
    'V': ["#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          ".#...#.",
          ".#...#.",
          "..#.#..",
          "...#..."],
    'E': ["#######",
          "#......",
          "#......",
          "#####..",
          "#......",
          "#......",
          "#......",
          "#......",
          "#######"],
    'L': ["#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#######"],
    'M': ["#.....#",
          "##...##",
          "#.#.#.#",
          "#.#.#.#",
          "#..#..#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#"],
    'O': [".#####.",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          ".#####."],
    'R': ["#####..",
          "#....#.",
          "#....#.",
          "#####..",
          "#.#....",
          "#..#...",
          "#...#..",
          "#....#.",
          "#.....#"],
    'A': ["...#...",
          "..#.#..",
          ".#...#.",
          "#.....#",
          "#.....#",
          "#######",
          "#.....#",
          "#.....#",
          "#.....#"],
}
CELL = 16          # px per grid cell
GAP = 20           # px between letters


def draw_name(name, y0, color):
    """Draw the place name centred, letterspaced, with a soft shadow."""
    widths = [len(FONT[ch][0]) * CELL for ch in name]
    total = sum(widths) + GAP * (len(name) - 1)
    x = (W - total) // 2
    for ox, oy in ((4, 5), (0, 0)):  # shadow pass, then cream pass
        cx = x + ox
        cy = y0 + oy
        col = SHADOW if (ox, oy) != (0, 0) else color
        for ch, wch in zip(name, widths):
            grid = FONT[ch]
            for r, row in enumerate(grid):
                for c, cell in enumerate(row):
                    if cell == '#':
                        fill_rect(cx + c * CELL, cy + r * CELL, CELL, CELL, col)
            cx += wch + GAP


# --- dunes and caravan -----------------------------------------------------
def dune_y(x, y_base=640, amp=26, phase=0.4):
    return y_base + amp * math.sin((x / W) * math.pi * 1.6 + phase)


def dune(y_base, amp, phase, color):
    """A dune ridge: filled polygon whose top edge is a sine curve."""
    pts = [(0, H)]
    for x in range(0, W + 1, 8):
        pts.append((x, y_base + amp * math.sin((x / W) * math.pi * 1.6 + phase)))
    pts.append((W, H))
    fill_polygon(pts, color)


def draw_camel(cx, gy):
    """Tiny camel silhouette with rider, standing on the ridge at gy."""
    fill_ellipse(cx, gy - 7, 18, 9, SHADOW)        # body
    fill_ellipse(cx, gy - 18, 9, 8, SHADOW)        # hump
    fill_polygon([(cx + 10, gy - 12), (cx + 24, gy - 34),
                  (cx + 30, gy - 32), (cx + 18, gy - 8)], SHADOW)  # neck
    fill_ellipse(cx + 28, gy - 33, 6, 5, SHADOW)   # head
    for lx in (cx - 11, cx - 3, cx + 5, cx + 13):  # four legs
        draw_line(lx, gy, lx, gy + 13, SHADOW, width=3)
    fill_ellipse(cx, gy - 29, 5, 5, SHADOW)        # rider

def main():
    random.seed(20261121)

    # --- sky: violet dusk melting into amber at the horizon ---------------
    sky_gradient([
        (0.00, VIOLET_TOP),
        (0.38, VIOLET_MID),
        (0.58, (176, 92, 96)),
        (0.66, AMBER),
        (1.00, AMBER),
    ])

    # --- faint stars in the upper sky --------------------------------------
    for _ in range(90):
        x = random.randint(0, W - 1)
        y = random.randint(0, 300)
        r = random.choice([1, 1, 2])
        a = random.randint(60, 170)
        fill_ellipse(x, y, r, r, STAR, alpha=a)

    # --- sun glow + sun, low on the left, just above the horizon ----------
    sun_x, sun_y, sun_r = 300, 565, 52
    draw_glow(sun_x, sun_y, 190, 130, SUN_HALO)
    fill_ellipse(sun_x, sun_y, sun_r, sun_r, SUN_CORE)

    # --- the crystal spire: one dominant landmark, centre-right -----------
    # glow behind the crystal so it reads as the light source of the valley
    draw_glow(640, 440, 150, 260, TEAL_GLOW)
    apex = (640, 250)
    base_y = 690
    half_w = 105
    # facet triangles (left = sunlit, right = shadow)
    left_facet = [apex, (apex[0] - half_w, base_y), (apex[0] - 18, base_y)]
    mid_facet = [apex, (apex[0] - 18, base_y), (apex[0] + 30, base_y)]
    right_facet = [apex, (apex[0] + 30, base_y), (apex[0] + half_w, base_y)]
    fill_polygon(left_facet, TEAL_HI)
    fill_polygon(mid_facet, TEAL_MID)
    fill_polygon(right_facet, TEAL_DARK)
    # a small notch cut near the top for a faceted silhouette
    fill_polygon([(640, 250), (612, 310), (640, 337), (668, 310)], TEAL_DARK)
    # bright core line down the sunlit edge
    draw_line(apex[0], apex[1], apex[0] - half_w, base_y, TEAL_HI, width=4)
    draw_line(apex[0], apex[1], apex[0] - half_w, base_y, EDGE_HI, width=5)
    # small shard crystals at the base
    for sx, sw, sh in [(505, 34, 120), (742, 28, 95), (700, 20, 70)]:
        fill_polygon([(sx, base_y - sh), (sx - sw, base_y), (sx + sw, base_y)],
                     TEAL_MID)
        fill_polygon([(sx, base_y - sh), (sx - sw, base_y), (sx, base_y)],
                     TEAL_HI)

    # --- dunes: three ridges, far to near, crystal base tucked behind ------
    dune(640, 26, 0.4, DUNE_FAR)
    # tiny caravan walking ON the far ridge, for scale
    for cx in (330, 395, 460):
        draw_camel(cx, int(dune_y(cx)))
    dune(700, 22, 1.2, DUNE_MID)
    dune(760, 34, 2.2, DUNE_NEAR)
    # re-draw the crystal base over the far dune so the spire sits IN the valley
    fill_polygon([(505, 690), (505 - 34, 690), (505, 570)], TEAL_MID)

    # --- birds --------------------------------------------------------------
    for bx, by, s in [(180, 210, 14), (240, 180, 11), (830, 250, 13), (880, 205, 10)]:
        draw_line(bx - s, by, bx, by - 6, BIRD, width=3, alpha=220)
        draw_line(bx, by - 6, bx + s, by, BIRD, width=3, alpha=220)

    # --- the place name: VELMORA, large, letterspaced, top centre ---------
    draw_name("VELMORA", 78, CREAM)

    # --- save ----------------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    n_bytes = write_png(OUT_PATH, W, H)
    print(f"wrote {OUT_PATH}: {W}x{H}, {n_bytes} bytes "
          f"({'OK' if n_bytes <= 1_048_576 else 'OVER 1 MiB'})")


if __name__ == "__main__":
    main()
