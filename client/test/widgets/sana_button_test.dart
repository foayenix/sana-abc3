import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sana_client/shared/widgets/sana_button.dart';

void main() {
  group('SanaButton', () {
    testWidgets('renders with text', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {},
            ),
          ),
        ),
      );

      expect(find.text('Test Button'), findsOneWidget);
    });

    testWidgets('calls onPressed when tapped', (tester) async {
      bool pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () => pressed = true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(SanaButton));
      expect(pressed, isTrue);
    });

    testWidgets('shows loading indicator when isLoading is true',
        (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {},
              isLoading: true,
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Test Button'), findsNothing);
    });

    testWidgets('is disabled when onPressed is null', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: null,
            ),
          ),
        ),
      );

      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.onPressed, isNull);
    });

    testWidgets('displays icon when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {},
              icon: Icons.add,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('outline variant renders OutlinedButton', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {},
              variant: SanaButtonVariant.outline,
            ),
          ),
        ),
      );

      expect(find.byType(OutlinedButton), findsOneWidget);
    });

    testWidgets('text variant renders TextButton', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {},
              variant: SanaButtonVariant.text,
            ),
          ),
        ),
      );

      expect(find.byType(TextButton), findsOneWidget);
    });

    testWidgets('respects custom width', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {},
              width: 200,
            ),
          ),
        ),
      );

      final sizedBox = tester.widget<SizedBox>(find.byType(SizedBox));
      expect(sizedBox.width, 200);
    });
  });
}
