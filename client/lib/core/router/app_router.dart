import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/onboarding_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/auth/screens/forgot_password_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/search/screens/search_screen.dart';
import '../../features/practitioner/screens/practitioner_profile_screen.dart';
import '../../features/booking/screens/booking_screen.dart';
import '../../features/sessions/screens/sessions_screen.dart';
import '../../features/sessions/screens/session_detail_screen.dart';
import '../../features/health/screens/health_screen.dart';
import '../../features/messaging/screens/messaging_screen.dart';
import '../../features/messaging/screens/chat_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/profile/screens/settings_screen.dart';
import '../../shared/widgets/main_scaffold.dart';

/// Route names
class AppRoutes {
  static const splash = '/';
  static const onboarding = '/onboarding';
  static const login = '/login';
  static const register = '/register';
  static const forgotPassword = '/forgot-password';
  static const home = '/home';
  static const search = '/search';
  static const practitioner = '/practitioner/:id';
  static const booking = '/booking/:practitionerId';
  static const sessions = '/sessions';
  static const sessionDetail = '/sessions/:id';
  static const health = '/health';
  static const messaging = '/messaging';
  static const chat = '/chat/:conversationId';
  static const profile = '/profile';
  static const settings = '/settings';
}

/// Router provider
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: AppRoutes.splash,
    debugLogDiagnostics: true,
    refreshListenable: GoRouterRefreshStream(ref),
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isLoading = authState.status == AuthStatus.loading ||
          authState.status == AuthStatus.initial;
      final currentPath = state.matchedLocation;

      // Public routes that don't require auth
      final publicRoutes = [
        AppRoutes.splash,
        AppRoutes.onboarding,
        AppRoutes.login,
        AppRoutes.register,
        AppRoutes.forgotPassword,
      ];

      // If still loading auth state, show splash
      if (isLoading && currentPath != AppRoutes.splash) {
        return AppRoutes.splash;
      }

      // If not authenticated and trying to access protected route
      if (!isAuthenticated && !publicRoutes.contains(currentPath)) {
        return AppRoutes.login;
      }

      // If authenticated and on auth pages, redirect to home
      if (isAuthenticated && publicRoutes.contains(currentPath)) {
        return AppRoutes.home;
      }

      return null;
    },
    routes: [
      // Auth routes
      GoRoute(
        path: AppRoutes.splash,
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: AppRoutes.onboarding,
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.register,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: AppRoutes.forgotPassword,
        builder: (context, state) => const ForgotPasswordScreen(),
      ),

      // Main app routes with shell
      ShellRoute(
        builder: (context, state, child) => MainScaffold(child: child),
        routes: [
          GoRoute(
            path: AppRoutes.home,
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: AppRoutes.search,
            builder: (context, state) => const SearchScreen(),
          ),
          GoRoute(
            path: AppRoutes.sessions,
            builder: (context, state) => const SessionsScreen(),
          ),
          GoRoute(
            path: AppRoutes.health,
            builder: (context, state) => const HealthScreen(),
          ),
          GoRoute(
            path: AppRoutes.profile,
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),

      // Detail routes (outside shell)
      GoRoute(
        path: AppRoutes.practitioner,
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return PractitionerProfileScreen(practitionerId: id);
        },
      ),
      GoRoute(
        path: AppRoutes.booking,
        builder: (context, state) {
          final practitionerId = int.parse(state.pathParameters['practitionerId']!);
          return BookingScreen(practitionerId: practitionerId);
        },
      ),
      GoRoute(
        path: AppRoutes.sessionDetail,
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return SessionDetailScreen(sessionId: id);
        },
      ),
      GoRoute(
        path: AppRoutes.messaging,
        builder: (context, state) => const MessagingScreen(),
      ),
      GoRoute(
        path: AppRoutes.chat,
        builder: (context, state) {
          final conversationId = int.parse(state.pathParameters['conversationId']!);
          return ChatScreen(conversationId: conversationId);
        },
      ),
      GoRoute(
        path: AppRoutes.settings,
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.matchedLocation}'),
      ),
    ),
  );
});

/// Helper to refresh router when auth state changes
class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(this._ref) {
    _ref.listen(authProvider, (previous, next) {
      notifyListeners();
    });
  }

  final Ref _ref;
}
