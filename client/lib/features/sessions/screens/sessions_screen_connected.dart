import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/session_provider.dart';
import '../../../core/api/services/session_service.dart';

/// Sessions screen connected to real data
class SessionsScreenConnected extends ConsumerStatefulWidget {
  const SessionsScreenConnected({super.key});

  @override
  ConsumerState<SessionsScreenConnected> createState() => _SessionsScreenConnectedState();
}

class _SessionsScreenConnectedState extends ConsumerState<SessionsScreenConnected>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    Future.microtask(() {
      ref.read(sessionsProvider.notifier).loadSessions();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sessionsProvider);
    final upcomingSessions = ref.watch(upcomingSessionsProvider);
    final pastSessions = ref.watch(pastSessionsProvider);

    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Sessions'),
        backgroundColor: SanaColors.surface,
        bottom: TabBar(
          controller: _tabController,
          labelColor: SanaColors.primaryDark,
          unselectedLabelColor: SanaColors.textSecondary,
          indicatorColor: SanaColors.primaryDark,
          tabs: [
            Tab(text: 'Upcoming (${upcomingSessions.length})'),
            Tab(text: 'Past (${pastSessions.length})'),
          ],
        ),
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () => ref.read(sessionsProvider.notifier).refresh(),
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Upcoming sessions
                  _buildSessionsList(upcomingSessions, isUpcoming: true),

                  // Past sessions
                  _buildSessionsList(pastSessions, isUpcoming: false),
                ],
              ),
            ),
    );
  }

  Widget _buildSessionsList(List<SessionDto> sessions, {required bool isUpcoming}) {
    if (sessions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isUpcoming ? Icons.calendar_today_outlined : Icons.history,
              size: 48,
              color: SanaColors.grey400,
            ),
            const SizedBox(height: 12),
            Text(
              isUpcoming ? 'No upcoming sessions' : 'No past sessions',
              style: SanaTextStyles.body.copyWith(
                color: SanaColors.textSecondary,
              ),
            ),
            if (isUpcoming) ...[
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => context.go('/search'),
                child: const Text('Book a Session'),
              ),
            ],
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(20),
      itemCount: sessions.length,
      itemBuilder: (context, index) {
        final session = sessions[index];
        return _SessionCard(
          session: session,
          isUpcoming: isUpcoming,
          onCancel: isUpcoming ? () => _cancelSession(session.id) : null,
        );
      },
    );
  }

  Future<void> _cancelSession(int sessionId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Session'),
        content: const Text('Are you sure you want to cancel this session?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('No'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Yes, Cancel'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await ref.read(sessionsProvider.notifier).cancelSession(sessionId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Session cancelled')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to cancel: $e')),
          );
        }
      }
    }
  }
}

class _SessionCard extends StatelessWidget {
  final SessionDto session;
  final bool isUpcoming;
  final VoidCallback? onCancel;

  const _SessionCard({
    required this.session,
    required this.isUpcoming,
    this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => context.push('/sessions/${session.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
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
                      ],
                    ),
                  ),
                  _StatusChip(status: session.status),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.calendar_today,
                    size: 16,
                    color: SanaColors.textSecondary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _formatDate(session.scheduledAt),
                    style: SanaTextStyles.body,
                  ),
                  const SizedBox(width: 16),
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: SanaColors.textSecondary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _formatTime(session.scheduledAt),
                    style: SanaTextStyles.body,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(
                    Icons.timer,
                    size: 16,
                    color: SanaColors.textSecondary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${session.durationMinutes} min',
                    style: SanaTextStyles.body,
                  ),
                  const Spacer(),
                  Text(
                    '\$${session.price.toStringAsFixed(0)}',
                    style: SanaTextStyles.bodyBold.copyWith(
                      color: SanaColors.primaryDark,
                    ),
                  ),
                ],
              ),
              if (isUpcoming && session.canCancel) ...[
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: onCancel,
                      child: Text(
                        'Cancel',
                        style: TextStyle(color: SanaColors.error),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${months[dt.month - 1]} ${dt.day}, ${dt.year}';
  }

  String _formatTime(DateTime dt) {
    final hour = dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour);
    final period = dt.hour >= 12 ? 'PM' : 'AM';
    final minute = dt.minute.toString().padLeft(2, '0');
    return '$hour:$minute $period';
  }
}

class _StatusChip extends StatelessWidget {
  final String status;

  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    Color bgColor;

    switch (status) {
      case 'scheduled':
        color = SanaColors.info;
        bgColor = SanaColors.infoLight;
        break;
      case 'completed':
        color = SanaColors.success;
        bgColor = SanaColors.successLight;
        break;
      case 'cancelled':
        color = SanaColors.error;
        bgColor = SanaColors.errorLight;
        break;
      default:
        color = SanaColors.grey600;
        bgColor = SanaColors.grey100;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status[0].toUpperCase() + status.substring(1),
        style: SanaTextStyles.caption.copyWith(color: color),
      ),
    );
  }
}
