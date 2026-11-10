#!/usr/bin/env python3
"""Measures how heavy each text line renders in the golden and the Simulator
capture, compared with the Figma export. Writes out/stems_vs_figma.json and
prints a summary table.

All three images are expected at out/{figma,golden,sim}_card_3x.png, each
1080x900 (the 360x300 pt card at 3x).

Usage: python tools/measure_vs_figma.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "out"

CARD_W, CARD_H = 1080, 900
PANEL_H = 450  # 150pt * 3

LIGHT_BG = np.array([255, 255, 255], dtype=np.float64)
LIGHT_FG = np.array([0x11, 0x11, 0x11], dtype=np.float64)
DARK_BG = np.array([0x11, 0x11, 0x11], dtype=np.float64)
DARK_FG = np.array([255, 255, 255], dtype=np.float64)

LINE_ORDER = ["bold", "semibold", "regular", "thin"]
PANEL_ORDER = ["light", "dark"]


def load_rgb(path: Path) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    assert im.size == (CARD_W, CARD_H), f"{path} is {im.size}, expected {(CARD_W, CARD_H)}"
    return np.asarray(im, dtype=np.float64)


def coverage_map(rgb: np.ndarray) -> np.ndarray:
    """Per-pixel 'how much like the true text color' in [0, 1], computed
    against each panel's own true fg/bg so a stroke that never reaches full
    contrast still counts as the faint stroke it is."""
    cov = np.zeros((CARD_H, CARD_W), dtype=np.float64)
    for y0, y1, bg, fg in (
        (0, PANEL_H, LIGHT_BG, LIGHT_FG),
        (PANEL_H, CARD_H, DARK_BG, DARK_FG),
    ):
        band = rgb[y0:y1]
        # Project each pixel onto the bg->fg axis using luminance distance.
        bg_l = bg.mean()
        fg_l = fg.mean()
        gray = band.mean(axis=2)
        denom = (fg_l - bg_l) if fg_l != bg_l else 1.0
        c = (gray - bg_l) / denom
        cov[y0:y1] = np.clip(c, 0.0, 1.0)
    return cov


def find_line_bands(cov: np.ndarray, epsilon: float = 0.5) -> list[tuple[int, int]]:
    """Contiguous row ranges with ink above `epsilon`, found from `cov`
    (expected to be the golden's own coverage map)."""
    row_ink = cov.sum(axis=1)
    is_text_row = row_ink > epsilon
    bands = []
    start = None
    for y, flag in enumerate(is_text_row):
        if flag and start is None:
            start = y
        elif not flag and start is not None:
            bands.append((start, y))
            start = None
    if start is not None:
        bands.append((start, len(is_text_row)))
    return bands


def mean_stem_width(cov_band: np.ndarray, threshold: float = 0.5) -> float:
    """Mean run length of contiguous above-threshold pixels per row,
    averaged over all rows in the band. A rough proxy for stroke width."""
    binary = cov_band >= threshold
    run_lengths = []
    for row in binary:
        run = 0
        for v in row:
            if v:
                run += 1
            elif run:
                run_lengths.append(run)
                run = 0
        if run:
            run_lengths.append(run)
    return float(np.mean(run_lengths)) if run_lengths else 0.0


def pixel_diff_pct(a: np.ndarray, b: np.ndarray) -> float:
    diff = np.any(np.abs(a - b) > 0.5, axis=2)
    return 100.0 * diff.sum() / diff.size


def main() -> None:
    figma = load_rgb(OUT / "figma_card_3x.png")
    golden = load_rgb(OUT / "golden_card_3x.png")
    sim = load_rgb(OUT / "sim_card_3x.png")

    cov_figma = coverage_map(figma)
    cov_golden = coverage_map(golden)
    cov_sim = coverage_map(sim)

    bands = find_line_bands(cov_golden)
    if len(bands) != 8:
        raise SystemExit(
            f"expected 8 line bands from the golden's ink, found {len(bands)}: {bands}"
        )

    results = []
    labels = [(p, l) for p in PANEL_ORDER for l in LINE_ORDER]

    print(f"{'panel':<6} {'line':<9} {'ink figma':>10} {'ink golden':>11} {'ink sim':>9} "
          f"{'golden vs fig':>14} {'sim vs fig':>11}")

    for (panel, line), (y0, y1) in zip(labels, bands):
        ink_figma = float(cov_figma[y0:y1].sum())
        ink_golden = float(cov_golden[y0:y1].sum())
        ink_sim = float(cov_sim[y0:y1].sum())

        stem_figma = mean_stem_width(cov_figma[y0:y1])
        stem_golden = mean_stem_width(cov_golden[y0:y1])
        stem_sim = mean_stem_width(cov_sim[y0:y1])

        golden_vs_figma = 100.0 * (ink_golden - ink_figma) / ink_figma if ink_figma else float("nan")
        sim_vs_figma = 100.0 * (ink_sim - ink_figma) / ink_figma if ink_figma else float("nan")

        print(f"{panel:<6} {line:<9} {ink_figma:>10.1f} {ink_golden:>11.1f} {ink_sim:>9.1f} "
              f"{golden_vs_figma:>+13.1f}% {sim_vs_figma:>+10.1f}%")

        results.append({
            "panel": panel,
            "line": line,
            "y_range": [y0, y1],
            "ink_figma": ink_figma,
            "ink_golden": ink_golden,
            "ink_sim": ink_sim,
            "stem_figma": stem_figma,
            "stem_golden": stem_golden,
            "stem_sim": stem_sim,
            "golden_vs_figma_pct": golden_vs_figma,
            "sim_vs_figma_pct": sim_vs_figma,
        })

    diff_golden_figma = pixel_diff_pct(golden, figma)
    diff_sim_figma = pixel_diff_pct(sim, figma)

    print()
    print(f"Pixels differing from Figma (any channel, any amount):")
    print(f"  golden vs figma: {diff_golden_figma:.2f}%")
    print(f"  sim vs figma:    {diff_sim_figma:.2f}%")

    (OUT / "stems_vs_figma.json").write_text(json.dumps({
        "lines": results,
        "pixel_diff_pct": {
            "golden_vs_figma": diff_golden_figma,
            "sim_vs_figma": diff_sim_figma,
        },
    }, indent=2))
    print(f"\nWrote {OUT / 'stems_vs_figma.json'}")


if __name__ == "__main__":
    main()
