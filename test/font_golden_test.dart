import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:font_weight_sample/sample_card.dart';

/// Renders [SampleCard] through the normal flutter_test pipeline (fonts
/// loaded by bc_golden_plugin's `loadConfiguration()` in
/// flutter_test_config.dart), then captures it at pixelRatio 3 so the output
/// is a true 1080x900 px image, matching the 3x Figma export and the 3x
/// iOS Simulator screenshot pixel-for-pixel in scale.
///
/// bc_golden_plugin's own capture paths (`bcWidgetMatchesImage`,
/// `captureGoldenScreenshot`) call `RenderRepaintBoundary.toImage()`/
/// `toImageSync()` with no `pixelRatio`, so they always rasterize at 1x
/// regardless of `devicePixelRatio`. Capturing manually with
/// `pixelRatio: 3` is the correct way to get a true high-resolution render.
void main() {
  testWidgets('sample_card_3x', (tester) async {
    final key = GlobalKey();

    await tester.pumpWidget(
      MaterialApp(
        home: Material(
          child: Center(
            child: RepaintBoundary(
              key: key,
              child: const SampleCard(),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final boundary =
        key.currentContext!.findRenderObject() as RenderRepaintBoundary;

    // toImage()/toByteData() use real async callbacks (GPU readback) that
    // the test's fake clock never drives, so this must run in a real zone.
    await tester.runAsync(() async {
      final image = await boundary.toImage(pixelRatio: 3);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);

      final file = File('test/goldens/sample_card_3x.png');
      await file.create(recursive: true);
      await file.writeAsBytes(byteData!.buffer.asUint8List());

      expect(image.width, SampleCard.width.toInt() * 3);
      expect(image.height, SampleCard.height.toInt() * 3);
    });
  });
}
