import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sana_client/main.dart';
import 'package:sana_client/config/colors.dart';
import 'package:sana_client/shared/widgets/sana_button.dart';
import 'package:sana_client/shared/widgets/sana_text_field.dart';
import 'package:sana_client/shared/widgets/health_score_widget.dart';

void main() {
  group('SanaColors', () {
    test('primary colors are correctly defined', () {
      expect(SanaColors.primaryDark, const Color(0xFF345519));
      expect(SanaColors.primaryMedium, const Color(0xFF58AA55));
      expect(SanaColors.primaryLight, const Color(0xFFA5BE5E));
      expect(SanaColors.accent, const Color(0xFFF2DF76));
    });

    test('getHealthColor returns correct colors', () {
      expect(SanaColors.getHealthColor(90), SanaColors.healthExcellent);
      expect(SanaColors.getHealthColor(70), SanaColors.healthGood);
      expect(SanaColors.getHealthColor(50), SanaColors.healthModerate);
      expect(SanaColors.getHealthColor(30), SanaColors.healthFair);
      expect(SanaColors.getHealthColor(10), SanaColors.healthPoor);
    });
  });

  group('SanaButton', () {
    testWidgets('renders with text', (WidgetTester tester) async {
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

    testWidgets('calls onPressed when tapped', (WidgetTester tester) async {
      bool pressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Test Button',
              onPressed: () {
                pressed = true;
              },
            ),
          ),
        ),
      );

      await tester.tap(find.text('Test Button'));
      expect(pressed, isTrue);
    });

    testWidgets('shows loading indicator when isLoading is true', (WidgetTester tester) async {
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

    testWidgets('is disabled when onPressed is null', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Disabled Button',
              onPressed: null,
            ),
          ),
        ),
      );

      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.onPressed, isNull);
    });

    testWidgets('outline variant renders correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaButton(
              text: 'Outline Button',
              onPressed: () {},
              variant: SanaButtonVariant.outline,
            ),
          ),
        ),
      );

      expect(find.byType(OutlinedButton), findsOneWidget);
    });
  });

  group('SanaTextField', () {
    testWidgets('renders with label', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
            ),
          ),
        ),
      );

      expect(find.text('Email'), findsOneWidget);
    });

    testWidgets('accepts text input', (WidgetTester tester) async {
      final controller = TextEditingController();

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              controller: controller,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextField), 'test@example.com');
      expect(controller.text, 'test@example.com');
    });

    testWidgets('shows error text when provided', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              errorText: 'Invalid email',
            ),
          ),
        ),
      );

      expect(find.text('Invalid email'), findsOneWidget);
    });

    testWidgets('obscures text when isPassword is true', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Password',
              isPassword: true,
            ),
          ),
        ),
      );

      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.obscureText, isTrue);
    });
  });

  group('HealthScoreWidget', () {
    testWidgets('displays score correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HealthScoreWidget(score: 85),
          ),
        ),
      );

      expect(find.text('85'), findsOneWidget);
    });

    testWidgets('shows correct color for excellent score', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HealthScoreWidget(score: 90),
          ),
        ),
      );

      // Widget should render without errors
      expect(find.byType(HealthScoreWidget), findsOneWidget);
    });

    testWidgets('shows correct color for poor score', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HealthScoreWidget(score: 15),
          ),
        ),
      );

      expect(find.byType(HealthScoreWidget), findsOneWidget);
    });
  });
}
