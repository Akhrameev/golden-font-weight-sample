import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:font_weight_sample/sample_card.dart';

/// Measures, from the real rendered widget, exactly where each line's text
/// baseline sits (in logical px, i.e. 1x points) inside the 360x300 card,
/// and the logical x-range of one chosen word per line.
///
/// Baselines are used to build `figma_frame.svg` so its <text> elements sit
/// on the same baselines Flutter uses, to within fractions of a point. Word
/// ranges are used by tools/zoom_squares.py to crop a representative word
/// per weight for the zoomed comparison -- computed from Flutter's own text
/// layout instead of a pixel-ink threshold, because the Thin weight has too
/// little ink for column-gap detection to reliably find word boundaries.
/// Run with: `flutter test test/measure_baselines_test.dart`.

/// Which word (0-indexed on whitespace split, negative counts from the end)
/// to report the x-range of, per line. Must match tools/zoom_squares.py.
const Map<String, int> wordIndexForLine = {
  'bold': -1,
  'semibold': 3,
  'regular': 1,
  'thin': 1,
};

void main() {
  testWidgets('measure baselines', (tester) async {
    final cardKey = GlobalKey();
    await tester.pumpWidget(
      MaterialApp(
        home: Material(
          child: Center(child: SampleCard(key: cardKey)),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // The card is centered in the default 800x600 test surface, so every
    // coordinate must be taken relative to the card's own origin, not the
    // screen's.
    final cardOrigin = tester.getTopLeft(find.byKey(cardKey));

    const lineIds = ['bold', 'semibold', 'regular', 'thin'];
    const panelIds = ['light', 'dark'];

    final results = <Map<String, Object>>[];

    for (final panelId in panelIds) {
      for (final lineId in lineIds) {
        final key = ValueKey('$panelId-$lineId');
        final finder = find.byKey(key);
        final topLeft = tester.getTopLeft(finder) - cardOrigin;
        final size = tester.getSize(finder);
        final widget = tester.widget<Text>(finder);

        // A standalone TextPainter mirrors the RenderParagraph's layout
        // without the layout/paint-phase restriction that
        // RenderBox.getDistanceToBaseline enforces.
        final painter = TextPainter(
          text: TextSpan(text: widget.data, style: widget.style),
          textDirection: TextDirection.ltr,
        )..layout(maxWidth: size.width);
        final lineMetrics = painter.computeLineMetrics();
        expect(lineMetrics.length, 1, reason: 'line wrapped unexpectedly');
        final baseline = lineMetrics.first.baseline;

        final text = widget.data!;
        final words = text.split(' ');
        final wordIndex = wordIndexForLine[lineId]!;
        final resolvedIndex = wordIndex < 0 ? words.length + wordIndex : wordIndex;
        int wordStart = 0;
        for (int i = 0; i < resolvedIndex; i++) {
          wordStart += words[i].length + 1;
        }
        final wordEnd = wordStart + words[resolvedIndex].length;
        final boxes = painter.getBoxesForSelection(
          TextSelection(baseOffset: wordStart, extentOffset: wordEnd),
        );
        expect(boxes.length, 1, reason: 'word spanned multiple boxes');

        results.add({
          'panel': panelId,
          'line': lineId,
          'x': topLeft.dx,
          'yBaseline': topLeft.dy + baseline,
          'word': words[resolvedIndex],
          'wordLeft': topLeft.dx + boxes.first.left,
          'wordRight': topLeft.dx + boxes.first.right,
        });
      }
    }

    // ignore: avoid_print
    print('BASELINES_JSON ${jsonEncode(results)}');

    // File I/O uses real async callbacks the fake test clock never drives.
    await tester.runAsync(() async {
      final file = File('out/baselines.json');
      await file.create(recursive: true);
      await file
          .writeAsString(const JsonEncoder.withIndent('  ').convert(results));
    });
  });
}
