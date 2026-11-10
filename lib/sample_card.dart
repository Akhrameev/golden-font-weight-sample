import 'package:flutter/material.dart';

/// A 360x300 card: a light panel on top, a dark panel on the bottom.
/// Each panel shows the same four Work Sans lines, each line a different
/// weight: 28 Bold, 16 SemiBold, 16 Regular, 14 Thin.
class SampleCard extends StatelessWidget {
  const SampleCard({super.key});

  static const double width = 360;
  static const double height = 300;
  static const double panelHeight = 150;
  static const EdgeInsets panelPadding = EdgeInsets.all(16);
  static const double lineGap = 4;

  static const String lineBold = 'From days to hours';
  static const String lineSemiBold = 'Golden tests love pixels. So do we.';
  static const String lineRegular = 'Every glyph comes from the same file.';
  static const String lineThin = 'Thin weights feel it the most: 0123456789';

  static const Color lightBg = Color(0xFFFFFFFF);
  static const Color lightFg = Color(0xFF111111);
  static const Color darkBg = Color(0xFF111111);
  static const Color darkFg = Color(0xFFFFFFFF);

  static TextStyle _style(double fontSize, FontWeight weight, Color color) {
    return TextStyle(
      inherit: false,
      fontFamily: 'Work Sans',
      fontSize: fontSize,
      fontWeight: weight,
      color: color,
      letterSpacing: 0,
    );
  }

  static Widget _panel(String panelId, Color bg, Color fg) {
    return Container(
      width: width,
      height: panelHeight,
      color: bg,
      padding: panelPadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            lineBold,
            key: ValueKey('$panelId-bold'),
            style: _style(28, FontWeight.w700, fg),
          ),
          const SizedBox(height: lineGap),
          Text(
            lineSemiBold,
            key: ValueKey('$panelId-semibold'),
            style: _style(16, FontWeight.w600, fg),
          ),
          const SizedBox(height: lineGap),
          Text(
            lineRegular,
            key: ValueKey('$panelId-regular'),
            style: _style(16, FontWeight.w400, fg),
          ),
          const SizedBox(height: lineGap),
          Text(
            lineThin,
            key: ValueKey('$panelId-thin'),
            style: _style(14, FontWeight.w100, fg),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _panel('light', lightBg, lightFg),
          _panel('dark', darkBg, darkFg),
        ],
      ),
    );
  }
}
