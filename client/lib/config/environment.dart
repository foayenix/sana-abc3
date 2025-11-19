/// Environment configuration for SANA Client App
class Environment {
  // Private constructor
  Environment._();

  /// Current environment
  static const String environment = String.fromEnvironment(
    'ENVIRONMENT',
    defaultValue: 'development',
  );

  /// API Base URL
  static String get apiBaseUrl {
    switch (environment) {
      case 'production':
        return 'https://api.sana-health.com/api/v1';
      case 'staging':
        return 'https://staging-api.sana-health.com/api/v1';
      default:
        return 'http://localhost:8000/api/v1';
    }
  }

  /// WebSocket URL
  static String get wsUrl {
    switch (environment) {
      case 'production':
        return 'wss://api.sana-health.com/ws';
      case 'staging':
        return 'wss://staging-api.sana-health.com/ws';
      default:
        return 'ws://localhost:8000/ws';
    }
  }

  /// Stripe Publishable Key
  static String get stripePublishableKey {
    switch (environment) {
      case 'production':
        return const String.fromEnvironment(
          'STRIPE_PUBLISHABLE_KEY',
          defaultValue: 'pk_live_your_key_here',
        );
      default:
        return const String.fromEnvironment(
          'STRIPE_PUBLISHABLE_KEY',
          defaultValue: 'pk_test_your_test_key_here',
        );
    }
  }

  /// Enable debug mode
  static bool get isDebug => environment == 'development';

  /// Enable analytics
  static bool get enableAnalytics => environment != 'development';

  /// Enable crash reporting
  static bool get enableCrashReporting => environment != 'development';

  /// API timeout in seconds
  static int get apiTimeout => 30;

  /// Image upload max size in MB
  static int get maxImageSize => 10;

  /// Session timeout in minutes
  static int get sessionTimeout => 60;
}

/// Feature flags
class FeatureFlags {
  FeatureFlags._();

  /// Enable video sessions
  static const bool enableVideoSessions = true;

  /// Enable chat attachments
  static const bool enableChatAttachments = true;

  /// Enable health questionnaire
  static const bool enableHealthQuestionnaire = true;

  /// Enable push notifications
  static const bool enablePushNotifications = true;

  /// Enable biometric authentication
  static const bool enableBiometricAuth = false;

  /// Enable dark mode
  static const bool enableDarkMode = true;

  /// Enable social login
  static const bool enableSocialLogin = false;
}
