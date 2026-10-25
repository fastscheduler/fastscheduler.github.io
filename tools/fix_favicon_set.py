#!/usr/bin/env python
"""Regenerate the raster favicon set from the footer brand mark.

The browser favicon is ``favicon.svg`` (the vector master next to this repo's
HTML). This script keeps the legacy PNG/ICO fallbacks in sync with
``brand-logo.png``: the green mark gets a white underlay so its calendar grid
stays readable on dark tab bars, while everything outside the circular mark
stays transparent (no white rounded-square plate).

Run from the repository root:

    python tools/fix_favicon_set.py
"""
from collections import deque

from PIL import Image

SRC = "brand-logo.png"

PNGS = {
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "icon-48.png": 48,
    "icon-96.png": 96,
    "icon-128.png": 128,
    "icon-192.png": 192,
    "icon-256.png": 256,
    "icon-512.png": 512,
    "apple-touch-icon.png": 180,
}


def outside_mask(alpha, threshold=127):
    """Pixels transparent AND connected to the image border."""
    width, height = alpha.size
    transparent = [
        [alpha.getpixel((x, y)) <= threshold for x in range(width)]
        for y in range(height)
    ]
    outside = [[False] * width for _ in range(height)]
    queue = deque()

    def seed(y, x):
        if transparent[y][x] and not outside[y][x]:
            outside[y][x] = True
            queue.append((y, x))

    for x in range(width):
        seed(0, x)
        seed(height - 1, x)
    for y in range(height):
        seed(y, 0)
        seed(y, width - 1)

    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < height and 0 <= nx < width:
                seed(ny, nx)
    return outside


def main():
    source = Image.open(SRC).convert("RGBA")
    alpha = source.getchannel("A")
    width, height = source.size
    outside = outside_mask(alpha)

    # White plate clipped to the circular mark: transparent holes become white,
    # the corners outside the mark stay transparent.
    plate = Image.new("RGBA", source.size, (255, 255, 255, 0))
    plate_px = plate.load()
    for y in range(height):
        row = outside[y]
        for x in range(width):
            if not row[x]:
                plate_px[x, y] = (255, 255, 255, 255)
    base = Image.alpha_composite(plate, source)

    for name, size in PNGS.items():
        base.resize((size, size), Image.LANCZOS).save(name, "PNG", optimize=True)
        print("[png ]", name, size)

    base.resize((256, 256), Image.LANCZOS).save(
        "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print("[ico ] favicon.ico 16/32/48")


if __name__ == "__main__":
    main()
