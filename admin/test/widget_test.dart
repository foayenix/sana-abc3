import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sana_admin/config/colors.dart';
import 'package:sana_admin/features/dashboard/screens/dashboard_screen.dart';
import 'package:sana_admin/features/users/screens/users_screen.dart';
import 'package:sana_admin/features/practitioners/screens/practitioners_screen.dart';
import 'package:sana_admin/features/analytics/screens/analytics_screen.dart';

void main() {
  group('SanaColors', () {
    test('primary colors are correctly defined', () {
      expect(SanaColors.primaryDark, const Color(0xFF345519));
      expect(SanaColors.primaryMedium, const Color(0xFF58AA55));
      expect(SanaColors.primaryLight, const Color(0xFFA5BE5E));
      expect(SanaColors.accent, const Color(0xFFF2DF76));
    });

    test('semantic colors are defined', () {
      expect(SanaColors.success, isA<Color>());
      expect(SanaColors.warning, isA<Color>());
      expect(SanaColors.error, isA<Color>());
      expect(SanaColors.info, isA<Color>());
    });
  });

  group('DashboardScreen', () {
    testWidgets('renders dashboard title', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: DashboardScreen(),
        ),
      );

      expect(find.text('Dashboard'), findsOneWidget);
    });

    testWidgets('shows stats cards', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: DashboardScreen(),
        ),
      );

      expect(find.text('Total Users'), findsOneWidget);
      expect(find.text('Practitioners'), findsOneWidget);
      expect(find.text('Sessions'), findsOneWidget);
      expect(find.text('Revenue'), findsOneWidget);
    });

    testWidgets('shows pending verifications', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: DashboardScreen(),
        ),
      );

      expect(find.text('Pending Verifications'), findsOneWidget);
    });

    testWidgets('shows recent activity', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: DashboardScreen(),
        ),
      );

      expect(find.text('Recent Activity'), findsOneWidget);
    });
  });

  group('UsersScreen', () {
    testWidgets('renders users table', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: UsersScreen(),
        ),
      );

      expect(find.text('Users'), findsOneWidget);
    });

    testWidgets('shows search and filter', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: UsersScreen(),
        ),
      );

      expect(find.byIcon(Icons.search), findsOneWidget);
      expect(find.byIcon(Icons.filter_list), findsOneWidget);
    });

    testWidgets('shows export button', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: UsersScreen(),
        ),
      );

      expect(find.text('Export'), findsOneWidget);
    });
  });

  group('PractitionersScreen', () {
    testWidgets('renders practitioners list', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: PractitionersScreen(),
        ),
      );

      expect(find.text('Practitioners'), findsOneWidget);
    });

    testWidgets('shows status tabs', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: PractitionersScreen(),
        ),
      );

      expect(find.byType(TabBar), findsOneWidget);
      expect(find.text('All'), findsOneWidget);
      expect(find.text('Pending'), findsOneWidget);
      expect(find.text('Verified'), findsOneWidget);
    });
  });

  group('AnalyticsScreen', () {
    testWidgets('renders analytics title', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: AnalyticsScreen(),
        ),
      );

      expect(find.text('Analytics'), findsOneWidget);
    });

    testWidgets('shows metric cards', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: AnalyticsScreen(),
        ),
      );

      // Should have various metric cards
      expect(find.byType(Container), findsWidgets);
    });

    testWidgets('shows charts section', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: AnalyticsScreen(),
        ),
      );

      expect(find.text('Bookings Over Time'), findsOneWidget);
    });
  });
}
