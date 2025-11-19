import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'config/theme.dart';
import 'config/routes.dart';

class SanaApp extends ConsumerWidget {
  const SanaApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'SANA',
      debugShowCheckedModeBanner: false,
      theme: SanaTheme.lightTheme,
      routerConfig: router,
    );
  }
}
