import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/health_score_widget.dart';

class HealthScreen extends StatelessWidget {
  const HealthScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.all(SanaSpacing.lg),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Health Tracking',
                      style: SanaTextStyles.heading2,
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.settings_outlined),
                    ),
                  ],
                ),
              ),

              // Health Score
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                child: SanaCard(
                  child: Column(
                    children: [
                      const HealthScoreWidget(score: 78, size: 140),
                      const SizedBox(height: SanaSpacing.md),
                      Text(
                        'Your health score improved by 5 points this month',
                        style: SanaTextStyles.bodySmall.copyWith(
                          color: SanaColors.success,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Quick Stats
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                child: Row(
                  children: [
                    Expanded(
                      child: _StatCard(
                        icon: Icons.nightlight_round,
                        label: 'Sleep',
                        value: '7.2h',
                        change: '+8%',
                        isPositive: true,
                      ),
                    ),
                    const SizedBox(width: SanaSpacing.sm),
                    Expanded(
                      child: _StatCard(
                        icon: Icons.directions_walk,
                        label: 'Steps',
                        value: '8,432',
                        change: '-3%',
                        isPositive: false,
                      ),
                    ),
                    const SizedBox(width: SanaSpacing.sm),
                    Expanded(
                      child: _StatCard(
                        icon: Icons.favorite,
                        label: 'HRV',
                        value: '45ms',
                        change: '+12%',
                        isPositive: true,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Journal Entry
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                child: SanaCard(
                  onTap: () => context.push(AppRoutes.journal),
                  child: Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: SanaColors.accentLight,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.edit_note,
                          color: SanaColors.primaryDark,
                        ),
                      ),
                      const SizedBox(width: SanaSpacing.md),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'How are you feeling today?',
                              style: SanaTextStyles.body.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            Text(
                              'Log your mood, energy, and symptoms',
                              style: SanaTextStyles.caption,
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.chevron_right,
                        color: SanaColors.textTertiary,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Health Metrics
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                child: Text(
                  'Health Metrics',
                  style: SanaTextStyles.heading3,
                ),
              ),
              const SizedBox(height: SanaSpacing.md),

              _MetricItem(
                icon: Icons.sentiment_satisfied_alt,
                label: 'Mood',
                value: 'Good',
                trend: 'Stable this week',
                color: SanaColors.success,
              ),
              _MetricItem(
                icon: Icons.bolt,
                label: 'Energy',
                value: '7/10',
                trend: 'Up from yesterday',
                color: SanaColors.accent,
              ),
              _MetricItem(
                icon: Icons.psychology,
                label: 'Stress',
                value: 'Low',
                trend: 'Improved 15%',
                color: SanaColors.info,
              ),
              _MetricItem(
                icon: Icons.local_fire_department,
                label: 'Pain Level',
                value: '2/10',
                trend: 'Down from 4/10',
                color: SanaColors.primaryMedium,
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Connected Devices
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Connected Devices',
                      style: SanaTextStyles.heading3,
                    ),
                    TextButton(
                      onPressed: () {},
                      child: Text(
                        'Manage',
                        style: SanaTextStyles.link,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: SanaSpacing.sm),

              Padding(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                child: SanaCard(
                  child: Column(
                    children: [
                      _DeviceItem(
                        icon: Icons.watch,
                        name: 'Apple Watch',
                        status: 'Connected',
                        lastSync: '2 min ago',
                        isConnected: true,
                      ),
                      const Divider(),
                      _DeviceItem(
                        icon: Icons.phone_iphone,
                        name: 'Apple Health',
                        status: 'Connected',
                        lastSync: '5 min ago',
                        isConnected: true,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: SanaSpacing.xl),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final String change;
  final bool isPositive;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.change,
    required this.isPositive,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      padding: const EdgeInsets.all(SanaSpacing.sm),
      child: Column(
        children: [
          Icon(icon, size: 20, color: SanaColors.primaryDark),
          const SizedBox(height: 4),
          Text(
            value,
            style: SanaTextStyles.body.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          Text(
            label,
            style: SanaTextStyles.caption,
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                isPositive ? Icons.arrow_upward : Icons.arrow_downward,
                size: 10,
                color: isPositive ? SanaColors.success : SanaColors.error,
              ),
              Text(
                change,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: isPositive ? SanaColors.success : SanaColors.error,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetricItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final String trend;
  final Color color;

  const _MetricItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.trend,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: SanaSpacing.lg,
        vertical: SanaSpacing.xs,
      ),
      child: SanaCard(
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: SanaSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: SanaTextStyles.bodySmall,
                  ),
                  Text(
                    value,
                    style: SanaTextStyles.body.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              trend,
              style: SanaTextStyles.caption.copyWith(
                color: SanaColors.success,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DeviceItem extends StatelessWidget {
  final IconData icon;
  final String name;
  final String status;
  final String lastSync;
  final bool isConnected;

  const _DeviceItem({
    required this.icon,
    required this.name,
    required this.status,
    required this.lastSync,
    required this.isConnected,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SanaSpacing.sm),
      child: Row(
        children: [
          Icon(icon, color: SanaColors.textSecondary),
          const SizedBox(width: SanaSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: SanaTextStyles.body.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  'Last sync: $lastSync',
                  style: SanaTextStyles.caption,
                ),
              ],
            ),
          ),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: isConnected ? SanaColors.success : SanaColors.grey400,
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }
}
