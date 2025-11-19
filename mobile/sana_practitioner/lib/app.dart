import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'config/theme.dart';
import 'config/routes.dart';

class SanaPractitionerApp extends ConsumerWidget {
  const SanaPractitionerApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'SANA Practitioner',
      debugShowCheckedModeBanner: false,
      theme: SanaTheme.lightTheme,
      routerConfig: router,
    );
  }
}
