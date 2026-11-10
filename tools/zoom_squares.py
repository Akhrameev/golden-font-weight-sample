#!/usr/bin/env python3
"""Builds a grid of one zoomed-in word per weight (Bold/SemiBold/Regular/Thin),
for Figma / golden / Simulator side by side, enlarged with nearest-neighbor
(no smoothing) so the antialiasing itself is visible.

Reads out/{figma,golden,sim}_card_3x.png, out/baselines.json (word x-ranges,
measured from Flutter's own text layout by
test/measure_baselines_test.dart) and out/stems_vs_figma.json (per-line
ink-vs-figma percentages). Writes out/zoom_squares.png.

Usage: python tools/zoom_squares.py [out/zoom_squares.png]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_vs_figma import (  # noqa: E402
    CARD_W,
    LINE_ORDER,
    coverage_map,
    find_line_bands,
    load_rgb,
)

HF = "/System/Library/Fonts/Helvetica.ttc"
OUT = Path(__file__).resolve().parent.parent / "out"

ZOOM = 6
PAD = 16
LABEL_H = 26
HEADER_H = 40
WORD_X_PAD_PT = 2  # logical px of breathing room around the word, at 1x


def main() -> None:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / "zoom_squares.png"

    figma = load_rgb(OUT / "figma_card_3x.png")
    golden = load_rgb(OUT / "golden_card_3x.png")
    sim = load_rgb(OUT / "sim_card_3x.png")
    images = {"Figma": figma, "golden": golden, "Simulator": sim}

    cov_golden = coverage_map(golden)
    bands = find_line_bands(cov_golden)
    # find_line_bands returns light panel's 4 bands then dark panel's 4, in
    # LINE_ORDER each (see measure_vs_figma.PANEL_ORDER / LINE_ORDER).
    light_bands = dict(zip(LINE_ORDER, bands[: len(LINE_ORDER)]))

    baselines = json.loads((OUT / "baselines.json").read_text())
    word_info = {
        row["line"]: row for row in baselines if row["panel"] == "light"
    }

    stems_path = OUT / "stems_vs_figma.json"
    stats_by_key = {}
    if stems_path.exists():
        data = json.loads(stems_path.read_text())
        for row in data["lines"]:
            stats_by_key[(row["panel"], row["line"])] = row

    tiles = []  # (line_label, {source_name: PIL.Image, ...}, pct_text)
    for line in LINE_ORDER:
        y0, y1 = light_bands[line]
        info = word_info[line]
        # wordLeft/wordRight are logical (1x) px; images are captured at 3x.
        wx0 = max(0, int((info["wordLeft"] - WORD_X_PAD_PT) * 3))
        wx1 = min(CARD_W, int((info["wordRight"] + WORD_X_PAD_PT) * 3))
        crop_box = (wx0, y0, wx1, y1)

        row_tiles = {}
        for name, rgb in images.items():
            im = Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"))
            word = im.crop(crop_box)
            zoomed = word.resize(
                (word.width * ZOOM, word.height * ZOOM), Image.NEAREST
            )
            row_tiles[name] = zoomed

        stat = stats_by_key.get(("light", line))
        if stat:
            pct_text = (
                f"“{info['word']}” — golden "
                f"{stat['golden_vs_figma_pct']:+.0f}% · sim "
                f"{stat['sim_vs_figma_pct']:+.0f}% vs Figma"
            )
        else:
            pct_text = f"“{info['word']}”"

        tiles.append((line, row_tiles, pct_text))

    tile_w = max(t.width for _, rt, _ in tiles for t in rt.values())
    tile_h = max(t.height for _, rt, _ in tiles for t in rt.values())
    col_names = list(images.keys())

    canvas_w = PAD + len(col_names) * (tile_w + PAD)
    canvas_h = HEADER_H + len(tiles) * (tile_h + LABEL_H + PAD) + PAD
    canvas = Image.new("RGB", (canvas_w, canvas_h), "#FFFFFF")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(HF, 18)
    font_small = ImageFont.truetype(HF, 14)

    for ci, name in enumerate(col_names):
        cx = PAD + ci * (tile_w + PAD) + tile_w / 2
        draw.text((cx, HEADER_H / 2), name, font=font, fill="#111111", anchor="mm")

    y = HEADER_H
    for line, row_tiles, pct_text in tiles:
        for ci, name in enumerate(col_names):
            x = PAD + ci * (tile_w + PAD)
            tile = row_tiles[name]
            bg = Image.new("RGB", (tile_w, tile_h), "#DDDDDD")
            bg.paste(tile, ((tile_w - tile.width) // 2, (tile_h - tile.height) // 2))
            canvas.paste(bg, (x, y))
            draw.rectangle([x, y, x + tile_w, y + tile_h], outline="#999999", width=1)
        draw.text(
            (PAD, y + tile_h + LABEL_H / 2),
            f"{line}  —  {pct_text}",
            font=font_small,
            fill="#333333",
            anchor="lm",
        )
        y += tile_h + LABEL_H + PAD

    canvas.save(out_path)
    print(f"Wrote {out_path} ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
