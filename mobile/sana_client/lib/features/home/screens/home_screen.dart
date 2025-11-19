import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/health_score_widget.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(context),

              // Health Score Card
              _buildHealthScoreCard(context),

              // Quick Actions
              _buildQuickActions(context),

              // Upcoming Session
              _buildUpcomingSession(context),

              // Recommended Practitioners
              _buildRecommendedPractitioners(context),

              // Recent Activity
              _buildRecentActivity(context),

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
                Text(
                  'Sarah',
                  style: SanaTextStyles.heading2,
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () {
              // TODO: Notifications
            },
            icon: Stack(
              children: [
                const Icon(
                  Icons.notifications_outlined,
                  color: SanaColors.textPrimary,
                  size: 28,
                ),
                Positioned(
                  right: 0,
                  top: 0,
                  child: Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: SanaColors.error,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: SanaColors.background,
                        width: 2,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: () => context.push(AppRoutes.profile),
            child: const SanaAvatar(
              name: 'Sarah Johnson',
              size: SanaAvatarSize.md,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthScoreCard(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
      child: SanaGradientCard(
        child: Row(
          children: [
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Your Health Score',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: SanaColors.white,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Great progress this week! Your sleep score improved by 12%.',
                    style: TextStyle(
                      fontSize: 12,
                      color: SanaColors.white,
                      height: 1.5,
                    ),
                  ),
                  SizedBox(height: 12),
                  Text(
                    'View Insights →',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: SanaColors.accent,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: SanaSpacing.md),
            Container(
              decoration: BoxDecoration(
                color: SanaColors.white.withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              padding: const EdgeInsets.all(8),
              child: const HealthScoreWidget(
                score: 78,
                size: 100,
                showLabel: false,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(SanaSpacing.lg),
      child: Row(
        children: [
          _QuickAction(
            icon: Icons.search,
            label: 'Find Care',
            onTap: () => context.go(AppRoutes.search),
          ),
          const SizedBox(width: SanaSpacing.md),
          _QuickAction(
            icon: Icons.edit_note,
            label: 'Journal',
            onTap: () => context.push(AppRoutes.journal),
          ),
          const SizedBox(width: SanaSpacing.md),
          _QuickAction(
            icon: Icons.watch,
            label: 'Wearables',
            onTap: () {
              // TODO: Wearables settings
            },
          ),
          const SizedBox(width: SanaSpacing.md),
          _QuickAction(
            icon: Icons.history,
            label: 'History',
            onTap: () {
              // TODO: History
            },
          ),
        ],
      ),
    );
  }

  Widget _buildUpcomingSession(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Upcoming Session',
                style: SanaTextStyles.heading3,
              ),
              TextButton(
                onPressed: () => context.go(AppRoutes.sessions),
                child: Text(
                  'View All',
                  style: SanaTextStyles.link,
                ),
              ),
            ],
          ),
          const SizedBox(height: SanaSpacing.sm),
          SanaCard(
            onTap: () => context.push('/sessions/1'),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: SanaColors.primaryLightest,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '24',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: SanaColors.primaryDark,
                        ),
                      ),
                      Text(
                        'Nov',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: SanaColors.primaryDark,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: SanaSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Acupuncture Session',
                        style: SanaTextStyles.body.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Dr. Emily Chen • 2:00 PM',
                        style: SanaTextStyles.bodySmall,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: SanaColors.successLight,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'Confirmed',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: SanaColors.success,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendedPractitioners(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: SanaSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Recommended for You',
                  style: SanaTextStyles.heading3,
                ),
                TextButton(
                  onPressed: () => context.go(AppRoutes.search),
                  child: Text(
                    'See All',
                    style: SanaTextStyles.link,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: SanaSpacing.sm),
          SizedBox(
            height: 200,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
              itemCount: 5,
              itemBuilder: (context, index) {
                return Padding(
                  padding: EdgeInsets.only(
                    right: index < 4 ? SanaSpacing.md : 0,
                  ),
                  child: _PractitionerCard(
                    name: 'Dr. ${['Emily Chen', 'Michael Park', 'Sarah Lee', 'James Wilson', 'Lisa Wang'][index]}',
                    specialty: ['Acupuncture', 'Massage Therapy', 'Naturopathy', 'Chiropractic', 'Herbalist'][index],
                    rating: [4.9, 4.8, 4.7, 4.9, 4.6][index],
                    outcomeScore: [92, 88, 85, 90, 82][index],
                    onTap: () => context.push('/practitioner/$index'),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivity(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(SanaSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent Activity',
            style: SanaTextStyles.heading3,
          ),
          const SizedBox(height: SanaSpacing.md),
          _ActivityItem(
            icon: Icons.edit_note,
            title: 'Journal Entry',
            subtitle: 'Logged mood and energy levels',
            time: '2 hours ago',
            color: SanaColors.primaryMedium,
          ),
          const SizedBox(height: SanaSpacing.sm),
          _ActivityItem(
            icon: Icons.check_circle,
            title: 'Session Completed',
            subtitle: 'Massage Therapy with Dr. Park',
            time: 'Yesterday',
            color: SanaColors.success,
          ),
          const SizedBox(height: SanaSpacing.sm),
          _ActivityItem(
            icon: Icons.sync,
            title: 'Health Data Synced',
            subtitle: 'Apple Health data updated',
            time: '2 days ago',
            color: SanaColors.info,
          ),
        ],
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Column(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: SanaColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: SanaColors.grey200),
              ),
              child: Icon(
                icon,
                color: SanaColors.primaryDark,
                size: 24,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: SanaTextStyles.caption.copyWith(
                fontWeight: FontWeight.w500,
                color: SanaColors.textPrimary,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _PractitionerCard extends StatelessWidget {
  final String name;
  final String specialty;
  final double rating;
  final int outcomeScore;
  final VoidCallback onTap;

  const _PractitionerCard({
    required this.name,
    required this.specialty,
    required this.rating,
    required this.outcomeScore,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 160,
        padding: const EdgeInsets.all(SanaSpacing.md),
        decoration: BoxDecoration(
          color: SanaColors.surface,
          borderRadius: BorderRadius.circular(SanaBorderRadius.lg),
          border: Border.all(color: SanaColors.grey200),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SanaAvatar(
              name: name,
              size: SanaAvatarSize.lg,
            ),
            const SizedBox(height: SanaSpacing.sm),
            Text(
              name,
              style: SanaTextStyles.body.copyWith(
                fontWeight: FontWeight.w600,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              specialty,
              style: SanaTextStyles.caption,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const Spacer(),
            Row(
              children: [
                const Icon(
                  Icons.star,
                  size: 14,
                  color: SanaColors.accent,
                ),
                const SizedBox(width: 4),
                Text(
                  rating.toString(),
                  style: SanaTextStyles.caption.copyWith(
                    fontWeight: FontWeight.w600,
                    color: SanaColors.textPrimary,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: SanaColors.primaryLightest,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '$outcomeScore%',
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
      ),
    );
  }
}

class _ActivityItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String time;
  final Color color;

  const _ActivityItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.time,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: color,
            size: 20,
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
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                subtitle,
                style: SanaTextStyles.caption,
              ),
            ],
          ),
        ),
        Text(
          time,
          style: SanaTextStyles.caption,
        ),
      ],
    );
  }
}
