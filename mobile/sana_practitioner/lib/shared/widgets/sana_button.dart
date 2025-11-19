import 'package:flutter/material.dart';
import '../../config/colors.dart';
import '../../config/theme.dart';

enum SanaButtonVariant { primary, secondary, outline, text, accent }

enum SanaButtonSize { small, medium, large }

class SanaButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final SanaButtonVariant variant;
  final SanaButtonSize size;
  final bool isLoading;
  final bool isFullWidth;
  final IconData? icon;
  final IconData? trailingIcon;

  const SanaButton({
    super.key,
    required this.text,
    this.onPressed,
    this.variant = SanaButtonVariant.primary,
    this.size = SanaButtonSize.medium,
    this.isLoading = false,
    this.isFullWidth = true,
    this.icon,
    this.trailingIcon,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: _getHeight(),
      child: _buildButton(),
    );
  }

  double _getHeight() {
    switch (size) {
      case SanaButtonSize.small:
        return 40;
      case SanaButtonSize.medium:
        return 52;
      case SanaButtonSize.large:
        return 60;
    }
  }

  double _getFontSize() {
    switch (size) {
      case SanaButtonSize.small:
        return 14;
      case SanaButtonSize.medium:
        return 16;
      case SanaButtonSize.large:
        return 18;
    }
  }

  Widget _buildButton() {
    switch (variant) {
      case SanaButtonVariant.primary:
        return _PrimaryButton(
          text: text,
          onPressed: onPressed,
          isLoading: isLoading,
          fontSize: _getFontSize(),
          icon: icon,
          trailingIcon: trailingIcon,
        );
      case SanaButtonVariant.secondary:
        return _SecondaryButton(
          text: text,
          onPressed: onPressed,
          isLoading: isLoading,
          fontSize: _getFontSize(),
          icon: icon,
          trailingIcon: trailingIcon,
        );
      case SanaButtonVariant.outline:
        return _OutlineButton(
          text: text,
          onPressed: onPressed,
          isLoading: isLoading,
          fontSize: _getFontSize(),
          icon: icon,
          trailingIcon: trailingIcon,
        );
      case SanaButtonVariant.text:
        return _TextButton(
          text: text,
          onPressed: onPressed,
          isLoading: isLoading,
          fontSize: _getFontSize(),
          icon: icon,
          trailingIcon: trailingIcon,
        );
      case SanaButtonVariant.accent:
        return _AccentButton(
          text: text,
          onPressed: onPressed,
          isLoading: isLoading,
          fontSize: _getFontSize(),
          icon: icon,
          trailingIcon: trailingIcon,
        );
    }
  }
}

class _PrimaryButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final double fontSize;
  final IconData? icon;
  final IconData? trailingIcon;

  const _PrimaryButton({
    required this.text,
    this.onPressed,
    required this.isLoading,
    required this.fontSize,
    this.icon,
    this.trailingIcon,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: SanaColors.primaryDark,
        foregroundColor: SanaColors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SanaBorderRadius.md),
        ),
      ),
      child: _buildContent(),
    );
  }

  Widget _buildContent() {
    if (isLoading) {
      return const SizedBox(
        width: 24,
        height: 24,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(SanaColors.white),
        ),
      );
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (icon != null) ...[
          Icon(icon, size: fontSize + 4),
          const SizedBox(width: 8),
        ],
        Text(
          text,
          style: TextStyle(
            fontSize: fontSize,
            fontWeight: FontWeight.w600,
          ),
        ),
        if (trailingIcon != null) ...[
          const SizedBox(width: 8),
          Icon(trailingIcon, size: fontSize + 4),
        ],
      ],
    );
  }
}

class _SecondaryButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final double fontSize;
  final IconData? icon;
  final IconData? trailingIcon;

  const _SecondaryButton({
    required this.text,
    this.onPressed,
    required this.isLoading,
    required this.fontSize,
    this.icon,
    this.trailingIcon,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: SanaColors.primaryLightest,
        foregroundColor: SanaColors.primaryDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SanaBorderRadius.md),
        ),
      ),
      child: isLoading
          ? const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(SanaColors.primaryDark),
              ),
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: fontSize + 4),
                  const SizedBox(width: 8),
                ],
                Text(
                  text,
                  style: TextStyle(
                    fontSize: fontSize,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (trailingIcon != null) ...[
                  const SizedBox(width: 8),
                  Icon(trailingIcon, size: fontSize + 4),
                ],
              ],
            ),
    );
  }
}

class _OutlineButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final double fontSize;
  final IconData? icon;
  final IconData? trailingIcon;

  const _OutlineButton({
    required this.text,
    this.onPressed,
    required this.isLoading,
    required this.fontSize,
    this.icon,
    this.trailingIcon,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: isLoading ? null : onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: SanaColors.primaryDark,
        side: const BorderSide(color: SanaColors.primaryDark, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SanaBorderRadius.md),
        ),
      ),
      child: isLoading
          ? const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(SanaColors.primaryDark),
              ),
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: fontSize + 4),
                  const SizedBox(width: 8),
                ],
                Text(
                  text,
                  style: TextStyle(
                    fontSize: fontSize,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (trailingIcon != null) ...[
                  const SizedBox(width: 8),
                  Icon(trailingIcon, size: fontSize + 4),
                ],
              ],
            ),
    );
  }
}

class _TextButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final double fontSize;
  final IconData? icon;
  final IconData? trailingIcon;

  const _TextButton({
    required this.text,
    this.onPressed,
    required this.isLoading,
    required this.fontSize,
    this.icon,
    this.trailingIcon,
  });

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: isLoading ? null : onPressed,
      child: isLoading
          ? const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(SanaColors.primaryDark),
              ),
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: fontSize + 4),
                  const SizedBox(width: 8),
                ],
                Text(
                  text,
                  style: TextStyle(
                    fontSize: fontSize,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (trailingIcon != null) ...[
                  const SizedBox(width: 8),
                  Icon(trailingIcon, size: fontSize + 4),
                ],
              ],
            ),
    );
  }
}

class _AccentButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final double fontSize;
  final IconData? icon;
  final IconData? trailingIcon;

  const _AccentButton({
    required this.text,
    this.onPressed,
    required this.isLoading,
    required this.fontSize,
    this.icon,
    this.trailingIcon,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: SanaColors.accent,
        foregroundColor: SanaColors.primaryDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SanaBorderRadius.md),
        ),
      ),
      child: isLoading
          ? const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(SanaColors.primaryDark),
              ),
            )
          : Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: fontSize + 4),
                  const SizedBox(width: 8),
                ],
                Text(
                  text,
                  style: TextStyle(
                    fontSize: fontSize,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (trailingIcon != null) ...[
                  const SizedBox(width: 8),
                  Icon(trailingIcon, size: fontSize + 4),
                ],
              ],
            ),
    );
  }
}
