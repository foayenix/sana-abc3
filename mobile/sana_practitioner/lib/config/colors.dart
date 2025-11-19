import 'package:flutter/material.dart';

class SanaColors {
  SanaColors._();

  // Brand Colors
  static const Color primaryDark = Color(0xFF345519);
  static const Color primaryMedium = Color(0xFF58AA55);
  static const Color primaryLight = Color(0xFFA5BE5E);
  static const Color accent = Color(0xFFF2DF76);
  static const Color white = Color(0xFFFFFFFF);

  // Extended Palette
  static const Color primaryLightest = Color(0xFFE8F5E9);
  static const Color primarySurface = Color(0xFFF1F8E9);
  static const Color accentLight = Color(0xFFFFF9E6);

  // Neutral Colors
  static const Color black = Color(0xFF1A1A1A);
  static const Color grey900 = Color(0xFF212121);
  static const Color grey800 = Color(0xFF424242);
  static const Color grey700 = Color(0xFF616161);
  static const Color grey600 = Color(0xFF757575);
  static const Color grey500 = Color(0xFF9E9E9E);
  static const Color grey400 = Color(0xFFBDBDBD);
  static const Color grey300 = Color(0xFFE0E0E0);
  static const Color grey200 = Color(0xFFEEEEEE);
  static const Color grey100 = Color(0xFFF5F5F5);
  static const Color grey50 = Color(0xFFFAFAFA);

  // Semantic Colors
  static const Color success = Color(0xFF4CAF50);
  static const Color successLight = Color(0xFFE8F5E9);
  static const Color warning = Color(0xFFFFA726);
  static const Color warningLight = Color(0xFFFFF3E0);
  static const Color error = Color(0xFFEF5350);
  static const Color errorLight = Color(0xFFFFEBEE);
  static const Color info = Color(0xFF29B6F6);
  static const Color infoLight = Color(0xFFE1F5FE);

  // Background Colors
  static const Color background = Color(0xFFFAFAFA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color card = Color(0xFFFFFFFF);

  // Text Colors
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF616161);
  static const Color textTertiary = Color(0xFF9E9E9E);
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  static const Color textOnAccent = Color(0xFF345519);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryDark, primaryMedium],
  );

  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accent, primaryLight],
  );

  static const LinearGradient surfaceGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [primaryLightest, white],
  );

  // Health Score Colors
  static const Color healthExcellent = Color(0xFF4CAF50);
  static const Color healthGood = Color(0xFF8BC34A);
  static const Color healthModerate = Color(0xFFFFC107);
  static const Color healthFair = Color(0xFFFF9800);
  static const Color healthPoor = Color(0xFFF44336);

  static Color getHealthColor(int score) {
    if (score >= 80) return healthExcellent;
    if (score >= 60) return healthGood;
    if (score >= 40) return healthModerate;
    if (score >= 20) return healthFair;
    return healthPoor;
  }
}
