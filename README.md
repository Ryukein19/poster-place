# ALDERA — The Poster for a Place That Isn't There

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Ryukein19/poster-place/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Ryukein19/poster-place/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for **ALDERA** — "WHERE LIFE MOVES SLOWLY". A
realistic mountain village at golden hour, alive with people doing
daily activities: a farmer with a hay cart, a woman carrying a basket
of bread, children playing with a dog, an old man smoking a pipe, a
market stall with vegetables, laundry on a line. The village name is
carved into the stone of the old clock tower — the name and the
landmark are one. Stone cottages with warm lit windows, a clear
stream, snow-capped mountains behind.

`main.py` ships the poster image (`asset.jpg`, generated in the build
session) and writes it to `/output/entry.png` (1024×1024, JPEG) using
only the Python standard library (no PIL, no network). It verifies the
asset's dimensions and size against the competition caps before writing.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
