#!/usr/bin/env python3
"""Builds a side-by-side comparison of full cards, each labeled.

Usage:
  python tools/side_by_side.py out/side_by_side.png \
    "Figma=out/figma_card_3x.png" \
    "flutter_test golden=out/golden_card_3x.png" \
    "iOS Simulator=out/sim_card_3x.png"
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HF = "/System/Library/Fonts/Helvetica.ttc"
SCALE = 1 / 3  # 1080x900 -> 360x300 per tile, for a readable composite
LABEL_H = 36
PAD = 24


def main() -> None:
    out_path = Path(sys.argv[1])
    entries = []
    for arg in sys.argv[2:]:
        label, path = arg.split("=", 1)
        entries.append((label, Image.open(path).convert("RGB")))

    tile_w = int(entries[0][1].width * SCALE)
    tile_h = int(entries[0][1].height * SCALE)

    canvas_w = len(entries) * tile_w + (len(entries) + 1) * PAD
    canvas_h = tile_h + LABEL_H + 2 * PAD
    canvas = Image.new("RGB", (canvas_w, canvas_h), "#F2F2F2")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(HF, 20)

    x = PAD
    for label, im in entries:
        tile = im.resize((tile_w, tile_h), Image.LANCZOS)
        canvas.paste(tile, (x, PAD))
        draw.rectangle(
            [x, PAD, x + tile_w, PAD + tile_h], outline="#999999", width=1
        )
        draw.text(
            (x + tile_w / 2, PAD + tile_h + LABEL_H / 2),
            label,
            font=font,
            fill="#111111",
            anchor="mm",
        )
        x += tile_w + PAD

    canvas.save(out_path)
    print(f"Wrote {out_path} ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
