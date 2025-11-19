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
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SanaCard(
              child: Row(
                children: [
                  const SanaAvatar(name: 'Sarah Johnson', size: SanaAvatarSize.lg),
                  const SizedBox(width: SanaSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Sarah Johnson', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                        Text('sarah.johnson@email.com', style: SanaTextStyles.caption),
                      ],
                    ),
                  ),
                  IconButton(icon: const Icon(Icons.chat_bubble_outline), onPressed: () {}),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.lg),
            Text('Session Info', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              child: Column(
                children: [
                  _InfoRow(icon: Icons.medical_services, label: 'Service', value: 'Acupuncture Session'),
                  const Divider(),
                  _InfoRow(icon: Icons.calendar_today, label: 'Date', value: 'Nov 22, 2024'),
                  const Divider(),
                  _InfoRow(icon: Icons.access_time, label: 'Time', value: '9:00 AM - 10:00 AM'),
                  const Divider(),
                  _InfoRow(icon: Icons.payments, label: 'Fee', value: '\$100'),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.lg),
            Text('Notes', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              child: TextField(
                maxLines: 4,
                decoration: const InputDecoration(hintText: 'Add session notes...', border: InputBorder.none),
              ),
            ),
            const SizedBox(height: SanaSpacing.lg),
            SanaButton(text: 'Save Notes', onPressed: () {}),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon; final String label; final String value;
  const _InfoRow({required this.icon, required this.label, required this.value});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SanaSpacing.sm),
      child: Row(children: [
        Icon(icon, size: 20, color: SanaColors.primaryDark),
        const SizedBox(width: SanaSpacing.md),
        Text(label, style: SanaTextStyles.bodySmall),
        const Spacer(),
        Text(value, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w500)),
      ]),
    );
  }
}
