import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'config/theme.dart';
import 'config/colors.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/dashboard/screens/dashboard_screen.dart';
import 'features/users/screens/users_screen.dart';
import 'features/practitioners/screens/practitioners_screen.dart';
import 'features/analytics/screens/analytics_screen.dart';
import 'features/settings/screens/settings_screen.dart';

void main() {
  runApp(const ProviderScope(child: SanaAdminApp()));
}

final _router = GoRouter(
  initialLocation: '/dashboard',
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
    ShellRoute(
      builder: (_, __, child) => AdminShell(child: child),
      routes: [
        GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
        GoRoute(path: '/users', builder: (_, __) => const UsersScreen()),
        GoRoute(path: '/practitioners', builder: (_, __) => const PractitionersScreen()),
        GoRoute(path: '/analytics', builder: (_, __) => const AnalyticsScreen()),
        GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
      ],
    ),
  ],
);

class SanaAdminApp extends StatelessWidget {
  const SanaAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'SANA Admin',
      debugShowCheckedModeBanner: false,
      theme: SanaTheme.lightTheme,
      routerConfig: _router,
    );
  }
}

class AdminShell extends StatelessWidget {
  final Widget child;
  const AdminShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Sidebar
          Container(
            width: 250,
            color: SanaColors.primaryDark,
            child: Column(
              children: [
                const SizedBox(height: 32),
                const Text('SANA', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: SanaColors.white, letterSpacing: 4)),
                const Text('Admin', style: TextStyle(color: SanaColors.white, fontSize: 12)),
                const SizedBox(height: 48),
                _NavItem(icon: Icons.dashboard, label: 'Dashboard', path: '/dashboard'),
                _NavItem(icon: Icons.people, label: 'Users', path: '/users'),
                _NavItem(icon: Icons.verified_user, label: 'Practitioners', path: '/practitioners'),
                _NavItem(icon: Icons.analytics, label: 'Analytics', path: '/analytics'),
                _NavItem(icon: Icons.settings, label: 'Settings', path: '/settings'),
                const Spacer(),
                _NavItem(icon: Icons.logout, label: 'Logout', path: '/login'),
                const SizedBox(height: 24),
              ],
            ),
          ),
          // Content
          Expanded(child: child),
        ],
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String path;

  const _NavItem({required this.icon, required this.label, required this.path});

  @override
  Widget build(BuildContext context) {
    final isSelected = GoRouterState.of(context).uri.path == path;
    return ListTile(
      leading: Icon(icon, color: isSelected ? SanaColors.accent : SanaColors.white.withOpacity(0.7)),
      title: Text(label, style: TextStyle(color: isSelected ? SanaColors.accent : SanaColors.white.withOpacity(0.9), fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400)),
      selected: isSelected,
      selectedTileColor: SanaColors.white.withOpacity(0.1),
      onTap: () => context.go(path),
    );
  }
}
