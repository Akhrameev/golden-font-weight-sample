# golden-font-weight-sample

Reproducible Flutter sample that compares text rendering across:

1. Figma export (PNG, 3x)
2. `flutter_test` golden render (PNG, 3x)
3. iOS Simulator screenshot crop (PNG, 3x)

It includes scripts to measure per-line text rendering/thickness and build visual comparison images.

## Why this repo exists

Pixel-diff percentages alone can miss typography drift.  
This sample shows that the golden can render text heavier than both Figma and Simulator, with the gap increasing for thinner weights.

## What is in the repo

- [lib/sample_card.dart](./lib/sample_card.dart): the 360x300 test card (light + dark panels)
- [test/font_golden_test.dart](./test/font_golden_test.dart): generates a true 3x (1080x900) golden image
- [tools/measure_vs_figma.py](./tools/measure_vs_figma.py): computes per-line rendering/stem metrics + pixel-diff
- [tools/side_by_side.py](./tools/side_by_side.py): creates a labeled full-card comparison image
- [tools/zoom_squares.py](./tools/zoom_squares.py): creates zoomed word crops per weight
- [figma_frame.svg](./figma_frame.svg): source SVG to paste into Figma
- [out/](./out): generated renders, metrics, and comparison images

## Fonts

The sample uses static Work Sans files from [assets/fonts/](./assets/fonts) and maps these weights:

- Thin: 100
- Regular: 400
- SemiBold: 600
- Bold: 700

## Prerequisites

- Flutter SDK (project contains local FVM at [`.fvm/`](./.fvm))
- Python 3
- Python packages: Pillow, NumPy
- iOS Simulator (for device capture)
- Figma file/frame export at 3x

## Reproduce

### 1) Generate golden render (3x)

```bash
./.fvm/flutter_sdk/bin/flutter test test/font_golden_test.dart
cp test/goldens/sample_card_3x.png out/golden_card_3x.png
```

### 2) Export Figma frame (3x)

Export the frame as PNG 3x and save it as:

`out/figma_card_3x.png`

Expected size: `1080x900`.

### 3) Capture Simulator render (3x crop)

Run the app on iPhone 16 Pro simulator and capture a screenshot:

```bash
./.fvm/flutter_sdk/bin/flutter run
xcrun simctl io booted screenshot /tmp/sim_full.png
```

Then crop to the 1080x900 card and save:

`out/sim_card_3x.png`

### 4) Run measurements + build visuals

```bash
python3 tools/measure_vs_figma.py
python3 tools/side_by_side.py out/side_by_side.png \
  "Figma=out/figma_card_3x.png" \
  "flutter_test golden=out/golden_card_3x.png" \
  "iOS Simulator=out/sim_card_3x.png"
python3 tools/zoom_squares.py out/zoom_squares.png
```

## Current outputs

- Metrics JSON: [out/stems_vs_figma.json](./out/stems_vs_figma.json)
- Full comparison image: [out/side_by_side.png](./out/side_by_side.png)
- Zoomed comparison image: [out/zoom_squares.png](./out/zoom_squares.png)

From the current run:

- Golden vs Figma: heavier on all lines, from about **+6%** (bold) up to **+136%** (thin, dark panel)
- Simulator vs Figma: generally lighter, around **-2% to -28%**
- Pixel-diff vs Figma is nearly identical: **7.80%** (golden) vs **7.83%** (simulator)

## Notes

- All three inputs must be exactly `1080x900`.
- Measurements are deterministic for a fixed set of input images.
- Cross-machine/runtime changes (Flutter engine, iOS runtime, font rasterization) can shift numeric results.
- Raw Figma API responses intentionally excluded from version control.
