# SANA Health Client App - Setup Guide

## Quick Start

### Prerequisites
- Flutter 3.2+ installed
- Android Studio or Xcode (for emulators)
- VSCode with Flutter extension

### 1. Install Dependencies

```bash
cd client
flutter pub get
```

### 2. Run the App

```bash
# Development mode
flutter run

# With environment variables
flutter run --dart-define=ENVIRONMENT=development
```

### 3. Demo Credentials

```
Email: demo@sana.com
Password: demo123
```

---

## Full Setup

### Backend Configuration

1. **Set API URL** in `lib/config/environment.dart`:
   ```dart
   case 'development':
     return 'http://localhost:8000/api/v1';
   ```

2. **Seed the database**:
   ```bash
   cd ../backend
   python scripts/seed_data.py
   ```

### Firebase Setup

1. **Install FlutterFire CLI**:
   ```bash
   dart pub global activate flutterfire_cli
   ```

2. **Configure Firebase**:
   ```bash
   flutterfire configure
   ```

3. **Enable Firebase services** in the [Firebase Console](https://console.firebase.google.com):
   - Authentication (Email/Password)
   - Cloud Messaging
   - Analytics
   - Crashlytics

4. **iOS specific** - Add to `ios/Runner/Info.plist`:
   ```xml
   <key>FirebaseMessagingAutoInitEnabled</key>
   <false/>
   ```

### Stripe Setup

1. Get your publishable key from [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)

2. Run with Stripe key:
   ```bash
   flutter run --dart-define=STRIPE_PUBLISHABLE_KEY=pk_test_xxx
   ```

### Sentry Setup (Error Tracking)

1. Create project at [Sentry](https://sentry.io)

2. Get DSN and run:
   ```bash
   flutter run --dart-define=SENTRY_DSN=https://xxx@sentry.io/xxx
   ```

---

## Running Tests

```bash
# All tests
flutter test

# Specific test file
flutter test test/providers/auth_provider_test.dart

# With coverage
flutter test --coverage
```

---

## Building for Production

### Android

```bash
flutter build apk --release \
  --dart-define=ENVIRONMENT=production \
  --dart-define=STRIPE_PUBLISHABLE_KEY=pk_live_xxx \
  --dart-define=SENTRY_DSN=https://xxx@sentry.io/xxx
```

### iOS

```bash
flutter build ios --release \
  --dart-define=ENVIRONMENT=production \
  --dart-define=STRIPE_PUBLISHABLE_KEY=pk_live_xxx \
  --dart-define=SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## Project Structure

```
client/
├── lib/
│   ├── config/           # Theme, colors, environment
│   ├── core/
│   │   ├── api/          # API client and services
│   │   ├── providers/    # Riverpod state providers
│   │   ├── router/       # GoRouter configuration
│   │   ├── services/     # Firebase, error tracking
│   │   └── storage/      # Secure storage
│   ├── features/
│   │   ├── auth/         # Login, register, forgot password
│   │   ├── home/         # Home dashboard
│   │   ├── search/       # Practitioner search
│   │   ├── practitioner/ # Practitioner profile
│   │   ├── booking/      # Booking wizard
│   │   ├── sessions/     # Sessions list and details
│   │   ├── health/       # Health tracking
│   │   ├── messaging/    # Chat and conversations
│   │   └── profile/      # User profile and settings
│   └── shared/
│       └── widgets/      # Reusable components
├── assets/
│   ├── images/           # App images
│   ├── icons/            # App icons
│   └── fonts/            # Custom fonts
└── test/                 # Unit and widget tests
```

---

## Troubleshooting

### App won't start
- Run `flutter clean && flutter pub get`
- Check that backend is running at configured URL

### Firebase errors
- Ensure `google-services.json` (Android) or `GoogleService-Info.plist` (iOS) is in place
- Run `flutterfire configure` to regenerate

### Build errors
- Update Flutter: `flutter upgrade`
- Check pubspec.yaml for version conflicts

---

## Support

For issues or questions:
- Check the [Flutter docs](https://docs.flutter.dev)
- Review app logs in VSCode Debug Console
