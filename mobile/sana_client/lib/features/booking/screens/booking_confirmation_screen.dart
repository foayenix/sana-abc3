import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';

class BookingConfirmationScreen extends StatelessWidget {
  const BookingConfirmationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(SanaSpacing.lg),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: SanaColors.successLight,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.check_circle,
                  size: 80,
                  color: SanaColors.success,
                ),
              ),
              const SizedBox(height: SanaSpacing.xl),
              Text(
                'Booking Confirmed!',
                style: SanaTextStyles.heading1,
              ),
              const SizedBox(height: SanaSpacing.md),
              Text(
                'Your appointment has been scheduled successfully.',
                style: SanaTextStyles.body.copyWith(
                  color: SanaColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: SanaSpacing.xl),
              Container(
                padding: const EdgeInsets.all(SanaSpacing.lg),
                decoration: BoxDecoration(
                  color: SanaColors.surface,
                  borderRadius: BorderRadius.circular(SanaBorderRadius.lg),
                  border: Border.all(color: SanaColors.grey200),
                ),
                child: Column(
                  children: [
                    _InfoRow(label: 'Practitioner', value: 'Dr. Emily Chen'),
                    const Divider(height: 24),
                    _InfoRow(label: 'Service', value: 'Follow-up Session'),
                    const Divider(height: 24),
                    _InfoRow(label: 'Date', value: 'Nov 24, 2024'),
                    const Divider(height: 24),
                    _InfoRow(label: 'Time', value: '2:00 PM'),
                    const Divider(height: 24),
                    _InfoRow(label: 'Duration', value: '60 minutes'),
                  ],
                ),
              ),
              const SizedBox(height: SanaSpacing.xl),
              SanaButton(
                text: 'View My Sessions',
                onPressed: () => context.go(AppRoutes.sessions),
              ),
              const SizedBox(height: SanaSpacing.md),
              SanaButton(
                text: 'Back to Home',
                variant: SanaButtonVariant.outline,
                onPressed: () => context.go(AppRoutes.home),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: SanaTextStyles.bodySmall),
        Text(
          value,
          style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}
