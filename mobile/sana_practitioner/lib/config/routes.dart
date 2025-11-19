import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/screens/splash_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/register_screen.dart';
import '../features/dashboard/screens/dashboard_screen.dart';
import '../features/dashboard/screens/main_shell.dart';
import '../features/calendar/screens/calendar_screen.dart';
import '../features/calendar/screens/availability_screen.dart';
import '../features/clients/screens/clients_screen.dart';
import '../features/clients/screens/client_detail_screen.dart';
import '../features/sessions/screens/sessions_screen.dart';
import '../features/sessions/screens/session_detail_screen.dart';
import '../features/analytics/screens/analytics_screen.dart';
import '../features/earnings/screens/earnings_screen.dart';
import '../features/earnings/screens/payout_screen.dart';
import '../features/messages/screens/messages_screen.dart';
import '../features/messages/screens/chat_screen.dart';
import '../features/profile/screens/profile_screen.dart';
import '../features/profile/screens/edit_profile_screen.dart';
import '../features/profile/screens/practice_settings_screen.dart';
import '../features/profile/screens/services_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String dashboard = '/dashboard';
  static const String calendar = '/calendar';
  static const String availability = '/calendar/availability';
  static const String clients = '/clients';
  static const String clientDetail = '/clients/:id';
  static const String sessions = '/sessions';
  static const String sessionDetail = '/sessions/:id';
  static const String analytics = '/analytics';
  static const String earnings = '/earnings';
  static const String payout = '/earnings/payout';
  static const String messages = '/messages';
  static const String chat = '/messages/:conversationId';
  static const String profile = '/profile';
  static const String editProfile = '/profile/edit';
  static const String practiceSettings = '/profile/practice';
  static const String services = '/profile/services';
}

final router = GoRouter(
  initialLocation: AppRoutes.splash,
  routes: [
    GoRoute(
      path: AppRoutes.splash,
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: AppRoutes.login,
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: AppRoutes.register,
      builder: (context, state) => const RegisterScreen(),
    ),

    // Main app shell with bottom navigation
    ShellRoute(
      builder: (context, state, child) => MainShell(child: child),
      routes: [
        GoRoute(
          path: AppRoutes.dashboard,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: DashboardScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.calendar,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: CalendarScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.clients,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ClientsScreen(),
          ),
        ),
        GoRoute(
          path: AppRoutes.analytics,
          pageBuilder: (context, state) => const NoTransitionPage(
            child: AnalyticsScreen(),
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
      path: AppRoutes.availability,
      builder: (context, state) => const AvailabilityScreen(),
    ),
    GoRoute(
      path: AppRoutes.clientDetail,
      builder: (context, state) => ClientDetailScreen(
        clientId: state.pathParameters['id']!,
      ),
    ),
    GoRoute(
      path: AppRoutes.sessions,
      builder: (context, state) => const SessionsScreen(),
    ),
    GoRoute(
      path: AppRoutes.sessionDetail,
      builder: (context, state) => SessionDetailScreen(
        sessionId: state.pathParameters['id']!,
      ),
    ),
    GoRoute(
      path: AppRoutes.earnings,
      builder: (context, state) => const EarningsScreen(),
    ),
    GoRoute(
      path: AppRoutes.payout,
      builder: (context, state) => const PayoutScreen(),
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
      path: AppRoutes.practiceSettings,
      builder: (context, state) => const PracticeSettingsScreen(),
    ),
    GoRoute(
      path: AppRoutes.services,
      builder: (context, state) => const ServicesScreen(),
    ),
  ],
);
