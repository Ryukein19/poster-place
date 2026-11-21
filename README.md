# BORALIA — The Poster for a Place That Isn't There

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Ryukein19/poster-place/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Ryukein19/poster-place/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for **BORALIA** — "WHERE THE LIGHTS TOUCH THE EARTH".
A snowy mountain valley at night where the aurora descends from the
sky and flows like a river of light down through the valley, pooling
around a small village of warm-lit stone cottages. One cloaked figure
stands in the snow in the foreground, looking up at the lights. The
aurora is the single dominant landmark — huge ribbons of green, teal
and violet filling the sky and touching the ground. Classic vintage
travel-poster style: bold, simple, one dominant image.

`main.py` ships the poster image (`asset.jpg`, generated in the build
session) and writes it to `/output/entry.png` (1024×1024, JPEG) using
only the Python standard library (no PIL, no network). It verifies the
asset's dimensions and size against the competition caps before writing.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
