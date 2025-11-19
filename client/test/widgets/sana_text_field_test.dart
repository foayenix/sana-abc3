import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sana_client/shared/widgets/sana_text_field.dart';

void main() {
  group('SanaTextField', () {
    testWidgets('renders with label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              controller: TextEditingController(),
            ),
          ),
        ),
      );

      expect(find.text('Email'), findsOneWidget);
    });

    testWidgets('renders with hint', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              hint: 'Enter your email',
              controller: TextEditingController(),
            ),
          ),
        ),
      );

      expect(find.text('Enter your email'), findsOneWidget);
    });

    testWidgets('accepts input', (tester) async {
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

    testWidgets('obscures text when isPassword is true', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Password',
              controller: TextEditingController(),
              isPassword: true,
            ),
          ),
        ),
      );

      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.obscureText, isTrue);
    });

    testWidgets('shows toggle button for password field', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Password',
              controller: TextEditingController(),
              isPassword: true,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });

    testWidgets('toggles password visibility', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Password',
              controller: TextEditingController(),
              isPassword: true,
            ),
          ),
        ),
      );

      // Initially password is hidden
      TextField textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.obscureText, isTrue);

      // Tap toggle button
      await tester.tap(find.byIcon(Icons.visibility_off));
      await tester.pump();

      // Password should now be visible
      textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.obscureText, isFalse);
      expect(find.byIcon(Icons.visibility), findsOneWidget);
    });

    testWidgets('displays prefix icon', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              controller: TextEditingController(),
              prefixIcon: Icons.email,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.email), findsOneWidget);
    });

    testWidgets('displays suffix icon', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Search',
              controller: TextEditingController(),
              suffixIcon: Icons.search,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.search), findsOneWidget);
    });

    testWidgets('shows error message', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              controller: TextEditingController(),
              errorText: 'Invalid email',
            ),
          ),
        ),
      );

      expect(find.text('Invalid email'), findsOneWidget);
    });

    testWidgets('calls onChanged when text changes', (tester) async {
      String? changedText;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Email',
              controller: TextEditingController(),
              onChanged: (value) => changedText = value,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextField), 'test');
      expect(changedText, 'test');
    });

    testWidgets('supports multiple lines', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SanaTextField(
              label: 'Notes',
              controller: TextEditingController(),
              maxLines: 5,
            ),
          ),
        ),
      );

      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.maxLines, 5);
    });

    testWidgets('validates input', (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Form(
              key: formKey,
              child: SanaTextField(
                label: 'Email',
                controller: TextEditingController(),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Required field';
                  }
                  return null;
                },
              ),
            ),
          ),
        ),
      );

      formKey.currentState!.validate();
      await tester.pump();

      expect(find.text('Required field'), findsOneWidget);
    });
  });
}
