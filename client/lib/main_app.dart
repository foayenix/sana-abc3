import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'config/theme.dart';
import 'config/environment.dart';
import 'core/router/app_router.dart';
import 'core/services/firebase_service.dart';
import 'core/services/error_tracking_service.dart';

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
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize error tracking first to catch any initialization errors
  await ErrorTrackingService.initialize();

  // Initialize Firebase services
  try {
    await FirebaseService().initialize();
  } catch (e) {
    debugPrint('Firebase initialization failed: $e');
    // App can still run without Firebase in development
  }

  // Run app with error boundary
  runApp(
    const ProviderScope(
      child: SanaClientApp(),
    ),
  );
}

/// Error boundary widget for graceful error handling
class ErrorBoundary extends StatelessWidget {
  final Widget child;

  const ErrorBoundary({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    ErrorWidget.builder = (FlutterErrorDetails details) {
      // Log error to tracking service
      ErrorTrackingService().captureException(
        details.exception,
        stackTrace: details.stack,
        message: details.context?.toString(),
      );

      // Show user-friendly error in release mode
      if (kReleaseMode) {
        return MaterialApp(
          home: Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Colors.red,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Something went wrong',
                    style: TextStyle(fontSize: 18),
                  ),
                  const SizedBox(height: 8),
                  TextButton(
                    onPressed: () {
                      // Restart app
                    },
                    child: const Text('Try Again'),
                  ),
                ],
              ),
            ),
          ),
        );
      }

      // Show detailed error in debug mode
      return ErrorWidget(details.exception);
    };

    return child;
  }
}
