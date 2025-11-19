import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:flutter/foundation.dart';
import '../../config/environment.dart';

/// Firebase service for push notifications, analytics, and crash reporting
class FirebaseService {
  static final FirebaseService _instance = FirebaseService._internal();
  factory FirebaseService() => _instance;
  FirebaseService._internal();

  late FirebaseMessaging _messaging;
  late FirebaseAnalytics _analytics;

  /// Initialize Firebase services
  Future<void> initialize() async {
    await Firebase.initializeApp();

    _messaging = FirebaseMessaging.instance;
    _analytics = FirebaseAnalytics.instance;

    // Configure Crashlytics
    if (Environment.enableCrashReporting) {
      FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;

      // Pass all uncaught asynchronous errors to Crashlytics
      PlatformDispatcher.instance.onError = (error, stack) {
        FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
        return true;
      };
    }

    // Configure push notifications
    await _configurePushNotifications();
  }

  /// Configure push notifications
  Future<void> _configurePushNotifications() async {
    // Request permission
    NotificationSettings settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      debugPrint('Push notifications authorized');

      // Get FCM token
      String? token = await _messaging.getToken();
      debugPrint('FCM Token: $token');

      // Listen for token refresh
      _messaging.onTokenRefresh.listen((newToken) {
        debugPrint('FCM Token refreshed: $newToken');
        // TODO: Send new token to backend
      });

      // Handle foreground messages
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

      // Handle background messages
      FirebaseMessaging.onBackgroundMessage(_handleBackgroundMessage);

      // Handle notification tap when app was terminated
      RemoteMessage? initialMessage = await _messaging.getInitialMessage();
      if (initialMessage != null) {
        _handleNotificationTap(initialMessage);
      }

      // Handle notification tap when app was in background
      FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
    }
  }

  /// Handle foreground message
  void _handleForegroundMessage(RemoteMessage message) {
    debugPrint('Foreground message: ${message.notification?.title}');
    // TODO: Show local notification or in-app banner
  }

  /// Handle notification tap
  void _handleNotificationTap(RemoteMessage message) {
    debugPrint('Notification tapped: ${message.data}');
    // TODO: Navigate to relevant screen based on message.data
  }

  /// Get FCM token
  Future<String?> getToken() async {
    return await _messaging.getToken();
  }

  /// Subscribe to topic
  Future<void> subscribeToTopic(String topic) async {
    await _messaging.subscribeToTopic(topic);
  }

  /// Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    await _messaging.unsubscribeFromTopic(topic);
  }

  // Analytics methods

  /// Log custom event
  Future<void> logEvent({
    required String name,
    Map<String, Object>? parameters,
  }) async {
    if (Environment.enableAnalytics) {
      await _analytics.logEvent(name: name, parameters: parameters);
    }
  }

  /// Log screen view
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  }) async {
    if (Environment.enableAnalytics) {
      await _analytics.logScreenView(
        screenName: screenName,
        screenClass: screenClass,
      );
    }
  }

  /// Set user ID for analytics
  Future<void> setUserId(String userId) async {
    if (Environment.enableAnalytics) {
      await _analytics.setUserId(id: userId);
    }
  }

  /// Set user property
  Future<void> setUserProperty({
    required String name,
    required String value,
  }) async {
    if (Environment.enableAnalytics) {
      await _analytics.setUserProperty(name: name, value: value);
    }
  }

  /// Log login event
  Future<void> logLogin(String method) async {
    if (Environment.enableAnalytics) {
      await _analytics.logLogin(loginMethod: method);
    }
  }

  /// Log sign up event
  Future<void> logSignUp(String method) async {
    if (Environment.enableAnalytics) {
      await _analytics.logSignUp(signUpMethod: method);
    }
  }

  /// Log booking event
  Future<void> logBooking({
    required int practitionerId,
    required int serviceId,
    required double price,
  }) async {
    await logEvent(
      name: 'booking_created',
      parameters: {
        'practitioner_id': practitionerId,
        'service_id': serviceId,
        'price': price,
      },
    );
  }

  /// Log health tracking event
  Future<void> logHealthTracking(String type) async {
    await logEvent(
      name: 'health_tracked',
      parameters: {'type': type},
    );
  }

  // Crashlytics methods

  /// Log error to Crashlytics
  Future<void> logError(
    dynamic error,
    StackTrace? stackTrace, {
    String? reason,
    bool fatal = false,
  }) async {
    if (Environment.enableCrashReporting) {
      await FirebaseCrashlytics.instance.recordError(
        error,
        stackTrace,
        reason: reason,
        fatal: fatal,
      );
    }
  }

  /// Log message to Crashlytics
  Future<void> logMessage(String message) async {
    if (Environment.enableCrashReporting) {
      await FirebaseCrashlytics.instance.log(message);
    }
  }

  /// Set custom key for Crashlytics
  Future<void> setCustomKey(String key, dynamic value) async {
    if (Environment.enableCrashReporting) {
      await FirebaseCrashlytics.instance.setCustomKey(key, value);
    }
  }

  /// Set user identifier for Crashlytics
  Future<void> setCrashlyticsUserId(String userId) async {
    if (Environment.enableCrashReporting) {
      await FirebaseCrashlytics.instance.setUserIdentifier(userId);
    }
  }
}

/// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> _handleBackgroundMessage(RemoteMessage message) async {
  debugPrint('Background message: ${message.notification?.title}');
}
