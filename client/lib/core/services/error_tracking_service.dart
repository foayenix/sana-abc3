import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import '../../config/environment.dart';

/// Error tracking service using Sentry
class ErrorTrackingService {
  static final ErrorTrackingService _instance = ErrorTrackingService._internal();
  factory ErrorTrackingService() => _instance;
  ErrorTrackingService._internal();

  /// Initialize Sentry
  static Future<void> initialize() async {
    if (!Environment.enableCrashReporting) {
      debugPrint('Error tracking disabled in development');
      return;
    }

    await SentryFlutter.init(
      (options) {
        options.dsn = const String.fromEnvironment(
          'SENTRY_DSN',
          defaultValue: 'https://your-sentry-dsn@sentry.io/project-id',
        );
        options.environment = Environment.environment;
        options.tracesSampleRate = 0.2;
        options.profilesSampleRate = 0.2;
        options.attachScreenshot = true;
        options.attachViewHierarchy = true;
        options.sendDefaultPii = false;

        // Filter sensitive data
        options.beforeSend = (event, {hint}) {
          // Remove sensitive data from breadcrumbs
          if (event.breadcrumbs != null) {
            event = event.copyWith(
              breadcrumbs: event.breadcrumbs!
                  .where((b) => !_containsSensitiveData(b.message))
                  .toList(),
            );
          }
          return event;
        };
      },
    );
  }

  /// Check if breadcrumb contains sensitive data
  static bool _containsSensitiveData(String? message) {
    if (message == null) return false;
    final sensitivePatterns = [
      'password',
      'token',
      'secret',
      'api_key',
      'credit_card',
    ];
    return sensitivePatterns.any(
      (pattern) => message.toLowerCase().contains(pattern),
    );
  }

  /// Capture exception
  Future<void> captureException(
    dynamic exception, {
    StackTrace? stackTrace,
    String? message,
    Map<String, dynamic>? extras,
  }) async {
    if (!Environment.enableCrashReporting) {
      debugPrint('Error: $exception');
      return;
    }

    await Sentry.captureException(
      exception,
      stackTrace: stackTrace,
      withScope: (scope) {
        if (message != null) {
          scope.setExtra('message', message);
        }
        if (extras != null) {
          extras.forEach((key, value) {
            scope.setExtra(key, value);
          });
        }
      },
    );
  }

  /// Capture message
  Future<void> captureMessage(
    String message, {
    SentryLevel level = SentryLevel.info,
    Map<String, dynamic>? extras,
  }) async {
    if (!Environment.enableCrashReporting) {
      debugPrint('Message: $message');
      return;
    }

    await Sentry.captureMessage(
      message,
      level: level,
      withScope: (scope) {
        if (extras != null) {
          extras.forEach((key, value) {
            scope.setExtra(key, value);
          });
        }
      },
    );
  }

  /// Add breadcrumb
  Future<void> addBreadcrumb({
    required String message,
    String? category,
    Map<String, dynamic>? data,
    SentryLevel level = SentryLevel.info,
  }) async {
    if (!Environment.enableCrashReporting) return;

    await Sentry.addBreadcrumb(
      Breadcrumb(
        message: message,
        category: category,
        data: data,
        level: level,
        timestamp: DateTime.now(),
      ),
    );
  }

  /// Set user context
  Future<void> setUser({
    required String id,
    String? email,
    String? username,
    Map<String, dynamic>? extras,
  }) async {
    if (!Environment.enableCrashReporting) return;

    await Sentry.configureScope((scope) {
      scope.setUser(SentryUser(
        id: id,
        email: email,
        username: username,
        data: extras,
      ));
    });
  }

  /// Clear user context
  Future<void> clearUser() async {
    if (!Environment.enableCrashReporting) return;

    await Sentry.configureScope((scope) {
      scope.setUser(null);
    });
  }

  /// Set tag
  Future<void> setTag(String key, String value) async {
    if (!Environment.enableCrashReporting) return;

    await Sentry.configureScope((scope) {
      scope.setTag(key, value);
    });
  }

  /// Set extra data
  Future<void> setExtra(String key, dynamic value) async {
    if (!Environment.enableCrashReporting) return;

    await Sentry.configureScope((scope) {
      scope.setExtra(key, value);
    });
  }

  /// Start transaction for performance monitoring
  ISentrySpan startTransaction({
    required String name,
    required String operation,
  }) {
    return Sentry.startTransaction(name, operation);
  }

  /// Wrap async function with error handling
  Future<T> wrapAsync<T>(
    Future<T> Function() fn, {
    String? operation,
  }) async {
    try {
      return await fn();
    } catch (e, stackTrace) {
      await captureException(
        e,
        stackTrace: stackTrace,
        message: operation,
      );
      rethrow;
    }
  }
}

/// Extension to make error tracking easier
extension ErrorTrackingExtension on Object {
  Future<void> reportError({
    StackTrace? stackTrace,
    String? message,
  }) async {
    await ErrorTrackingService().captureException(
      this,
      stackTrace: stackTrace,
      message: message,
    );
  }
}
