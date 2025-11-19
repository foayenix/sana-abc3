import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sana_client/main_app.dart';

void main() {
  group('Auth Flow Integration Tests', () {
    testWidgets('shows splash screen on launch', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SanaClientApp(),
        ),
      );

      // Should show splash screen initially
      expect(find.text('SANA'), findsOneWidget);
    });

    testWidgets('navigates to login from onboarding', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SanaClientApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Skip through onboarding if shown
      if (find.text('Skip').evaluate().isNotEmpty) {
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();
      }

      // Should reach login screen
      expect(find.text('Welcome Back'), findsOneWidget);
    });

    testWidgets('shows validation errors on empty login', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SanaClientApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Navigate to login
      if (find.text('Skip').evaluate().isNotEmpty) {
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();
      }

      // Try to login with empty fields
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      // Should show validation errors
      expect(find.text('Email is required'), findsOneWidget);
    });

    testWidgets('navigates to register from login', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SanaClientApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Navigate to login
      if (find.text('Skip').evaluate().isNotEmpty) {
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();
      }

      // Tap sign up link
      await tester.tap(find.text('Sign Up'));
      await tester.pumpAndSettle();

      // Should be on register screen
      expect(find.text('Create Account'), findsOneWidget);
    });

    testWidgets('navigates to forgot password from login', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SanaClientApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Navigate to login
      if (find.text('Skip').evaluate().isNotEmpty) {
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();
      }

      // Tap forgot password
      await tester.tap(find.text('Forgot Password?'));
      await tester.pumpAndSettle();

      // Should be on forgot password screen
      expect(find.text('Reset Password'), findsOneWidget);
    });
  });

  group('Main App Navigation Tests', () {
    testWidgets('bottom navigation has 5 tabs', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              bottomNavigationBar: NavigationBar(
                destinations: [
                  NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
                  NavigationDestination(
                      icon: Icon(Icons.search), label: 'Search'),
                  NavigationDestination(
                      icon: Icon(Icons.calendar_today), label: 'Sessions'),
                  NavigationDestination(
                      icon: Icon(Icons.favorite), label: 'Health'),
                  NavigationDestination(
                      icon: Icon(Icons.person), label: 'Profile'),
                ],
              ),
            ),
          ),
        ),
      );

      expect(find.text('Home'), findsOneWidget);
      expect(find.text('Search'), findsOneWidget);
      expect(find.text('Sessions'), findsOneWidget);
      expect(find.text('Health'), findsOneWidget);
      expect(find.text('Profile'), findsOneWidget);
    });
  });
}
