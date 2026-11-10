import 'dart:async';

import 'package:bc_golden_plugin/bc_golden_plugin.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  TestWidgetsFlutterBinding.ensureInitialized();

  final bcGoldenConfiguration = BcGoldenConfiguration();
  bcGoldenConfiguration.setThresholdRatio(0.005);

  await loadConfiguration();

  await testMain();
}
