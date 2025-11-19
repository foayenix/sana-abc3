import 'package:flutter/material.dart';

/// SANA Brand Colors
class SanaColors {
  // Primary brand colors
  static const Color primaryDark = Color(0xFF345519);
  static const Color primaryMedium = Color(0xFF58AA55);
  static const Color primaryLight = Color(0xFFA5BE5E);
  static const Color primaryLightest = Color(0xFFE8F5E9);
  static const Color accent = Color(0xFFF2DF76);
  static const Color white = Color(0xFFFFFFFF);

  // Neutral colors
  static const Color background = Color(0xFFF5F5F5);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color grey100 = Color(0xFFF5F5F5);
  static const Color grey200 = Color(0xFFEEEEEE);
  static const Color grey300 = Color(0xFFE0E0E0);
  static const Color grey400 = Color(0xFFBDBDBD);
  static const Color grey500 = Color(0xFF9E9E9E);
  static const Color grey600 = Color(0xFF757575);

  // Text colors
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color textTertiary = Color(0xFF9E9E9E);

  // Semantic colors
  static const Color success = Color(0xFF4CAF50);
  static const Color successLight = Color(0xFFE8F5E9);
  static const Color warning = Color(0xFFFF9800);
  static const Color warningLight = Color(0xFFFFF3E0);
  static const Color error = Color(0xFFF44336);
  static const Color errorLight = Color(0xFFFFEBEE);
  static const Color info = Color(0xFF2196F3);
  static const Color infoLight = Color(0xFFE3F2FD);

  // Health score colors
  static const Color healthExcellent = Color(0xFF4CAF50);
  static const Color healthGood = Color(0xFF8BC34A);
  static const Color healthModerate = Color(0xFFFFC107);
  static const Color healthFair = Color(0xFFFF9800);
  static const Color healthPoor = Color(0xFFF44336);

  // Gradient
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryDark, primaryMedium],
  );

  /// Get health color based on score
  static Color getHealthColor(int score) {
    if (score >= 80) return healthExcellent;
    if (score >= 60) return healthGood;
    if (score >= 40) return healthModerate;
    if (score >= 20) return healthFair;
    return healthPoor;
  }
}
