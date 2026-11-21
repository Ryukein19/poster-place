# VERDARA — The Poster for a Place That Isn't There

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Ryukein19/poster-place/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Ryukein19/poster-place/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for **VERDARA** — a peaceful mountain village in a
green valley at golden hour. Stone cottages with warm lit windows and
smoke curling from chimneys, a little church with a tall steeple, a
winding dirt path through vast flower meadows, a clear stream, grazing
sheep, snow-capped mountains behind, and a person walking the path
with a basket — a place that makes you want to come back.

`main.py` ships the poster image (`asset.jpg`, generated in the build
session) and writes it to `/output/entry.png` (1024×1024, JPEG) using
only the Python standard library (no PIL, no network). It verifies the
asset's dimensions and size against the competition caps before writing.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
