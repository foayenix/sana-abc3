import 'package:flutter/material.dart';
import '../../config/colors.dart';
import '../../config/theme.dart';

class SanaCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final VoidCallback? onTap;
  final Color? backgroundColor;
  final bool hasShadow;
  final bool hasBorder;

  const SanaCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.backgroundColor,
    this.hasShadow = false,
    this.hasBorder = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      decoration: BoxDecoration(
        color: backgroundColor ?? SanaColors.surface,
        borderRadius: BorderRadius.circular(SanaBorderRadius.lg),
        border: hasBorder
            ? Border.all(color: SanaColors.grey200, width: 1)
            : null,
        boxShadow: hasShadow
            ? [
                BoxShadow(
                  color: SanaColors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(SanaBorderRadius.lg),
          child: Padding(
            padding: padding ?? const EdgeInsets.all(SanaSpacing.md),
            child: child,
          ),
        ),
      ),
    );
  }
}

class SanaGradientCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final VoidCallback? onTap;
  final Gradient gradient;

  const SanaGradientCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.gradient = SanaColors.primaryGradient,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(SanaBorderRadius.lg),
        boxShadow: [
          BoxShadow(
            color: SanaColors.primaryDark.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(SanaBorderRadius.lg),
          child: Padding(
            padding: padding ?? const EdgeInsets.all(SanaSpacing.lg),
            child: child,
          ),
        ),
      ),
    );
  }
}

class SanaInfoCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Color? iconColor;
  final Color? backgroundColor;
  final VoidCallback? onTap;
  final Widget? trailing;

  const SanaInfoCard({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.iconColor,
    this.backgroundColor,
    this.onTap,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      onTap: onTap,
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: backgroundColor ?? SanaColors.primaryLightest,
              borderRadius: BorderRadius.circular(SanaBorderRadius.md),
            ),
            child: Icon(
              icon,
              color: iconColor ?? SanaColors.primaryDark,
              size: 24,
            ),
          ),
          const SizedBox(width: SanaSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: SanaTextStyles.body.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    subtitle!,
                    style: SanaTextStyles.bodySmall,
                  ),
                ],
              ],
            ),
          ),
          if (trailing != null) trailing!,
          if (onTap != null && trailing == null)
            const Icon(
              Icons.chevron_right,
              color: SanaColors.textTertiary,
            ),
        ],
      ),
    );
  }
}

class SanaStatCard extends StatelessWidget {
  final String label;
  final String value;
  final String? change;
  final bool isPositive;
  final IconData? icon;
  final Color? color;

  const SanaStatCard({
    super.key,
    required this.label,
    required this.value,
    this.change,
    this.isPositive = true,
    this.icon,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(
                  icon,
                  size: 16,
                  color: color ?? SanaColors.textTertiary,
                ),
                const SizedBox(width: 4),
              ],
              Text(
                label,
                style: SanaTextStyles.caption.copyWith(
                  color: SanaColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: SanaTextStyles.heading2.copyWith(
              color: color ?? SanaColors.textPrimary,
            ),
          ),
          if (change != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(
                  isPositive ? Icons.arrow_upward : Icons.arrow_downward,
                  size: 14,
                  color: isPositive ? SanaColors.success : SanaColors.error,
                ),
                const SizedBox(width: 2),
                Text(
                  change!,
                  style: SanaTextStyles.caption.copyWith(
                    color: isPositive ? SanaColors.success : SanaColors.error,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
