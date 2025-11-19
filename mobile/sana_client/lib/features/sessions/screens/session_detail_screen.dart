import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';

class SessionDetailScreen extends StatelessWidget {
  final String sessionId;

  const SessionDetailScreen({super.key, required this.sessionId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Session Details'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Practitioner Info
            SanaCard(
              child: Row(
                children: [
                  const SanaAvatar(
                    name: 'Dr. Emily Chen',
                    size: SanaAvatarSize.lg,
                  ),
                  const SizedBox(width: SanaSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Dr. Emily Chen',
                          style: SanaTextStyles.body.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'Licensed Acupuncturist',
                          style: SanaTextStyles.bodySmall,
                        ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () => context.push('/messages/1'),
                    child: Text('Message', style: SanaTextStyles.link),
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Session Info
            Text('Session Information', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              child: Column(
                children: [
                  _DetailRow(icon: Icons.medical_services, label: 'Service', value: 'Acupuncture Session'),
                  const Divider(height: 24),
                  _DetailRow(icon: Icons.calendar_today, label: 'Date', value: 'Nov 24, 2024'),
                  const Divider(height: 24),
                  _DetailRow(icon: Icons.access_time, label: 'Time', value: '2:00 PM - 3:00 PM'),
                  const Divider(height: 24),
                  _DetailRow(icon: Icons.location_on, label: 'Location', value: '123 Wellness St, SF'),
                  const Divider(height: 24),
                  _DetailRow(icon: Icons.payments, label: 'Fee', value: '\$100'),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Notes
            Text('Session Notes', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              child: Text(
                'Focus on lower back pain. Patient reported improvement after last session. Continue with same treatment protocol.',
                style: SanaTextStyles.body.copyWith(height: 1.6),
              ),
            ),

            const SizedBox(height: SanaSpacing.xxl),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        decoration: BoxDecoration(
          color: SanaColors.surface,
          boxShadow: [
            BoxShadow(
              color: SanaColors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          child: Row(
            children: [
              Expanded(
                child: SanaButton(
                  text: 'Reschedule',
                  variant: SanaButtonVariant.outline,
                  onPressed: () {},
                ),
              ),
              const SizedBox(width: SanaSpacing.md),
              Expanded(
                child: SanaButton(
                  text: 'Cancel',
                  variant: SanaButtonVariant.secondary,
                  onPressed: () {},
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20, color: SanaColors.primaryDark),
        const SizedBox(width: SanaSpacing.md),
        Text(label, style: SanaTextStyles.bodySmall),
        const Spacer(),
        Text(
          value,
          style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w500),
        ),
      ],
    );
  }
}
