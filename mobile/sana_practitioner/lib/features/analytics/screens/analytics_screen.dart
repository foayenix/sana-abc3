import 'package:flutter/material.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_card.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  String _period = 'This Month';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(SanaSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Analytics', style: SanaTextStyles.heading2),
                  DropdownButton<String>(
                    value: _period,
                    underline: const SizedBox(),
                    items: ['This Week', 'This Month', 'This Year']
                        .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                        .toList(),
                    onChanged: (value) => setState(() => _period = value!),
                  ),
                ],
              ),
              const SizedBox(height: SanaSpacing.lg),

              // Key Metrics
              Row(
                children: [
                  Expanded(child: _MetricCard(label: 'Revenue', value: '\$4,280', change: '+12%', isPositive: true)),
                  const SizedBox(width: SanaSpacing.sm),
                  Expanded(child: _MetricCard(label: 'Sessions', value: '32', change: '+8%', isPositive: true)),
                ],
              ),
              const SizedBox(height: SanaSpacing.sm),
              Row(
                children: [
                  Expanded(child: _MetricCard(label: 'New Clients', value: '6', change: '+20%', isPositive: true)),
                  const SizedBox(width: SanaSpacing.sm),
                  Expanded(child: _MetricCard(label: 'Retention', value: '94%', change: '+2%', isPositive: true)),
                ],
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Outcome Score
              Text('Outcome Performance', style: SanaTextStyles.heading3),
              const SizedBox(height: SanaSpacing.md),
              SanaCard(
                child: Column(
                  children: [
                    _OutcomeBar(label: 'Pain Reduction', value: 94, color: SanaColors.success),
                    const SizedBox(height: SanaSpacing.md),
                    _OutcomeBar(label: 'Stress Relief', value: 89, color: SanaColors.primaryMedium),
                    const SizedBox(height: SanaSpacing.md),
                    _OutcomeBar(label: 'Sleep Quality', value: 85, color: SanaColors.info),
                    const SizedBox(height: SanaSpacing.md),
                    _OutcomeBar(label: 'Overall Satisfaction', value: 92, color: SanaColors.accent),
                  ],
                ),
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Top Services
              Text('Top Services', style: SanaTextStyles.heading3),
              const SizedBox(height: SanaSpacing.md),
              SanaCard(
                child: Column(
                  children: [
                    _ServiceRow(name: 'Follow-up Session', count: 18, revenue: '\$1,800'),
                    const Divider(),
                    _ServiceRow(name: 'Initial Consultation', count: 8, revenue: '\$1,200'),
                    const Divider(),
                    _ServiceRow(name: 'Cupping Therapy', count: 6, revenue: '\$480'),
                  ],
                ),
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Reviews Summary
              Text('Recent Reviews', style: SanaTextStyles.heading3),
              const SizedBox(height: SanaSpacing.md),
              SanaCard(
                child: Column(
                  children: [
                    Row(
                      children: [
                        const Text('4.9', style: TextStyle(fontSize: 48, fontWeight: FontWeight.w700, color: SanaColors.primaryDark)),
                        const SizedBox(width: SanaSpacing.md),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(children: List.generate(5, (i) => const Icon(Icons.star, color: SanaColors.accent, size: 20))),
                              const SizedBox(height: 4),
                              Text('Based on 124 reviews', style: SanaTextStyles.caption),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: SanaSpacing.md),
                    _RatingBar(stars: 5, count: 108, total: 124),
                    _RatingBar(stars: 4, count: 12, total: 124),
                    _RatingBar(stars: 3, count: 3, total: 124),
                    _RatingBar(stars: 2, count: 1, total: 124),
                    _RatingBar(stars: 1, count: 0, total: 124),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final String change;
  final bool isPositive;

  const _MetricCard({required this.label, required this.value, required this.change, required this.isPositive});

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: SanaTextStyles.caption),
          const SizedBox(height: 4),
          Text(value, style: SanaTextStyles.heading2),
          const SizedBox(height: 4),
          Row(
            children: [
              Icon(isPositive ? Icons.arrow_upward : Icons.arrow_downward, size: 12, color: isPositive ? SanaColors.success : SanaColors.error),
              Text(change, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: isPositive ? SanaColors.success : SanaColors.error)),
            ],
          ),
        ],
      ),
    );
  }
}

class _OutcomeBar extends StatelessWidget {
  final String label;
  final int value;
  final Color color;

  const _OutcomeBar({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: SanaTextStyles.bodySmall),
            Text('$value%', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(value: value / 100, backgroundColor: SanaColors.grey200, valueColor: AlwaysStoppedAnimation(color), minHeight: 8),
        ),
      ],
    );
  }
}

class _ServiceRow extends StatelessWidget {
  final String name;
  final int count;
  final String revenue;

  const _ServiceRow({required this.name, required this.count, required this.revenue});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SanaSpacing.sm),
      child: Row(
        children: [
          Expanded(child: Text(name, style: SanaTextStyles.body)),
          Text('$count', style: SanaTextStyles.bodySmall),
          const SizedBox(width: SanaSpacing.lg),
          Text(revenue, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _RatingBar extends StatelessWidget {
  final int stars;
  final int count;
  final int total;

  const _RatingBar({required this.stars, required this.count, required this.total});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text('$stars', style: SanaTextStyles.caption),
          const Icon(Icons.star, size: 12, color: SanaColors.accent),
          const SizedBox(width: 8),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(2),
              child: LinearProgressIndicator(
                value: total > 0 ? count / total : 0,
                backgroundColor: SanaColors.grey200,
                valueColor: const AlwaysStoppedAnimation(SanaColors.accent),
                minHeight: 6,
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(width: 30, child: Text('$count', style: SanaTextStyles.caption)),
        ],
      ),
    );
  }
}
