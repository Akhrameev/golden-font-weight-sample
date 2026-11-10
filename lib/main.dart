import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'sample_card.dart';

void main() {
  runApp(const SampleApp());
}

class SampleApp extends StatelessWidget {
  const SampleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFFCCCCCC),
        body: Center(
          child: _ReportingCard(child: const SampleCard()),
        ),
      ),
    );
  }
}

/// Wraps the card and prints its on-screen rect (in points) plus the device
/// pixel ratio, once laid out. Used to compute the exact pixel crop box for
/// a Simulator screenshot: see REPRODUCE.md section 4.
class _ReportingCard extends StatefulWidget {
  const _ReportingCard({required this.child});
  final Widget child;

  @override
  State<_ReportingCard> createState() => _ReportingCardState();
}

class _ReportingCardState extends State<_ReportingCard> {
  final GlobalKey _key = GlobalKey();
  bool _reported = false;

  @override
  Widget build(BuildContext context) {
    SchedulerBinding.instance.addPostFrameCallback((_) {
      if (_reported) return;
      final renderBox = _key.currentContext?.findRenderObject() as RenderBox?;
      if (renderBox == null || !renderBox.hasSize) return;
      _reported = true;
      final offset = renderBox.localToGlobal(Offset.zero);
      final size = renderBox.size;
      final dpr = MediaQuery.of(context).devicePixelRatio;
      // ignore: avoid_print
      print(
        'SAMPLE_RECT ${offset.dx} ${offset.dy} ${size.width} ${size.height} $dpr',
      );
    });
    return KeyedSubtree(key: _key, child: widget.child);
  }
}
