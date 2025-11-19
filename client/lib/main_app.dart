import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'config/theme.dart';
import 'core/router/app_router.dart';

/// Main app with Riverpod and GoRouter
class SanaClientApp extends ConsumerWidget {
  const SanaClientApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'SANA Health',
      theme: SanaTheme.lightTheme,
      darkTheme: SanaTheme.darkTheme,
      themeMode: ThemeMode.light,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}

/// App entry point
void main() {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(
    const ProviderScope(
      child: SanaClientApp(),
    ),
  );
}
