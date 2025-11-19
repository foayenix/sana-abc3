import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/screens/splash_screen.dart';
import '../features/auth/screens/onboarding_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/register_screen.dart';
import '../features/auth/screens/forgot_password_screen.dart';
import '../features/home/screens/home_screen.dart';
import '../features/home/screens/main_shell.dart';
import '../features/search/screens/search_screen.dart';
import '../features/practitioner/screens/practitioner_profile_screen.dart';
import '../features/booking/screens/booking_screen.dart';
import '../features/booking/screens/booking_confirmation_screen.dart';
import '../features/sessions/screens/sessions_screen.dart';
import '../features/sessions/screens/session_detail_screen.dart';
import '../features/health/screens/health_screen.dart';
import '../features/health/screens/journal_screen.dart';
import '../features/messages/screens/messages_screen.dart';
import '../features/messages/screens/chat_screen.dart';
import '../features/profile/screens/profile_screen.dart';
import '../features/profile/screens/edit_profile_screen.dart';
import '../features/profile/screens/settings_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String home = '/home';
  static const String search = '/search';
  static const String practitioner = '/practitioner/:id';
  static const String booking = '/booking/:practitionerId';
  static const String bookingConfirmation = '/booking/confirmation';
  static const String sessions = '/sessions';
  static const String sessionDetail = '/sessions/:id';
  static const String health = '/health';
  static const String journal = '/health/journal';
  static const String messages = '/messages';
  static const String chat = '/messages/:conversationId';
  static const String profile = '/profile';
  static const String editProfile = '/profile/edit';
  static const String settings = '/settings';
}

final router = GoRouter(
  initialLocation: AppRoutes.splash,
  routes: [
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

    // Main app shell with bottom navigation
    ShellRoute(
      builder: (context, state, child) => MainShell(child: child),
      routes: [
        GoRoute(
          path: AppRoutes.home,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: HomeScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.search,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: SearchScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.sessions,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: SessionsScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.health,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: HealthScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.messages,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: MessagesScreen(),
          ),
        ),
      ],
    ),

    // Detail screens outside shell
    GoRoute(
      path: AppRoutes.practitioner,
      builder: (context, state) => PractitionerProfileScreen(
        practitionerId: state.pathParameters['id']!,
      ),
    ),
    GoRoute(
      path: AppRoutes.booking,
      builder: (context, state) => BookingScreen(
        practitionerId: state.pathParameters['practitionerId']!,
      ),
    ),
    GoRoute(
      path: AppRoutes.bookingConfirmation,
      builder: (context, state) => const BookingConfirmationScreen(),
    ),
    GoRoute(
      path: AppRoutes.sessionDetail,
      builder: (context, state) => SessionDetailScreen(
        sessionId: state.pathParameters['id']!,
      ),
    ),
    GoRoute(
      path: AppRoutes.journal,
      builder: (context, state) => const JournalScreen(),
    ),
    GoRoute(
      path: AppRoutes.chat,
      builder: (context, state) => ChatScreen(
        conversationId: state.pathParameters['conversationId']!,
      ),
    ),
    GoRoute(
      path: AppRoutes.profile,
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: AppRoutes.editProfile,
      builder: (context, state) => const EditProfileScreen(),
    ),
    GoRoute(
      path: AppRoutes.settings,
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);
