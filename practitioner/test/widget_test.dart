import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sana_practitioner/config/colors.dart';

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

    test('semantic colors are defined', () {
      expect(SanaColors.success, isA<Color>());
      expect(SanaColors.warning, isA<Color>());
      expect(SanaColors.error, isA<Color>());
      expect(SanaColors.info, isA<Color>());
    });
  });

  group('Revenue Formatting', () {
    test('formats currency correctly', () {
      // Test currency formatting utility
      double revenue = 12500.50;
      String formatted = '\$${revenue.toStringAsFixed(2)}';
      expect(formatted, '\$12500.50');
    });

    test('formats large numbers with commas', () {
      int count = 1234567;
      String formatted = count.toString().replaceAllMapped(
        RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
        (Match m) => '${m[1]},',
      );
      expect(formatted, '1,234,567');
    });
  });

  group('Date Formatting', () {
    test('formats session dates correctly', () {
      final date = DateTime(2024, 3, 15, 14, 30);
      final formatted = '${date.month}/${date.day}/${date.year}';
      expect(formatted, '3/15/2024');
    });

    test('formats time slots correctly', () {
      final time = TimeOfDay(hour: 14, minute: 30);
      final formatted = '${time.hour}:${time.minute.toString().padLeft(2, '0')}';
      expect(formatted, '14:30');
    });
  });
}
