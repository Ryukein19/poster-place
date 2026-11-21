# AQUARIS — a travel poster for a place that does not exist.
# MakeFun bounty: the-poster-for-a-place-that-i-2-20261121-0539
#
# The place: AQUARIS, a city beneath the waves. One great glass dome city
# glowing warm gold in the deep blue, smaller domes linked by glowing tube
# walkways, god rays falling from the surface, and the sea alive around
# it: fish schools, rising bubble streams, jellyfish, coral, seaweed, a
# submarine and a diver. The name sits large at the top in cream, with
# the tagline "THE CITY BENEATH THE WAVES" beneath it. Palette is deep
# indigo water, glowing teal, warm gold windows, cream type.
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
WATER_TOP = (6, 14, 40)        # deep indigo, surface water
WATER_MID = (12, 44, 90)       # mid blue
WATER_GLOW = (24, 100, 140)    # glow band around the city
WATER_DEEP = (10, 26, 58)      # deep water near the seabed
RAY = (180, 230, 240)          # god-ray pale cyan
DOME_RIM = (175, 232, 242)     # glass rim highlight
DOME_IN = (34, 104, 138)       # dome interior, lit blue-teal
DOME_HI = (205, 242, 250)      # specular highlight on the glass
DOME_SH = (10, 28, 58)         # dome shadow, bottom-right
DOME_FAR = (26, 72, 108)       # far dome interior, hazier blue
DOME_FAR_RIM = (140, 195, 215)
BUILD = (14, 36, 64)           # building silhouettes inside the dome
WINDOW = (255, 200, 110)       # warm gold windows
GOLD = (255, 214, 130)
CREAM = (255, 246, 224)        # place-name type
SHADOW = (6, 12, 34)
SEABED = (16, 24, 54)          # seabed ridge
ROCK = (24, 34, 68)
CORAL_PINK = (255, 120, 150)
CORAL_ORANGE = (255, 150, 90)
WEED = (36, 150, 110)
WEED_DARK = (22, 100, 78)
FISH = (140, 200, 230)         # fish, pale blue
FISH_DARK = (16, 42, 74)       # fish, dark silhouette
FISH_BELLY = (210, 235, 245)
BUBBLE = (190, 230, 245)
JELLY_PINK = (255, 170, 212)
JELLY_CYAN = (150, 230, 255)
SUB = (52, 84, 124)            # submarine hull
SUB_TOP = (96, 136, 176)
DIVER = (18, 28, 48)

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


def _poly_spans(pts, y_min, y_max):
    """Yield (y, x_left, x_right) scanline spans of a polygon."""
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
            yield y, int(math.ceil(xs[k])), int(math.floor(xs[k + 1])) + 1


def fill_polygon(pts, color):
    """Scanline fill of a polygon (list of (x, y), floats ok)."""
    if len(pts) < 3:
        return
    ys = [p[1] for p in pts]
    y_min = max(0, int(math.floor(min(ys))))
    y_max = min(H - 1, int(math.ceil(max(ys))))
    for y, x0, x1 in _poly_spans(pts, y_min, y_max):
        hspan(y, x0, x1, color)


def fill_polygon_alpha(pts, color, alpha):
    """Scanline fill with a translucent colour (alpha 0..255)."""
    if len(pts) < 3 or alpha <= 0:
        return
    ys = [p[1] for p in pts]
    y_min = max(0, int(math.floor(min(ys))))
    y_max = min(H - 1, int(math.ceil(max(ys))))
    for y, x0, x1 in _poly_spans(pts, y_min, y_max):
        x0 = max(0, x0)
        x1 = min(W, x1)
        for x in range(x0, x1):
            blend_px(x, y, color, alpha)


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


def v_gradient(stops):
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

# --- geometric bitmap font -------------------------------------------------
# 7 wide x 9 tall per letter, '#' = filled. Bold blocky letterforms.
# The place name uses 16px cells (144px cap height); the tagline uses
# 5px cells (45px cap height). Must read clearly at full size and at
# a 300px downscale.
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
    'Q': [".#####.",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#...#.#",
          "#....##",
          ".#####."],
    'U': ["#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          ".#####."],
    'I': ["#######",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "#######"],
    'S': [".#####.",
          "#.....#",
          "#......",
          "#......",
          ".#####.",
          "......#",
          "......#",
          "#.....#",
          ".#####."],
    'T': ["#######",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#..."],
    'H': ["#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#######",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#"],
    'C': [".#####.",
          "#.....#",
          "#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#.....#",
          ".#####."],
    'Y': ["#.....#",
          "#.....#",
          ".#...#.",
          ".#...#.",
          "..#.#..",
          "...#...",
          "...#...",
          "...#...",
          "...#..."],
    'B': ["#####..",
          "#....#.",
          "#....#.",
          "#....#.",
          "#####..",
          "#....#.",
          "#....#.",
          "#....#.",
          "#####.."],
    'N': ["#.....#",
          "##....#",
          "#.#...#",
          "#..#..#",
          "#...#.#",
          "#....##",
          "#.....#",
          "#.....#",
          "#.....#"],
    'W': ["#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#..#..#",
          "#..#..#",
          "#.#.#.#",
          "#.#.#.#",
          "##...##"],
}


def text_width(text, cell, gap):
    """Pixel width of text at the given cell size and letter gap."""
    w = 0
    for ch in text:
        w += 3 * cell if ch == ' ' else 7 * cell
        w += gap
    return w - gap if text else 0


def draw_text(text, y0, color, cell=16, gap=20, shad=(4, 5)):
    """Draw text centred, letterspaced, with a soft shadow pass."""
    total = text_width(text, cell, gap)
    x = (W - total) // 2
    for ox, oy in ((shad[0], shad[1]), (0, 0)):
        cx = x + ox
        cy = y0 + oy
        col = SHADOW if (ox, oy) != (0, 0) else color
        for ch in text:
            if ch == ' ':
                cx += 3 * cell + gap
                continue
            grid = FONT[ch]
            for r, row in enumerate(grid):
                for c, cellv in enumerate(row):
                    if cellv == '#':
                        fill_rect(cx + c * cell, cy + r * cell, cell, cell, col)
            cx += 7 * cell + gap

# --- the underwater city ---------------------------------------------------
def draw_dome_shell(cx, cy, r, interior, rim, hi, sh):
    """A glass dome: bright rim ring, lit interior, specular highlight
    top-left, shadow bottom-right, bright arc along the upper-left rim."""
    fill_ellipse(cx, cy, r, r, rim)
    fill_ellipse(cx, cy, r - 6, r - 6, interior)
    draw_glow(cx - r // 3, cy - r // 3, r // 2 + 20, r // 2 + 20, hi, 0.5)
    draw_glow(cx + r // 3, cy + r // 3, r // 2 + 10, r // 2 + 10, sh, 0.45)
    for a in range(185, 272, 6):  # bright arc, upper-left rim
        rad = math.radians(a)
        ax = cx + int((r - 3) * math.cos(rad))
        ay = cy + int((r - 3) * math.sin(rad))
        fill_ellipse(ax, ay, 4, 4, (235, 250, 255), alpha=200)


def draw_building(bx, base_y, w, h):
    """Dark tower inside the dome with a grid of warm gold windows."""
    fill_rect(bx, base_y - h, w, h, BUILD)
    for wy in range(base_y - h + 8, base_y - 6, 12):
        for wx in range(bx + 6, bx + w - 4, 11):
            if random.random() < 0.75:
                fill_rect(wx, wy, 4, 5, WINDOW)


def dome_windows(cx, cy, r, n):
    """Scattered warm window lights inside a dome, lower two-thirds."""
    for _ in range(n):
        ang = random.uniform(0, 2 * math.pi)
        rad = random.uniform(0, r * 0.85)
        x = int(cx + rad * math.cos(ang))
        y = int(cy + rad * math.sin(ang))
        if y > cy - r * 0.4:
            fill_rect(x, y, 4, 4, WINDOW)


def draw_walkway(x0, y0, x1, y1):
    """A glowing tube walkway between two domes."""
    draw_line(x0, y0, x1, y1, (50, 170, 175), width=9)
    draw_line(x0, y0, x1, y1, (140, 235, 230), width=3)
    draw_glow((x0 + x1) // 2, (y0 + y1) // 2, 40, 25, (60, 180, 185), 0.4)


def draw_fish(cx, cy, size, direction, body, belly=None):
    """A small fish: elliptical body, tail triangle, belly, eye."""
    fill_ellipse(cx, cy, size, max(2, int(size * 0.45)), body)
    tx = cx - direction * size
    fill_polygon([(tx, cy),
                  (tx - direction * size, cy - size // 2),
                  (tx - direction * size, cy + size // 2)], body)
    if belly:
        fill_ellipse(cx, cy + size // 5, size // 2, max(1, size // 4), belly)
    ex = cx + direction * size * 2 // 3
    fill_ellipse(ex, cy - size // 6, 1, 1, SHADOW)


def draw_fish_school(cx, cy, n, direction, body, belly=None):
    """A loose school: fish scattered around a centre, same direction."""
    for _ in range(n):
        fx = cx + random.randint(-70, 70)
        fy = cy + random.randint(-28, 28)
        size = random.randint(8, 18)
        draw_fish(fx, fy, size, direction, body, belly)


def draw_bubble(x, y, r, alpha=140):
    fill_ellipse(x, y, r, r, BUBBLE, alpha=alpha)
    fill_ellipse(x - r // 3, y - r // 3, max(1, r // 3), max(1, r // 3),
                 (255, 255, 255), alpha=200)


def bubble_stream(x0, y_top, y_base):
    """A column of bubbles rising from y_base up to y_top, wobbling."""
    y = y_base
    step = 0
    while y > y_top:
        wob = int(6 * math.sin(step * 0.9))
        r = 2 + (step % 4)
        draw_bubble(x0 + wob, y, r)
        y -= 26 + (step % 3) * 5
        step += 1


def draw_jellyfish(cx, cy, r, color):
    """Glowing bell + wavy tentacles, drifting."""
    fill_ellipse(cx, cy, r, int(r * 0.7), color, alpha=200)
    fill_ellipse(cx, cy - r // 5, int(r * 0.6), int(r * 0.4),
                 (255, 255, 255), alpha=90)
    for i, dx in enumerate([-r * 3 // 4, -r // 3, 0, r // 3, r * 3 // 4]):
        length = r + 20 + (i * 7) % 25
        x0 = cx + dx
        y0 = cy + int(r * 0.5)
        x1, y1 = x0 + 4, y0 + length // 3
        x2, y2 = x0 - 3, y0 + 2 * length // 3
        x3, y3 = x0 + 2, y0 + length
        draw_line(x0, y0, x1, y1, color, width=2, alpha=160)
        draw_line(x1, y1, x2, y2, color, width=2, alpha=160)
        draw_line(x2, y2, x3, y3, color, width=2, alpha=160)


def draw_coral(cx, cy, scale, color):
    """A fan of branching arms from one base point on the seabed."""
    for ang in [-70, -45, -20, 0, 20, 45, 70]:
        rad = math.radians(ang)
        length = scale * random.uniform(0.6, 1.0)
        x1 = cx + int(length * math.sin(rad))
        y1 = cy - int(length * math.cos(rad))
        draw_line(cx, cy, x1, y1, color, width=max(2, scale // 4))
        mx, my = (cx + x1) // 2, (cy + y1) // 2
        bx = mx + int(scale * 0.3 * math.sin(rad + 0.6))
        by = my - int(scale * 0.3 * math.cos(rad + 0.6))
        draw_line(mx, my, bx, by, color, width=2)


def draw_seaweed(x, base_y, height, color):
    """One wavy blade: a ribbon polygon along a sine centreline."""
    pts_left = []
    pts_right = []
    wdt = 5
    for s in range(0, height + 1, 6):
        y = base_y - s
        off = int(8 * math.sin(s / height * math.pi * 1.5))
        pts_left.append((x + off - wdt, y))
        pts_right.append((x + off + wdt, y))
    fill_polygon(pts_left + pts_right[::-1], color)


def draw_sub(cx, cy, scale, direction=1):
    """A small submarine: hull, tower, periscope, gold portholes,
    tail fin, propeller, and a translucent searchlight cone."""
    rx = int(70 * scale)
    ry = int(22 * scale)
    fill_ellipse(cx, cy, rx, ry, SUB)
    fill_ellipse(cx, cy - ry // 3, rx, ry // 2, SUB_TOP)
    fill_rect(cx - int(12 * scale), cy - ry - int(14 * scale),
              int(24 * scale), int(16 * scale), SUB)
    draw_line(cx + int(6 * scale), cy - ry - int(14 * scale),
              cx + int(6 * scale), cy - ry - int(26 * scale), SUB, width=3)
    for px in (-40, -10, 20):
        fill_ellipse(cx + int(px * scale), cy, int(5 * scale),
                     int(5 * scale), WINDOW)
    fill_polygon([(cx - direction * rx, cy),
                  (cx - direction * (rx + 18), cy - 14),
                  (cx - direction * (rx + 18), cy + 14)], SUB)
    draw_line(cx - direction * (rx + 20), cy - 8,
              cx - direction * (rx + 20), cy + 8, SUB_TOP, width=3)
    fx = cx + direction * rx
    fill_polygon_alpha([(fx, cy - 6), (fx, cy + 6),
                        (fx + direction * 130, cy + 40),
                        (fx + direction * 130, cy - 40)],
                       (255, 230, 160), 26)


def draw_diver(cx, cy, scale):
    """A tiny diver: body, head, tank, fins, one arm."""
    fill_ellipse(cx, cy, int(16 * scale), int(7 * scale), DIVER)
    fill_ellipse(cx + int(18 * scale), cy - int(2 * scale),
                 int(6 * scale), int(6 * scale), DIVER)
    fill_rect(cx - int(6 * scale), cy - int(12 * scale),
              int(14 * scale), int(6 * scale), (150, 160, 170))
    fill_polygon([(cx - int(16 * scale), cy),
                  (cx - int(30 * scale), cy - int(8 * scale)),
                  (cx - int(28 * scale), cy + int(4 * scale))], DIVER)
    fill_polygon([(cx - int(16 * scale), cy),
                  (cx - int(30 * scale), cy + int(8 * scale)),
                  (cx - int(28 * scale), cy - int(2 * scale))], DIVER)
    draw_line(cx + int(8 * scale), cy + int(4 * scale),
              cx + int(20 * scale), cy + int(10 * scale), DIVER, width=3)


def seabed(top_y, amp, phase, color):
    """A seabed ridge: filled polygon whose top edge is a sine curve."""
    pts = [(0, H)]
    for x in range(0, W + 1, 8):
        pts.append((x, top_y + amp * math.sin((x / W) * math.pi * 1.8 + phase)))
    pts.append((W, H))
    fill_polygon(pts, color)


def main():
    random.seed(20261121)

    # --- water: dark indigo at the surface, glowing teal around the city,
    #     deep again toward the seabed --------------------------------------
    v_gradient([
        (0.00, WATER_TOP),
        (0.30, WATER_MID),
        (0.55, WATER_GLOW),
        (0.78, WATER_DEEP),
        (1.00, (8, 18, 44)),
    ])

    # --- god rays slanting down from the surface ---------------------------
    for (tx0, tx1, bx0, bx1, yb, a) in [
            (100, 170, 180, 230, 520, 26),
            (330, 400, 400, 450, 480, 22),
            (580, 640, 640, 680, 500, 26),
            (800, 860, 850, 890, 460, 20)]:
        fill_polygon_alpha([(tx0, 0), (tx1, 0), (bx1, yb), (bx0, yb)],
                           RAY, a)

    # --- the city's own glow, lighting the water around it -----------------
    draw_glow(512, 650, 340, 300, (40, 140, 170), 0.4)

    # --- far domes: smaller, hazier, bluer ---------------------------------
    draw_dome_shell(235, 745, 100, DOME_FAR, DOME_FAR_RIM,
                    (190, 230, 240), (12, 30, 60))
    dome_windows(235, 745, 100, 12)
    draw_dome_shell(805, 725, 115, DOME_FAR, DOME_FAR_RIM,
                    (190, 230, 240), (12, 30, 60))
    dome_windows(805, 725, 115, 14)
    draw_dome_shell(120, 800, 55, DOME_FAR, DOME_FAR_RIM,
                    (190, 230, 240), (12, 30, 60))
    dome_windows(120, 800, 55, 5)

    # --- glowing tube walkways linking the domes ---------------------------
    draw_walkway(334, 730, 273, 670)   # left dome -> central dome
    draw_walkway(691, 710, 751, 665)   # right dome -> central dome
    draw_walkway(140, 770, 172, 792)   # tiny dome -> left dome

    # --- the central dome city: one dominant landmark ----------------------
    draw_dome_shell(512, 650, 240, DOME_IN, DOME_RIM, DOME_HI, DOME_SH)
    for (bx, w, h) in [(375, 42, 80), (425, 50, 120), (480, 45, 95),
                        (530, 55, 140), (590, 42, 70)]:
        draw_building(bx, 840, w, h)
    dome_windows(512, 650, 240, 30)

    # --- the sea, alive: fish schools --------------------------------------
    draw_fish_school(300, 340, 12, 1, FISH, FISH_BELLY)
    draw_fish_school(720, 300, 10, -1, FISH_DARK, None)
    draw_fish_school(860, 480, 7, -1, FISH, FISH_BELLY)
    draw_fish(450, 420, 14, 1, FISH_DARK, None)
    draw_fish(200, 600, 12, -1, FISH, FISH_BELLY)
    draw_fish(900, 600, 10, 1, FISH_DARK, None)

    # --- bubble streams -----------------------------------------------------
    bubble_stream(512, 300, 410)   # from the central dome
    bubble_stream(235, 500, 640)   # from the left dome
    bubble_stream(180, 750, 880)   # from the coral
    bubble_stream(706, 430, 530)   # from the diver

    # --- jellyfish drifting near the top ------------------------------------
    draw_jellyfish(140, 330, 26, JELLY_PINK)
    draw_jellyfish(890, 310, 22, JELLY_CYAN)
    draw_jellyfish(700, 360, 16, JELLY_PINK)

    # --- a submarine and a diver, for scale ---------------------------------
    draw_sub(170, 520, 1.0, direction=1)
    draw_diver(700, 540, 1.0)

    # --- the seabed, tucked over the dome bases ----------------------------
    seabed(885, 18, 0.6, SEABED)
    for (rx, ry, rw, rh) in [(60, 905, 46, 18), (830, 920, 60, 22),
                              (960, 900, 40, 16)]:
        fill_ellipse(rx, ry, rw, rh, ROCK)

    # --- coral, seaweed and shells on the seabed ---------------------------
    draw_coral(180, 895, 46, CORAL_PINK)
    draw_coral(700, 900, 40, CORAL_ORANGE)
    draw_coral(920, 885, 34, CORAL_PINK)
    fill_ellipse(300, 905, 26, 14, CORAL_ORANGE)
    fill_ellipse(620, 915, 22, 12, CORAL_PINK)
    for (sx, sy, hh, col) in [(90, 900, 90, WEED), (320, 895, 120, WEED_DARK),
                               (480, 900, 70, WEED), (760, 905, 110, WEED),
                               (960, 895, 80, WEED_DARK)]:
        draw_seaweed(sx, sy, hh, col)
    for (sx, sy) in [(260, 930), (420, 940), (560, 935), (840, 945)]:
        fill_ellipse(sx, sy, 7, 4, (200, 190, 220))

    # --- the place name: AQUARIS, large, letterspaced, top centre ---------
    draw_text("AQUARIS", 64, CREAM, cell=16, gap=20)
    draw_text("THE CITY BENEATH THE WAVES", 232, GOLD, cell=5, gap=6,
              shad=(2, 2))

    # --- save ----------------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    n_bytes = write_png(OUT_PATH, W, H)
    print(f"wrote {OUT_PATH}: {W}x{H}, {n_bytes} bytes "
          f"({'OK' if n_bytes <= 1_048_576 else 'OVER 1 MiB'})")


if __name__ == "__main__":
    main()
