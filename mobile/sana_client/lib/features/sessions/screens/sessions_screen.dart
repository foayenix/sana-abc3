import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';

class SessionsScreen extends StatefulWidget {
  const SessionsScreen({super.key});

  @override
  State<SessionsScreen> createState() => _SessionsScreenState();
}

class _SessionsScreenState extends State<SessionsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Text(
                'My Sessions',
                style: SanaTextStyles.heading2,
              ),
            ),

            // Tab bar
            Container(
              margin: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
              decoration: BoxDecoration(
                color: SanaColors.grey100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: TabBar(
                controller: _tabController,
                indicator: BoxDecoration(
                  color: SanaColors.surface,
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: [
                    BoxShadow(
                      color: SanaColors.black.withOpacity(0.05),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                indicatorSize: TabBarIndicatorSize.tab,
                indicatorPadding: const EdgeInsets.all(4),
                labelColor: SanaColors.primaryDark,
                unselectedLabelColor: SanaColors.textSecondary,
                labelStyle: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
                unselectedLabelStyle: SanaTextStyles.body,
                dividerColor: Colors.transparent,
                tabs: const [
                  Tab(text: 'Upcoming'),
                  Tab(text: 'Past'),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.md),

            // Tab content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _UpcomingSessionsList(),
                  _PastSessionsList(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UpcomingSessionsList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
      itemCount: 3,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: SanaSpacing.md),
          child: _SessionCard(
            practitionerName: ['Dr. Emily Chen', 'Dr. Michael Park', 'Dr. Sarah Lee'][index],
            sessionType: ['Acupuncture Session', 'Massage Therapy', 'Naturopathy Consultation'][index],
            date: ['Nov 24, 2024', 'Nov 28, 2024', 'Dec 2, 2024'][index],
            time: ['2:00 PM', '10:30 AM', '3:00 PM'][index],
            duration: ['60 min', '90 min', '45 min'][index],
            status: index == 0 ? 'Confirmed' : 'Pending',
            isUpcoming: true,
            onTap: () => context.push('/sessions/$index'),
          ),
        );
      },
    );
  }
}

class _PastSessionsList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
      itemCount: 8,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: SanaSpacing.md),
          child: _SessionCard(
            practitionerName: ['Dr. Michael Park', 'Dr. Emily Chen', 'Dr. James Wilson', 'Dr. Lisa Wang', 'Dr. Emily Chen', 'Dr. Sarah Lee', 'Dr. Michael Park', 'Dr. Emily Chen'][index],
            sessionType: ['Massage Therapy', 'Acupuncture Session', 'Chiropractic', 'Herbalist Consultation', 'Acupuncture Session', 'Naturopathy', 'Massage Therapy', 'Acupuncture Session'][index],
            date: ['Nov 18, 2024', 'Nov 10, 2024', 'Nov 5, 2024', 'Oct 28, 2024', 'Oct 20, 2024', 'Oct 15, 2024', 'Oct 8, 2024', 'Oct 1, 2024'][index],
            time: ['11:00 AM', '2:00 PM', '4:30 PM', '10:00 AM', '2:00 PM', '1:00 PM', '11:00 AM', '3:00 PM'][index],
            duration: ['90 min', '60 min', '45 min', '30 min', '60 min', '45 min', '90 min', '60 min'][index],
            status: 'Completed',
            isUpcoming: false,
            hasReview: index > 2,
            onTap: () => context.push('/sessions/$index'),
          ),
        );
      },
    );
  }
}

class _SessionCard extends StatelessWidget {
  final String practitionerName;
  final String sessionType;
  final String date;
  final String time;
  final String duration;
  final String status;
  final bool isUpcoming;
  final bool hasReview;
  final VoidCallback onTap;

  const _SessionCard({
    required this.practitionerName,
    required this.sessionType,
    required this.date,
    required this.time,
    required this.duration,
    required this.status,
    required this.isUpcoming,
    this.hasReview = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      onTap: onTap,
      child: Column(
        children: [
          Row(
            children: [
              SanaAvatar(
                name: practitionerName,
                size: SanaAvatarSize.md,
              ),
              const SizedBox(width: SanaSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      sessionType,
                      style: SanaTextStyles.body.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      practitionerName,
                      style: SanaTextStyles.bodySmall,
                    ),
                  ],
                ),
              ),
              _StatusBadge(status: status),
            ],
          ),
          const SizedBox(height: SanaSpacing.md),
          Container(
            padding: const EdgeInsets.all(SanaSpacing.sm),
            decoration: BoxDecoration(
              color: SanaColors.grey50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                _InfoChip(
                  icon: Icons.calendar_today,
                  label: date,
                ),
                const SizedBox(width: SanaSpacing.md),
                _InfoChip(
                  icon: Icons.access_time,
                  label: time,
                ),
                const SizedBox(width: SanaSpacing.md),
                _InfoChip(
                  icon: Icons.timer_outlined,
                  label: duration,
                ),
              ],
            ),
          ),
          if (isUpcoming) ...[
            const SizedBox(height: SanaSpacing.md),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {},
                    style: OutlinedButton.styleFrom(
                      foregroundColor: SanaColors.textSecondary,
                      side: const BorderSide(color: SanaColors.grey300),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text('Reschedule'),
                  ),
                ),
                const SizedBox(width: SanaSpacing.sm),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: SanaColors.primaryDark,
                      foregroundColor: SanaColors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text('Join'),
                  ),
                ),
              ],
            ),
          ],
          if (!isUpcoming && !hasReview) ...[
            const SizedBox(height: SanaSpacing.md),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.star_outline, size: 18),
                label: const Text('Leave Review'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: SanaColors.primaryDark,
                  side: const BorderSide(color: SanaColors.primaryDark),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;

  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    Color backgroundColor;
    Color textColor;

    switch (status) {
      case 'Confirmed':
        backgroundColor = SanaColors.successLight;
        textColor = SanaColors.success;
        break;
      case 'Pending':
        backgroundColor = SanaColors.warningLight;
        textColor = SanaColors.warning;
        break;
      case 'Completed':
        backgroundColor = SanaColors.grey100;
        textColor = SanaColors.textSecondary;
        break;
      default:
        backgroundColor = SanaColors.grey100;
        textColor = SanaColors.textSecondary;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        status,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: textColor,
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({
    required this.icon,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          size: 14,
          color: SanaColors.textTertiary,
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: SanaTextStyles.caption.copyWith(
            color: SanaColors.textPrimary,
          ),
        ),
      ],
    );
  }
}
