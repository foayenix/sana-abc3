import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/health_score_widget.dart';

class ClientDetailScreen extends StatelessWidget {
  final String clientId;
  const ClientDetailScreen({super.key, required this.clientId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Client Details'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        actions: [IconButton(icon: const Icon(Icons.more_vert), onPressed: () {})],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          children: [
            const SanaAvatar(name: 'Sarah Johnson', size: SanaAvatarSize.xxl),
            const SizedBox(height: SanaSpacing.md),
            Text('Sarah Johnson', style: SanaTextStyles.heading2),
            Text('sarah.johnson@email.com', style: SanaTextStyles.bodySmall),
            const SizedBox(height: SanaSpacing.lg),
            Row(
              children: [
                Expanded(child: _StatCard(label: 'Sessions', value: '12')),
                const SizedBox(width: SanaSpacing.sm),
                Expanded(child: _StatCard(label: 'Since', value: 'Mar 2024')),
              ],
            ),
            const SizedBox(height: SanaSpacing.lg),
            Text('Health Progress', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            const SanaCard(child: HealthScoreBar(score: 78)),
            const SizedBox(height: SanaSpacing.lg),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Session History', style: SanaTextStyles.heading3),
                TextButton(onPressed: () {}, child: Text('View All', style: SanaTextStyles.link)),
              ],
            ),
            const SizedBox(height: SanaSpacing.sm),
            ...List.generate(3, (i) => Padding(
              padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
              child: SanaCard(
                child: Row(
                  children: [
                    Container(
                      width: 48, height: 48,
                      decoration: BoxDecoration(color: SanaColors.primaryLightest, borderRadius: BorderRadius.circular(12)),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text('${22 - i}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: SanaColors.primaryDark)),
                          const Text('Nov', style: TextStyle(fontSize: 10, color: SanaColors.primaryDark)),
                        ],
                      ),
                    ),
                    const SizedBox(width: SanaSpacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(['Acupuncture', 'Follow-up', 'Initial Consultation'][i], style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w500)),
                          Text('${['60', '60', '90'][i]} min', style: SanaTextStyles.caption),
                        ],
                      ),
                    ),
                    Text('\$${[100, 100, 150][i]}', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label; final String value;
  const _StatCard({required this.label, required this.value});
  @override
  Widget build(BuildContext context) {
    return SanaCard(child: Column(children: [Text(value, style: SanaTextStyles.heading3), Text(label, style: SanaTextStyles.caption)]));
  }
}
