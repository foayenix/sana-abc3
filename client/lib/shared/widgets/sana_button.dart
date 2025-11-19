import 'package:flutter/material.dart';
import '../../config/colors.dart';
import '../../config/theme.dart';

enum SanaButtonVariant { filled, outline, text }

/// Custom SANA button widget
class SanaButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final SanaButtonVariant variant;
  final IconData? icon;
  final double? width;

  const SanaButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.variant = SanaButtonVariant.filled,
    this.icon,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    final Widget child = isLoading
        ? const SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(SanaColors.white),
            ),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 20),
                const SizedBox(width: 8),
              ],
              Text(text),
            ],
          );

    Widget button;
    switch (variant) {
      case SanaButtonVariant.filled:
        button = ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          child: child,
        );
        break;
      case SanaButtonVariant.outline:
        button = OutlinedButton(
          onPressed: isLoading ? null : onPressed,
          child: child,
        );
        break;
      case SanaButtonVariant.text:
        button = TextButton(
          onPressed: isLoading ? null : onPressed,
          child: child,
        );
        break;
    }

    if (width != null) {
      return SizedBox(width: width, child: button);
    }
    return SizedBox(width: double.infinity, child: button);
  }
}
