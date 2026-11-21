#!/usr/bin/env python3
"""VERDARA -- The Poster for a Place That Isn't There.

Writes the poster image to /output/entry.png.

The poster itself is a single image asset (asset.jpg) generated in the
build session: a painterly travel poster of VERDARA, a peaceful
mountain village in a green valley at golden hour -- stone cottages
with warm lit windows, a church with a tall steeple, a winding path
through flower meadows, a stream, grazing sheep, snow-capped
mountains, and a person walking the path with a basket. This program
ships that image and writes it out, using only the Python standard
library (no PIL, no network).
"""

import os
import sys

ASSET = "asset.jpg"
WIDTH = 1024
HEIGHT = 1024
MAX_BYTES = 1_048_576


def asset_path():
    """Locate the poster asset next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, ASSET)


def jpeg_size(data):
    """Return (width, height) from a JPEG's SOF marker, or (None, None).

    Walks the JPEG marker segments until it finds a start-of-frame
    marker (SOF0/SOF1/SOF2), which carries height then width as two
    big-endian 16-bit values. Pure stdlib; no image library needed.
    """
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        return None, None
    i = 2
    n = len(data)
    while i + 1 < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker == 0xD8:  # SOI: no length field
            i += 2
            continue
        if marker == 0xD9 or marker == 0x01 or 0xD0 <= marker <= 0xD7:
            i += 2  # EOI, TEM, RSTn: no length field
            continue
        if i + 4 > n:
            break
        seg_len = (data[i + 2] << 8) | data[i + 3]
        if seg_len < 2:
            break
        if marker in (0xC0, 0xC1, 0xC2):  # SOF0, SOF1, SOF2
            if i + 9 > n:
                return None, None
            height = (data[i + 5] << 8) | data[i + 6]
            width = (data[i + 7] << 8) | data[i + 8]
            return width, height
        i += 2 + seg_len
    return None, None


def main():
    src = asset_path()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = os.path.join(out_dir, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    width, height = jpeg_size(data)
    if width is None:
        print("error: asset is not a readable JPEG", file=sys.stderr)
        return 1
    if width > WIDTH or height > HEIGHT:
        print(f"error: asset is {width}x{height}, over the 1024x1024 cap",
              file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"error: asset is {len(data)} bytes, over the 1,048,576 cap",
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"wrote {out_path}: {width}x{height}, {len(data)} bytes (OK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
