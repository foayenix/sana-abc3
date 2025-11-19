import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/health_provider.dart';
import '../../../core/providers/session_provider.dart';
import '../../../core/router/app_router.dart';
import '../../../shared/widgets/health_score_widget.dart';

/// Home screen connected to real data
class HomeScreenConnected extends ConsumerStatefulWidget {
  const HomeScreenConnected({super.key});

  @override
  ConsumerState<HomeScreenConnected> createState() => _HomeScreenConnectedState();
}

class _HomeScreenConnectedState extends ConsumerState<HomeScreenConnected> {
  @override
  void initState() {
    super.initState();
    // Load data on init
    Future.microtask(() {
      ref.read(healthProvider.notifier).loadHealthData();
      ref.read(sessionsProvider.notifier).loadSessions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(currentUserProvider);
    final healthState = ref.watch(healthProvider);
    final sessions = ref.watch(upcomingSessionsProvider);

    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            await Future.wait([
              ref.read(healthProvider.notifier).refresh(),
              ref.read(sessionsProvider.notifier).refresh(),
            ]);
          },
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Greeting
                Text(
                  'Hello, ${user?.firstName ?? 'there'}',
                  style: SanaTextStyles.heading2,
                ),
                const SizedBox(height: 4),
                Text(
                  'How are you feeling today?',
                  style: SanaTextStyles.body.copyWith(
                    color: SanaColors.textSecondary,
                  ),
                ),

                const SizedBox(height: 24),

                // Health Score Card
                _buildHealthScoreCard(healthState),

                const SizedBox(height: 24),

                // Upcoming Sessions
                _buildUpcomingSessions(sessions),

                const SizedBox(height: 24),

                // Quick Actions
                Text('Quick Actions', style: SanaTextStyles.heading3),
                const SizedBox(height: 12),
                _buildQuickActions(),

                const SizedBox(height: 24),

                // Health Dimensions
                if (healthState.dimensions.isNotEmpty)
                  _buildHealthDimensions(healthState.dimensions),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHealthScoreCard(HealthState state) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: SanaColors.primaryGradient,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Text(
            'Your Health Score',
            style: SanaTextStyles.body.copyWith(color: SanaColors.white),
          ),
          const SizedBox(height: 16),
          if (state.isLoading)
            const CircularProgressIndicator(color: SanaColors.white)
          else
            HealthScoreWidget(
              score: state.currentScore?.score ?? 0,
              size: 120,
              showLabel: false,
            ),
          const SizedBox(height: 16),
          Text(
            _getScoreMessage(state.currentScore?.score ?? 0),
            style: SanaTextStyles.bodySmall.copyWith(
              color: SanaColors.white.withValues(alpha: 0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  String _getScoreMessage(int score) {
    if (score >= 80) return 'Excellent! Keep up the great work.';
    if (score >= 60) return 'Good progress! Stay consistent.';
    if (score >= 40) return 'Room for improvement. Let\'s work on it.';
    return 'Let\'s start your wellness journey.';
  }

  Widget _buildUpcomingSessions(List<SessionDto> sessions) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Upcoming Sessions', style: SanaTextStyles.heading3),
            TextButton(
              onPressed: () => context.go(AppRoutes.sessions),
              child: const Text('See All'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (sessions.isEmpty)
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: SanaColors.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: SanaColors.grey200),
            ),
            child: Column(
              children: [
                Icon(
                  Icons.calendar_today_outlined,
                  size: 48,
                  color: SanaColors.grey400,
                ),
                const SizedBox(height: 12),
                Text(
                  'No upcoming sessions',
                  style: SanaTextStyles.body.copyWith(
                    color: SanaColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => context.go(AppRoutes.search),
                  child: const Text('Book a Session'),
                ),
              ],
            ),
          )
        else
          ...sessions.take(2).map((session) => _buildSessionCard(session)),
      ],
    );
  }

  Widget _buildSessionCard(SessionDto session) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SanaColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: SanaColors.grey200),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: SanaColors.primaryLightest,
            backgroundImage: session.practitionerAvatar != null
                ? NetworkImage(session.practitionerAvatar!)
                : null,
            child: session.practitionerAvatar == null
                ? Text(
                    session.practitionerName[0],
                    style: SanaTextStyles.body.copyWith(
                      color: SanaColors.primaryDark,
                    ),
                  )
                : null,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  session.practitionerName,
                  style: SanaTextStyles.bodyBold,
                ),
                Text(
                  session.serviceName,
                  style: SanaTextStyles.bodySmall.copyWith(
                    color: SanaColors.textSecondary,
                  ),
                ),
                Text(
                  _formatDateTime(session.scheduledAt),
                  style: SanaTextStyles.bodySmall.copyWith(
                    color: SanaColors.primaryDark,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: () => context.push('/sessions/${session.id}'),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dt) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final date = DateTime(dt.year, dt.month, dt.day);

    String dateStr;
    if (date == today) {
      dateStr = 'Today';
    } else if (date == today.add(const Duration(days: 1))) {
      dateStr = 'Tomorrow';
    } else {
      dateStr = '${dt.month}/${dt.day}';
    }

    final hour = dt.hour > 12 ? dt.hour - 12 : dt.hour;
    final period = dt.hour >= 12 ? 'PM' : 'AM';
    final minute = dt.minute.toString().padLeft(2, '0');

    return '$dateStr at $hour:$minute $period';
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: _QuickActionCard(
            icon: Icons.search,
            label: 'Find\nPractitioner',
            onTap: () => context.go(AppRoutes.search),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _QuickActionCard(
            icon: Icons.edit_note,
            label: 'Health\nJournal',
            onTap: () => context.go(AppRoutes.health),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _QuickActionCard(
            icon: Icons.message_outlined,
            label: 'Messages',
            onTap: () => context.push(AppRoutes.messaging),
          ),
        ),
      ],
    );
  }

  Widget _buildHealthDimensions(Map<String, double> dimensions) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Health Dimensions', style: SanaTextStyles.heading3),
        const SizedBox(height: 12),
        ...dimensions.entries.map((entry) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _formatDimensionName(entry.key),
                    style: SanaTextStyles.body,
                  ),
                  Text(
                    '${(entry.value * 100).round()}%',
                    style: SanaTextStyles.bodyBold.copyWith(
                      color: SanaColors.primaryDark,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              LinearProgressIndicator(
                value: entry.value,
                backgroundColor: SanaColors.grey200,
                valueColor: AlwaysStoppedAnimation(
                  SanaColors.getHealthColor((entry.value * 100).round()),
                ),
                minHeight: 8,
                borderRadius: BorderRadius.circular(4),
              ),
            ],
          ),
        )),
      ],
    );
  }

  String _formatDimensionName(String key) {
    return key.replaceAll('_', ' ').split(' ').map((word) =>
      word[0].toUpperCase() + word.substring(1)
    ).join(' ');
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: SanaColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: SanaColors.grey200),
        ),
        child: Column(
          children: [
            Icon(icon, color: SanaColors.primaryDark, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              style: SanaTextStyles.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
