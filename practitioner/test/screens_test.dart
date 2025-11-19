import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sana_practitioner/features/auth/screens/login_screen.dart';
import 'package:sana_practitioner/features/dashboard/screens/dashboard_screen.dart';
import 'package:sana_practitioner/features/calendar/screens/calendar_screen.dart';
import 'package:sana_practitioner/features/clients/screens/clients_screen.dart';
import 'package:sana_practitioner/features/earnings/screens/earnings_screen.dart';

void main() {
  group('PractitionerLoginScreen', () {
    testWidgets('renders login form', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      expect(find.text('Practitioner Portal'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2));
      expect(find.text('Sign In'), findsOneWidget);
    });
  });

  group('DashboardScreen', () {
    testWidgets('renders dashboard metrics', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: DashboardScreen(),
          ),
        ),
      );

      // Check for metric sections
      expect(find.text("Today's Sessions"), findsOneWidget);
      expect(find.text('This Week'), findsOneWidget);
      expect(find.text('This Month'), findsOneWidget);
    });

    testWidgets('shows upcoming appointments', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: DashboardScreen(),
          ),
        ),
      );

      expect(find.text('Upcoming Appointments'), findsOneWidget);
    });

    testWidgets('shows revenue overview', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: DashboardScreen(),
          ),
        ),
      );

      expect(find.text('Revenue'), findsOneWidget);
    });
  });

  group('CalendarScreen', () {
    testWidgets('renders calendar view', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: CalendarScreen(),
          ),
        ),
      );

      expect(find.text('Calendar'), findsOneWidget);
    });

    testWidgets('shows view toggle', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: CalendarScreen(),
          ),
        ),
      );

      // Should have day/week/month toggle
      expect(find.byType(SegmentedButton), findsOneWidget);
    });
  });

  group('ClientsScreen', () {
    testWidgets('renders clients list', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: ClientsScreen(),
          ),
        ),
      );

      expect(find.text('Clients'), findsOneWidget);
      expect(find.byIcon(Icons.search), findsOneWidget);
    });

    testWidgets('shows client count', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: ClientsScreen(),
          ),
        ),
      );

      // Should show total clients
      expect(find.textContaining('Total'), findsOneWidget);
    });
  });

  group('EarningsScreen', () {
    testWidgets('renders earnings overview', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: EarningsScreen(),
          ),
        ),
      );

      expect(find.text('Earnings'), findsOneWidget);
    });

    testWidgets('shows period selector', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: EarningsScreen(),
          ),
        ),
      );

      // Should have time period tabs
      expect(find.byType(TabBar), findsOneWidget);
    });

    testWidgets('shows payout section', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: EarningsScreen(),
          ),
        ),
      );

      expect(find.text('Pending Payout'), findsOneWidget);
    });
  });
}
