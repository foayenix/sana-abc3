import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context),
              _buildRevenueCard(context),
              _buildQuickStats(context),
              _buildTodaysSessions(context),
              _buildRecentClients(context),
              const SizedBox(height: SanaSpacing.lg),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(SanaSpacing.lg),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Good Morning',
                  style: SanaTextStyles.bodySmall.copyWith(
                    color: SanaColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 4),
                Text('Dr. Emily', style: SanaTextStyles.heading2),
              ],
            ),
          ),
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.notifications_outlined, size: 28),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: () => context.push(AppRoutes.profile),
            child: const SanaAvatar(
              name: 'Dr. Emily Chen',
              size: SanaAvatarSize.md,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRevenueCard(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
      child: SanaGradientCard(
        onTap: () => context.push(AppRoutes.earnings),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'This Month',
                  style: TextStyle(
                    fontSize: 14,
                    color: SanaColors.white,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: SanaColors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.arrow_upward, size: 12, color: SanaColors.accent),
                      SizedBox(width: 4),
                      Text(
                        '12%',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: SanaColors.accent,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              '\$4,280',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.w700,
                color: SanaColors.white,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '32 sessions completed',
              style: TextStyle(
                fontSize: 14,
                color: SanaColors.white.withOpacity(0.8),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Text(
                  'View Earnings',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: SanaColors.accent,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(Icons.arrow_forward, size: 16, color: SanaColors.accent),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(SanaSpacing.lg),
      child: Row(
        children: [
          Expanded(
            child: _StatCard(
              icon: Icons.people,
              label: 'Active Clients',
              value: '48',
              color: SanaColors.primaryMedium,
            ),
          ),
          const SizedBox(width: SanaSpacing.sm),
          Expanded(
            child: _StatCard(
              icon: Icons.star,
              label: 'Rating',
              value: '4.9',
              color: SanaColors.accent,
            ),
          ),
          const SizedBox(width: SanaSpacing.sm),
          Expanded(
            child: _StatCard(
              icon: Icons.trending_up,
              label: 'Outcomes',
              value: '92%',
              color: SanaColors.success,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTodaysSessions(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("Today's Sessions", style: SanaTextStyles.heading3),
              TextButton(
                onPressed: () => context.go(AppRoutes.calendar),
                child: Text('View All', style: SanaTextStyles.link),
              ),
            ],
          ),
          const SizedBox(height: SanaSpacing.sm),
          _SessionItem(
            clientName: 'Sarah Johnson',
            time: '9:00 AM - 10:00 AM',
            service: 'Acupuncture',
            status: 'Upcoming',
          ),
          const SizedBox(height: SanaSpacing.sm),
          _SessionItem(
            clientName: 'Michael Brown',
            time: '11:00 AM - 12:00 PM',
            service: 'Follow-up',
            status: 'Upcoming',
          ),
          const SizedBox(height: SanaSpacing.sm),
          _SessionItem(
            clientName: 'Lisa Wang',
            time: '2:00 PM - 3:00 PM',
            service: 'Initial Consultation',
            status: 'Upcoming',
          ),
        ],
      ),
    );
  }

  Widget _buildRecentClients(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(SanaSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Recent Clients', style: SanaTextStyles.heading3),
              TextButton(
                onPressed: () => context.go(AppRoutes.clients),
                child: Text('View All', style: SanaTextStyles.link),
              ),
            ],
          ),
          const SizedBox(height: SanaSpacing.sm),
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: 6,
              itemBuilder: (context, index) {
                final names = ['Sarah J.', 'Michael B.', 'Lisa W.', 'James K.', 'Anna S.', 'Robert M.'];
                return Padding(
                  padding: EdgeInsets.only(right: index < 5 ? SanaSpacing.md : 0),
                  child: GestureDetector(
                    onTap: () => context.push('/clients/$index'),
                    child: Column(
                      children: [
                        SanaAvatar(
                          name: names[index],
                          size: SanaAvatarSize.lg,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          names[index],
                          style: SanaTextStyles.caption.copyWith(
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: SanaTextStyles.heading3.copyWith(color: color),
          ),
          Text(label, style: SanaTextStyles.caption),
        ],
      ),
    );
  }
}

class _SessionItem extends StatelessWidget {
  final String clientName;
  final String time;
  final String service;
  final String status;

  const _SessionItem({
    required this.clientName,
    required this.time,
    required this.service,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Row(
        children: [
          SanaAvatar(name: clientName, size: SanaAvatarSize.md),
          const SizedBox(width: SanaSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  clientName,
                  style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
                ),
                Text(service, style: SanaTextStyles.caption),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                time,
                style: SanaTextStyles.bodySmall.copyWith(fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: SanaColors.primaryLightest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  status,
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: SanaColors.primaryDark,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
