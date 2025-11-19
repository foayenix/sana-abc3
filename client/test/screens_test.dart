import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sana_client/features/auth/screens/login_screen.dart';
import 'package:sana_client/features/auth/screens/register_screen.dart';
import 'package:sana_client/features/home/screens/home_screen.dart';
import 'package:sana_client/features/search/screens/search_screen.dart';

void main() {
  group('LoginScreen', () {
    testWidgets('renders login form', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2)); // Email and password
      expect(find.text('Sign In'), findsOneWidget);
    });

    testWidgets('shows register link', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      expect(find.text("Don't have an account?"), findsOneWidget);
      expect(find.text('Sign Up'), findsOneWidget);
    });

    testWidgets('shows forgot password link', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      expect(find.text('Forgot Password?'), findsOneWidget);
    });
  });

  group('RegisterScreen', () {
    testWidgets('renders registration form', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: RegisterScreen(),
          ),
        ),
      );

      expect(find.text('Create Account'), findsOneWidget);
      // Full name, email, password, confirm password
      expect(find.byType(TextFormField), findsNWidgets(4));
      expect(find.text('Sign Up'), findsOneWidget);
    });

    testWidgets('shows login link', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: RegisterScreen(),
          ),
        ),
      );

      expect(find.text('Already have an account?'), findsOneWidget);
    });
  });

  group('HomeScreen', () {
    testWidgets('renders home screen components', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );

      // Check for main sections
      expect(find.text('Your Health Score'), findsOneWidget);
      expect(find.text('Upcoming Sessions'), findsOneWidget);
      expect(find.text('Quick Actions'), findsOneWidget);
    });

    testWidgets('shows health score widget', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );

      // Health score should be displayed
      expect(find.byType(Container), findsWidgets);
    });
  });

  group('SearchScreen', () {
    testWidgets('renders search bar', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: SearchScreen(),
          ),
        ),
      );

      expect(find.byIcon(Icons.search), findsOneWidget);
      expect(find.text('Search practitioners...'), findsOneWidget);
    });

    testWidgets('shows filter chips', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: SearchScreen(),
          ),
        ),
      );

      // Check for specialty filter chips
      expect(find.byType(FilterChip), findsWidgets);
    });
  });
}
